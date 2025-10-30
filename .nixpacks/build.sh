#!/bin/bash
# Script de build para garantir instalação do Chromium

echo "🔧 Instalando Chromium e dependências..."

# Tenta instalar via apt se disponível
if command -v apt-get &> /dev/null; then
    apt-get update -qq
    apt-get install -y -qq chromium-browser chromium-driver \
        libnss3 libxss1 libasound2 fonts-liberation \
        libatk-bridge2.0-0 libgtk-3-0 libdrm2 libgbm1 libxshmfence1 || true
fi

# Verifica instalação
if [ -f /usr/bin/chromium ]; then
    echo "✅ Chromium instalado em /usr/bin/chromium"
elif [ -f /usr/bin/chromium-browser ]; then
    echo "✅ Chromium instalado em /usr/bin/chromium-browser"
else
    echo "⚠️ Chromium não encontrado após tentativa de instalação"
fi

echo "✅ Build concluído"

