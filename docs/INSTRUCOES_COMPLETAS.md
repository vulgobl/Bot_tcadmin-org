# 🚀 INSTRUÇÕES COMPLETAS - Sistema Anti-Lag TCAdmin

## 📋 **ÍNDICE**
1. [Configuração Inicial](#configuração-inicial)
2. [Execução do Sistema](#execução-do-sistema)
3. [Monitoramento](#monitoramento)
4. [Troubleshooting](#troubleshooting)
5. [Manutenção](#manutenção)
6. [Comandos Úteis](#comandos-úteis)

---

## 🔧 **CONFIGURAÇÃO INICIAL**

### **1. Verificar Dependências**
```bash
cd /home/codexbl/test/cloudbase-hosting-site/tcadmin_bot
python3 setup_production.py
```

### **2. Configurar Variáveis de Ambiente**
Crie/edite o arquivo `variables.env`:
```env
SUPABASE_URL=https://gxvcovuwtbpkvzqdbcbr.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd4dmNvdnV3dGJwa3Z6cWRiY2JyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODIwNTQzOCwiZXhwIjoyMDYzNzgxNDM4fQ.8f838023-ab78-4468-ad2b-b830894fb156
TCADMIN_URL=https://tcadmin.xyz/
TCADMIN_USERNAME=bernardol
TCADMIN_PASSWORD=Xyr+(191oTPZ7i
```

### **3. Verificar Permissões**
```bash
chmod +x run.sh
chmod +x monitor.py
```

---

## 🚀 **EXECUÇÃO DO SISTEMA**

### **Método 1: Script Automático (Recomendado)**
```bash
cd /home/codexbl/test/cloudbase-hosting-site/tcadmin_bot
./run.sh
```

### **Método 2: Execução Manual**
```bash
cd /home/codexbl/test/cloudbase-hosting-site/tcadmin_bot
python3 start_production.py
```

### **Método 3: Execução em Background**
```bash
cd /home/codexbl/test/cloudbase-hosting-site/tcadmin_bot
nohup python3 start_production.py > bot_output.log 2>&1 &
```

---

## 📊 **MONITORAMENTO**

### **1. Monitor de Status**
```bash
python3 monitor.py
```

### **2. Monitor Contínuo**
```bash
python3 monitor.py --continuous
```

### **3. Ver Logs em Tempo Real**
```bash
tail -f anti_lag_bot.log
```

### **4. Ver Logs com Filtros**
```bash
# Apenas erros
grep "ERROR" anti_lag_bot.log

# Apenas sucessos
grep "✅" anti_lag_bot.log

# Apenas pedidos processados
grep "Pedido.*processado" anti_lag_bot.log
```

### **5. Verificar Status do Sistema**
```bash
# Verificar se o processo está rodando
ps aux | grep anti_lag_bot

# Verificar uso de memória
ps aux | grep anti_lag_bot | awk '{print $4, $6}'

# Verificar logs recentes
tail -20 anti_lag_bot.log
```

---

## 🔍 **TROUBLESHOOTING**

### **Problema 1: Sistema não inicia**
```bash
# Verificar dependências
python3 -c "import selenium, requests, dotenv"

# Verificar ChromeDriver
python3 -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.quit()"

# Verificar variáveis de ambiente
python3 -c "import os; print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))"
```

### **Problema 2: Erro de login TCAdmin**
```bash
# Testar login manual
python3 test_login.py

# Verificar credenciais
cat variables.env | grep TCADMIN
```

### **Problema 3: Sistema sobrecarregado**
```bash
# Verificar logs de sobrecarga
grep "OVERLOAD" anti_lag_bot.log

# Verificar requisições
grep "requisições" anti_lag_bot.log | tail -10
```

### **Problema 4: Chrome não abre**
```bash
# Verificar se está em modo headless
grep "headless" anti_lag_bot.py

# Verificar permissões
ls -la /usr/bin/chromedriver
```

---

## 🛠️ **MANUTENÇÃO**

### **1. Limpeza de Logs**
```bash
# Backup dos logs antigos
cp anti_lag_bot.log backups/anti_lag_bot_$(date +%Y%m%d).log

# Limpar logs atuais
> anti_lag_bot.log
```

### **2. Atualização do Sistema**
```bash
# Backup da configuração
cp variables.env backups/variables_$(date +%Y%m%d).env

# Atualizar dependências
pip3 install --upgrade selenium requests python-dotenv
```

### **3. Reinicialização**
```bash
# Parar sistema
pkill -f anti_lag_bot

# Limpar logs
> anti_lag_bot.log

# Reiniciar
./run.sh
```

---

## 📋 **COMANDOS ÚTEIS**

### **Inicialização**
```bash
# Iniciar sistema
./run.sh

# Iniciar em background
nohup ./run.sh > bot_output.log 2>&1 &

# Iniciar com monitor
./run.sh & python3 monitor.py
```

### **Monitoramento**
```bash
# Status rápido
python3 monitor.py

# Monitor contínuo
python3 monitor.py --continuous

# Logs em tempo real
tail -f anti_lag_bot.log

# Verificar processos
ps aux | grep anti_lag_bot
```

### **Controle**
```bash
# Parar sistema
pkill -f anti_lag_bot

# Reiniciar sistema
pkill -f anti_lag_bot && sleep 5 && ./run.sh

# Verificar status
ps aux | grep anti_lag_bot
```

### **Logs e Debug**
```bash
# Ver logs recentes
tail -50 anti_lag_bot.log

# Filtrar por tipo
grep "ERROR" anti_lag_bot.log
grep "✅" anti_lag_bot.log
grep "⚠️" anti_lag_bot.log

# Contar eventos
grep -c "Pedido.*processado" anti_lag_bot.log
grep -c "ERROR" anti_lag_bot.log
```

---

## 📊 **ESTADOS DO SISTEMA**

### **🟢 IDLE (Parado)**
- **Quando**: Nenhum pedido por 3+ verificações
- **Intervalo**: 10min (fora) / 5min (comercial)
- **Ação**: Aguarda próximo pedido

### **🟡 ACTIVE (Ativo)**
- **Quando**: Acabou de processar pedidos
- **Intervalo**: 5min (fora) / 1min (comercial)
- **Ação**: Verifica se há novos pedidos

### **🔴 BUSY (Ocupado)**
- **Quando**: Processando pedidos
- **Intervalo**: 1min (fora) / 30s (comercial)
- **Ação**: Processa pedidos ativos

### **⚠️ OVERLOAD (Sobrecarregado)**
- **Quando**: 100+ requisições/hora
- **Intervalo**: Pausa 1 hora
- **Ação**: Proteção automática

---

## 🎯 **INDICADORES DE SUCESSO**

### **✅ Sistema Funcionando**
- Logs mostram "Sistema inicializado"
- Monitor mostra status "Verde"
- Processo ativo no sistema

### **✅ Processamento Normal**
- Logs mostram "Pedidos encontrados"
- Logs mostram "Pedido processado"
- Status muda entre IDLE/ACTIVE/BUSY

### **✅ Proteção Ativa**
- Logs mostram "Proteção contra sobrecarga"
- Sistema pausa automaticamente
- Logs mostram "Sistema pausado"

---

## 🚨 **ALERTAS IMPORTANTES**

### **⚠️ Sistema Sobrecarregado**
```
⚠️ LIMITE DE REQUISIÇÕES ATINGIDO!
🛑 Sistema entrando em modo OVERLOAD...
⏰ Pausando por 1 hora para proteção
```

### **❌ Erro Crítico**
```
❌ ERRO CRÍTICO no bot principal
❌ Falha ao processar pedido
❌ Sistema com problemas
```

### **✅ Sistema Recuperado**
```
🔄 Sistema resetado do modo OVERLOAD
✅ Sistema funcionando normalmente
🎯 Pedidos sendo processados
```

---

## 📞 **SUPORTE**

### **Logs Importantes**
- `anti_lag_bot.log` - Log principal
- `bot_output.log` - Output do sistema
- `monitor.log` - Logs do monitor

### **Comandos de Diagnóstico**
```bash
# Status completo
python3 monitor.py --full

# Verificar configuração
python3 -c "from anti_lag_config import AntiLagConfig; print(AntiLagConfig())"

# Testar conexões
python3 test_login.py
```

### **Contatos**
- **Logs**: `anti_lag_bot.log`
- **Monitor**: `python3 monitor.py`
- **Status**: `ps aux | grep anti_lag_bot`

---

**🎯 Sistema configurado e pronto para produção!** 🚀
