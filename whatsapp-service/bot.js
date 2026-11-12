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

const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, '..');
const STATUS_FILE = path.join(__dirname, '..', 'public', 'whatsapp_status.json');
const AUTH_DIR = path.join(DATA_DIR, 'auth_info_baileys');
const TRANSCRIBE_SCRIPT = path.join(__dirname, '..', 'transcribe_audio.py');

// Ensure AUTH_DIR exists in persistent storage
if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
}

// Seed persistent AUTH_DIR from local container files if empty
const localAuthDir = path.join(__dirname, 'auth_info_baileys');
if (fs.existsSync(localAuthDir) && path.resolve(AUTH_DIR) !== path.resolve(localAuthDir)) {
    const credsFile = path.join(AUTH_DIR, 'creds.json');
    const localCreds = path.join(localAuthDir, 'creds.json');
    if (!fs.existsSync(credsFile) && fs.existsSync(localCreds)) {
        try {
            console.log('📦 Migrando credenciais do WhatsApp para o volume persistente...');
            const files = fs.readdirSync(localAuthDir);
            for (const f of files) {
                fs.copyFileSync(path.join(localAuthDir, f), path.join(AUTH_DIR, f));
            }
        } catch (copyErr) {
            console.error('Erro ao migrar credenciais:', copyErr.message);
        }
    }
}

const processedIds = new Set();
let currentSock = null;

const ALLOWED_GROUPS_FILE = path.join(DATA_DIR, 'allowed_groups.json');
const allowedGroups = new Set(['120363431136155849@g.us']);
const groupSubjectsCache = new Map();

try {
    if (fs.existsSync(ALLOWED_GROUPS_FILE)) {
        const raw = JSON.parse(fs.readFileSync(ALLOWED_GROUPS_FILE, 'utf-8'));
        if (Array.isArray(raw)) {
            raw.forEach(id => allowedGroups.add(id));
        }
    }
} catch (e) {
    console.error('Erro ao ler allowed_groups.json:', e.message);
}

function saveAllowedGroups() {
    try {
        fs.writeFileSync(ALLOWED_GROUPS_FILE, JSON.stringify([...allowedGroups], null, 2), 'utf-8');
    } catch (e) {
        console.error('Erro ao salvar allowed_groups.json:', e.message);
    }
}

const FINANCE_KEYWORDS = [
    'finan', 'organize', 'organiza', 'zeca', 'gasto', 'despesa',
    'conta', 'casa', 'casal', 'famili', 'famíli', 'orcamento',
    'orçamento', 'custo', 'cartao', 'cartão', 'economia', 'compras'
];

