#!/bin/bash
set -e

echo "🚀 Iniciando Organize Aí..."

# Configuração de persistência para o WhatsApp e dados
if [ -n "$DATA_DIR" ] && [ -d "$DATA_DIR" ]; then
    echo "💾 Configurando persistência em $DATA_DIR..."
    mkdir -p "$DATA_DIR/auth_info_baileys"
    if [ -d "/app/whatsapp-service/auth_info_baileys" ] && [ -f "/app/whatsapp-service/auth_info_baileys/creds.json" ]; then
        if [ ! -f "$DATA_DIR/auth_info_baileys/creds.json" ]; then
            echo "📦 Migrando credenciais do WhatsApp para o volume persistente..."
            cp -r /app/whatsapp-service/auth_info_baileys/* "$DATA_DIR/auth_info_baileys/" 2>/dev/null || true
        fi
    fi
fi

# Start python server in background
python3 server.py &
PYTHON_PID=$!

# Wait 2 seconds for server to bind
sleep 2

# Start WhatsApp bot supervisor only if explicitly enabled
if [ "$ENABLE_WHATSAPP_BOT" = "true" ] && [ -d "whatsapp-service" ]; then
    echo "🤖 Iniciando supervisor resiliente do WhatsApp..."
    (
        cd whatsapp-service
        while true; do
            echo "🤖 [Supervisor] Iniciando bot.js..."
            node bot.js || true
            echo "⚠️ [Supervisor] bot.js parou. Reiniciando em 3 segundos..."
            sleep 3
        done
    ) &
    BOT_SUPERVISOR_PID=$!
else
    echo "⏸️ Robô do WhatsApp desativado."
    if [ -f "public/whatsapp_status.json" ]; then
        echo '{"status": "disabled", "message": "Robô desativado", "updatedAt": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}' > public/whatsapp_status.json
    fi
fi

# Wait for processes
if [ -n "$BOT_SUPERVISOR_PID" ]; then
    wait -n $PYTHON_PID $BOT_SUPERVISOR_PID
else
    wait $PYTHON_PID
fi
