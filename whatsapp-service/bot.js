import makeWASocket, {
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion,
    Browsers,
    makeCacheableSignalKeyStore,
    downloadMediaMessage
} from '@whiskeysockets/baileys';
import QRCode from 'qrcode';
import pino from 'pino';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import util from 'util';
import http from 'http';

const execPromise = util.promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const STATUS_FILE = path.join(__dirname, '..', 'public', 'whatsapp_status.json');
const AUTH_DIR = path.join(__dirname, 'auth_info_baileys');
const TRANSCRIBE_SCRIPT = path.join(__dirname, '..', 'transcribe_audio.py');

const processedIds = new Set();
let currentSock = null;

// Only the couple's finance group and explicitly named finance groups are allowed
const ALLOWED_GROUPS = new Set(['120363431136155849@g.us']);
const BLOCKED_GROUPS = new Set();

function saveStatus(statusObj) {
    try {
        fs.writeFileSync(STATUS_FILE, JSON.stringify(statusObj, null, 2), 'utf-8');
    } catch (e) {
        console.error('Error saving status:', e.message);
    }
}

saveStatus({ status: 'starting', updatedAt: new Date().toISOString() });

async function startBot() {
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`Usando WhatsApp Web v${version.join('.')} (isLatest: ${isLatest})`);

    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

    const sock = makeWASocket({
        version,
        logger: pino({ level: 'silent' }),
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(state.keys, pino({ level: 'silent' }))
        },
        browser: Browsers.macOS('Desktop'),
        syncFullHistory: false,
        printQRInTerminal: false,
        generateHighQualityLinkPreview: false,
        defaultQueryTimeoutMs: 60000,
        connectTimeoutMs: 60000
    });

    currentSock = sock;
    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            try {
                const qrDataUrl = await QRCode.toDataURL(qr, { margin: 2, scale: 8 });
                saveStatus({
                    status: 'scan_qr',
                    qrDataUrl: qrDataUrl,
                    qrRaw: qr,
                    updatedAt: new Date().toISOString()
                });
                console.log('⚡ QR Code atualizado em /whatsapp');
            } catch (err) {
                console.error('Erro ao gerar QR Code DataURL:', err.message);
            }
        }

        if (connection === 'close') {
            const statusCode = (lastDisconnect?.error)?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
            console.log(`Conexão encerrada (código: ${statusCode}). Reconectando: ${shouldReconnect}...`);

            saveStatus({
                status: 'disconnected',
                reason: statusCode,
                updatedAt: new Date().toISOString()
            });

            if (shouldReconnect) {
                setTimeout(startBot, 3000);
            } else {
                console.log('Sessão encerrada (Logout). Limpando credenciais...');
                try {
                    fs.rmSync(AUTH_DIR, { recursive: true, force: true });
                } catch (e) {}
                setTimeout(startBot, 3000);
            }
        } else if (connection === 'open') {
            console.log('\n=============================================');
            console.log('🎉 ZECA CONECTADO AO WHATSAPP COM SUCESSO!');
            console.log('Usuário conectado:', sock.user?.name || sock.user?.id);
            console.log('=============================================\n');

            saveStatus({
                status: 'connected',
                user: sock.user,
                updatedAt: new Date().toISOString()
            });
        }
    });

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;

        for (const m of messages) {
            if (!m.message) continue;

            const msgId = m.key.id;
            if (processedIds.has(msgId)) continue;
            processedIds.add(msgId);
            if (processedIds.size > 500) {
                const oldest = processedIds.values().next().value;
                processedIds.delete(oldest);
            }

            const remoteJid = m.key.remoteJid;
            if (!remoteJid || remoteJid === 'status@broadcast') continue;

            // Extract preliminary text to check for self-replies
            let text = m.message.conversation ||
                       m.message.extendedTextMessage?.text ||
                       m.message.imageMessage?.caption ||
                       '';

            // NEVER process bot's own confirmations (prevent feedback loops)
            if (text.includes('Lançado com sucesso no Organize') || text.includes('Fala Davi! Aqui é o Zeca')) {
                continue;
            }

            const isGroup = remoteJid.endsWith('@g.us');
            const ownPhone = sock.user?.id ? sock.user.id.split(':')[0] : '554791490805';
            const senderJid = isGroup ? (m.key.participant || m.participant || '') : remoteJid;
            const isSelfChat = !isGroup && (remoteJid.includes(ownPhone) || remoteJid.includes('5547991490805'));

            // AUDIO / VOICE MESSAGE PROCESSING
            if (m.message.audioMessage) {
                console.log(`🎤 Áudio recebido no chat ${remoteJid}... Baixando para transcrição`);
                const tempAudioPath = path.join(__dirname, `temp_audio_${Date.now()}.ogg`);
                try {
                    const audioBuffer = await downloadMediaMessage(m, 'buffer', {});
                    fs.writeFileSync(tempAudioPath, audioBuffer);

                    const { stdout } = await execPromise(`python3 "${TRANSCRIBE_SCRIPT}" "${tempAudioPath}"`);
                    text = stdout.trim();
                    console.log('📝 Áudio transcrito:', text);
                } catch (audioErr) {
                    console.error('Erro na transcrição:', audioErr.message);
                } finally {
                    if (fs.existsSync(tempAudioPath)) {
                        try { fs.unlinkSync(tempAudioPath); } catch (e) {}
                    }
                }
            }

            if (!text || text.trim().length === 0) continue;

            const textLower = text.toLowerCase();

            // 1. STRICT CHAT AUTHORIZATION FILTER:
            if (isGroup) {
                // Must be the couple's finance group or named with finances/zeca
                if (!ALLOWED_GROUPS.has(remoteJid)) {
                    if (BLOCKED_GROUPS.has(remoteJid)) {
                        continue;
                    }
                    try {
                        const metadata = await sock.groupMetadata(remoteJid);
                        const subject = (metadata.subject || '').toLowerCase();
                        if (subject.includes('finan') || subject.includes('organize') || subject.includes('zeca') || subject.includes('gastos')) {
                            ALLOWED_GROUPS.add(remoteJid);
                            console.log(`✅ Grupo financeiro reconhecido e autorizado: "${metadata.subject}" (${remoteJid})`);
                        } else {
                            BLOCKED_GROUPS.add(remoteJid);
                            console.log(`🚫 Grupo comum bloqueado: "${metadata.subject}" (${remoteJid})`);
                            continue;
                        }
                    } catch (e) {
                        BLOCKED_GROUPS.add(remoteJid);
                        continue;
                    }
                }
            } else if (!isSelfChat) {
                // In private chat with other people: ONLY allow if message starts with "zeca"
                const textTrim = textLower.trim();
                if (!textTrim.startsWith('zeca') && !textTrim.startsWith('zéca') && !textTrim.startsWith('zac') && !textTrim.startsWith('zeck')) {
                    continue;
                }
            }

            // 2. FINANCIAL INTENT FILTER (Must contain numbers or financial currency words):
            const hasDigit = /\d+/.test(text);
            const hasCurrencyWord = /(reais|real|r\$|pix|d[eé]bito|devido|cr[eé]dito|cart[aã]o|paguei|comprei|gastei|custou|cento|vinte|trinta|quarenta|cinquenta|dez|quinze|quatro|cinco|seis|sete|oito|nove)/i.test(text);
            if (!hasDigit && !hasCurrencyWord) {
                // Casual chat ("bom dia", "kkk", "tudo bem?") -> Ignore completely!
                continue;
            }

            console.log(`📩 [Processando Gasto] Chat: ${remoteJid} | Remetente: ${senderJid} | Mensagem: "${text}"`);

            // DETERMINE SENDER (Davi vs Nati)
            let determinedSender = 'Davi';
            const senderPush = (m.pushName || '').toLowerCase();

            if (isGroup) {
                if (m.key.fromMe) {
                    determinedSender = 'Davi';
                } else if (senderPush.includes('nat') || senderPush.includes('nati') || senderPush.includes('nathalie')) {
                    determinedSender = 'Nati';
                } else {
                    // In a couple's group, if it's not Davi, it's Nati!
                    determinedSender = 'Nati';
                }
            } else {
                if (senderPush.includes('nat') || senderPush.includes('nati') || senderPush.includes('nathalie') || remoteJid.includes('nat')) {
                    determinedSender = 'Nati';
                } else {
                    determinedSender = 'Davi';
                }
            }

            // Also check message content for explicit person hints
            if (textLower.includes('nati') || textLower.includes('minha mulher') || textLower.includes('esposa')) {
                determinedSender = 'Nati';
            } else if (textLower.includes('davi') || textLower.includes('meu')) {
                determinedSender = 'Davi';
            }

            const senderPhone = senderJid.replace('@s.whatsapp.net', '').replace('@g.us', '');

            try {
                const resp = await fetch('http://localhost:5050/api/webhook/whatsapp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: text,
                        senderName: determinedSender,
                        phone: senderPhone,
                        isGroup: isGroup
                    })
                });

                const data = await resp.json();
                if (data.reply) {
                    console.log(`🤖 Zeca respondendo no chat ${remoteJid}...`);
                    await sock.sendMessage(remoteJid, { text: data.reply }, { quoted: m });
                }
            } catch (err) {
                console.error('Erro ao chamar webhook:', err.message);
            }
        }
    });
}