async function isGroupAuthorized(sock, remoteJid) {
    let subject = groupSubjectsCache.get(remoteJid);
    if (!subject) {
        try {
            const metadata = await sock.groupMetadata(remoteJid);
            subject = (metadata?.subject || '').toLowerCase();
            groupSubjectsCache.set(remoteJid, subject);
        } catch (e) {
            return false;
        }
    }
    // EXCLUSIVE: ONLY allow group with name "Organize aí" / "Organize ai"
    if (subject && (subject.includes('organize a') || subject.includes('organize aí') || subject.includes('organize ai'))) {
        return true;
    }
    return false;
}

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

            const isGroup = remoteJid.endsWith('@g.us');
            const ownPhone = sock.user?.id ? sock.user.id.split(':')[0] : '554791490805';
            const cleanOwnPhone = ownPhone.replace(/\D/g, '');
            const senderJid = isGroup ? (m.key.participant || m.participant || '') : remoteJid;
            const isSelfChat = !isGroup && (remoteJid.includes(ownPhone) || remoteJid.includes('5547991490805'));

            // Check if group is authorized
            let isAuthGroup = isGroup ? await isGroupAuthorized(sock, remoteJid) : false;

            // Check if quoting bot
            const quotedParticipant = m.message.extendedTextMessage?.contextInfo?.participant || '';
            const isQuotingBot = quotedParticipant.includes(cleanOwnPhone);

            // Check if bot was tagged/mentioned in mentions array
            const mentionedJids = m.message.extendedTextMessage?.contextInfo?.mentionedJid || [];
            const isBotMentioned = mentionedJids.some(jid => jid.includes(cleanOwnPhone));

            // Extract preliminary text / caption
            let text = m.message.conversation ||
                       m.message.extendedTextMessage?.text ||
                       m.message.imageMessage?.caption ||
                       m.message.videoMessage?.caption ||
                       m.message.documentMessage?.caption ||
                       '';

            // Check if user called Zeca in text/caption
            const initialLower = text.toLowerCase();
            let isZecaCall = initialLower.includes('zeca') || 
                             initialLower.includes('zéca') || 
                             initialLower.includes('zeck') || 
                             initialLower.includes('zac') || 
                             isBotMentioned || 
                             isQuotingBot;

            // AUDIO / VOICE MESSAGE PROCESSING:
            // Download & transcribe IF: private chat OR authorized group OR quoting bot OR calling Zeca
            if (m.message.audioMessage) {
                if (!isGroup || isAuthGroup || isQuotingBot || isZecaCall) {
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
                } else {
                    // Audio from un-authorized general group (church, sports, etc) -> skip to save CPU
                    continue;
                }
            }

            if (!text || text.trim().length === 0) continue;

            // NEVER process bot's own confirmations (prevent feedback loops)
            if (text.includes('Lançado com sucesso no Organize') || text.includes('Fala aí! Aqui é o Zeca')) {
                continue;
            }

            const textLower = text.toLowerCase();
            if (!isZecaCall) {
                isZecaCall = textLower.includes('zeca') || 
                             textLower.includes('zéca') || 
                             textLower.includes('zeck') || 
                             textLower.includes('zac');
            }

            // Command: "Zeca ativar grupo"
            if (isGroup && (textLower.includes('ativar grupo') || textLower.includes('ativa grupo') || textLower.includes('ativa esse grupo'))) {
                allowedGroups.add(remoteJid);
                saveAllowedGroups();
                isAuthGroup = true;
                console.log(`✅ Grupo ativado manualmente por comando: ${remoteJid}`);
            }

            // STRICT CHAT AUTHORIZATION:
            if (isGroup) {
                // EXCLUSIVELY allow the "Organize aí" group! No other group is allowed!
                if (!isAuthGroup) {
                    continue;
                }
            } else if (!isSelfChat) {
                // In private chat with other people: ONLY process if message calls Zeca
                if (!isZecaCall) {
                    continue;
                }
            }

            // FINANCIAL INTENT OR ZECA CALL:
            const hasDigit = /\d+/.test(text);
            const hasCurrencyWord = /(reais|real|r\$|pix|d[eé]bito|devido|cr[eé]dito|cart[aã]o|paguei|comprei|gastei|custou|cento|vinte|trinta|quarenta|cinquenta|dez|quinze|quatro|cinco|seis|sete|oito|nove)/i.test(text);

            // If user did not call Zeca explicitly, require financial intent (numbers/currency)
            if (!isZecaCall && !hasDigit && !hasCurrencyWord) {
                // Casual chat in finance group ("bom dia", "tudo bem?") -> ignore
                continue;
            }

            console.log(`📩 [Processando Gasto] Chat: ${remoteJid} | Remetente: ${senderJid} | ZecaCall: ${isZecaCall} | Mensagem: "${text}"`);

            // DETERMINE SENDER (Davi vs Nathalie)
            let determinedSender = 'Davi';
            const senderPush = (m.pushName || '').toLowerCase();

            if (isGroup) {
                if (m.key.fromMe || senderPush.includes('davi') || senderPush.includes('cruz') || senderPush.includes('costa')) {
                    determinedSender = 'Davi';
                } else if (senderPush.includes('nat') || senderPush.includes('nati') || senderPush.includes('nathalie') || senderPush.includes('pezzarico') || senderPush.includes('pezarico')) {
                    determinedSender = 'Nathalie';
                } else if (m.pushName) {
                    determinedSender = m.pushName;
                } else {
                    determinedSender = 'Davi';
                }
            } else {
                if (senderPush.includes('nat') || senderPush.includes('nati') || senderPush.includes('nathalie') || remoteJid.includes('nat')) {
                    determinedSender = 'Nathalie';
                } else {
                    determinedSender = 'Davi';
                }
            }

            // Also check message content for explicit person hints
            if (textLower.includes('nati') || textLower.includes('nathalie') || textLower.includes('minha mulher') || textLower.includes('esposa')) {
                determinedSender = 'Nathalie';
            } else if (textLower.includes('davi') || textLower.includes('meu')) {
                determinedSender = 'Davi';
            }

            const senderPhone = senderJid.replace('@s.whatsapp.net', '').replace('@g.us', '');

            // Endpoints list: Direct Railway first (immune to FortiGuard SSL interception), then custom domain, then local
            const endpoints = [
                'https://organize-ai-production-6b46.up.railway.app/api/webhook/whatsapp',
                'https://apporganizeai.com.br/api/webhook/whatsapp',
                'http://localhost:5050/api/webhook/whatsapp'
            ];

            const payload = {
                text: text,
                senderName: determinedSender,
                phone: senderPhone,
                isGroup: isGroup,
                isZecaCall: isZecaCall
            };

            try {
                let resp = null;
                for (const url of endpoints) {
                    try {
                        const r = await fetch(url, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        const ct = r.headers.get('content-type') || '';
                        if (r.ok && ct.includes('application/json')) {
                            resp = r;
                            break;
                        }
                    } catch (e) {
                        // Try next endpoint
                    }
                }

                if (!resp) {
                    console.log('⚠️ Nenhum endpoint de webhook respondeu com JSON.');
                    continue;
                }

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
