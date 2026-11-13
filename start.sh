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

# Clean any broken/desynced session ratchets on boot while keeping creds.json
if [ -n "$DATA_DIR" ] && [ -d "$DATA_DIR/auth_info_baileys" ]; then
    echo "🧹 Limpando sessões antigas para evitar loops de Bad MAC..."
    find "$DATA_DIR/auth_info_baileys" -name "session-*.json" -delete 2>/dev/null || true
fi

# Start WhatsApp bot supervisor if configured
if [ -d "whatsapp-service" ]; then
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
fi

# Wait for both processes
wait -n $PYTHON_PID $BOT_SUPERVISOR_PID