// Pairing helper server
const pairServer = http.createServer(async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    if (req.url.startsWith('/send-test')) {
        if (!currentSock) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Socket não iniciado' }));
            return;
        }

        const testMsg = `👋 *Fala Davi! Aqui é o Zeca!* 🤖\n\nConexão estabelecida com sucesso! Toda vez que você ou a Nati mandarem uma mensagem de áudio, texto ou foto de comprovante aqui (ou no grupo de vocês), eu já calculo e lanço direto no Organize Aí.\n\n*Pode testar me mandando um áudio ou texto agora, por exemplo:*\n_"Zeca, almoço de 35 reais no débito"_`;

        try {
            const ownJid = currentSock.user?.id || '554791490805@s.whatsapp.net';
            const cleanJid = ownJid.split(':')[0] + '@s.whatsapp.net';
            await currentSock.sendMessage(cleanJid, { text: testMsg });
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true, sentTo: cleanJid }));
        } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        }
        return;
    }

    if (req.url.startsWith('/pair-code')) {
        const urlParams = new URL(req.url, 'http://localhost:5052');
        const phone = urlParams.searchParams.get('phone');
        if (!phone) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Telefone não informado' }));
            return;
        }

        if (currentSock && !currentSock.authState.creds.registered) {
            try {
                const cleanPhone = phone.replace(/\D/g, '');
                console.log(`Solicitando código de pareamento para ${cleanPhone}...`);
                const code = await currentSock.requestPairingCode(cleanPhone);
                console.log(`Código de pareamento gerado: ${code}`);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, code: code }));
            } catch (err) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: err.message }));
            }
        } else {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Robô já registrado ou iniciando' }));
        }
        return;
    }

    res.writeHead(404);
    res.end();
});

pairServer.listen(5052, () => {
    console.log('Servidor de pareamento auxiliar ativo na porta 5052');
});

startBot();
