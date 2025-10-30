#!/bin/bash
# Sistema Anti-Lag TCAdmin - ÚNICO BOT

echo "🚀 SISTEMA ANTI-LAG TCADMIN"
echo "=========================="
echo "⏰ Iniciado em: $(date)"
echo "🛡️ Proteção contra sobrecarga: ATIVA"
echo "⏰ Intervalos inteligentes: ATIVOS"
echo "📊 Monitoramento contínuo: ATIVO"
echo "=========================="
echo

# Verifica se está no diretório correto
if [ ! -f "anti_lag_bot.py" ]; then
    echo "❌ Erro: Execute este script no diretório tcadmin_bot/"
    exit 1
fi

# Verifica dependências
echo "🔍 Verificando dependências..."
python3 -c "import selenium, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependências faltando. Execute: python3 scripts/setup_production.py"
    exit 1
fi
echo "✅ Dependências OK"

# Cria diretórios necessários
mkdir -p logs backups

# Inicia o sistema
echo "🚀 Iniciando sistema..."
echo "📋 Logs serão salvos em: anti_lag_bot.log"
echo "🛑 Para parar: Ctrl+C"
echo "--------------------------------------"

python3 anti_lag_bot.py
