# 🚀 COMANDOS RÁPIDOS - Sistema Anti-Lag TCAdmin

## 🎯 **COMANDOS ESSENCIAIS**

### **🚀 Iniciar Sistema**
```bash
cd /home/codexbl/test/cloudbase-hosting-site/tcadmin_bot
./run.sh
```

### **📊 Monitorar Sistema**
```bash
python3 monitor.py
```

### **🔍 Diagnóstico Completo**
```bash
python3 diagnostico.py
```

### **🛑 Parar Sistema**
```bash
pkill -f anti_lag_bot
```

---

## 📋 **COMANDOS DE MONITORAMENTO**

### **Ver Status Rápido**
```bash
python3 monitor.py
```

### **Ver Logs em Tempo Real**
```bash
tail -f anti_lag_bot.log
```

### **Ver Logs Recentes**
```bash
tail -50 anti_lag_bot.log
```

### **Ver Apenas Erros**
```bash
grep "ERROR" anti_lag_bot.log
```

### **Ver Apenas Sucessos**
```bash
grep "✅" anti_lag_bot.log
```

### **Ver Pedidos Processados**
```bash
grep "Pedido.*processado" anti_lag_bot.log
```

---

## 🔧 **COMANDOS DE CONTROLE**

### **Iniciar em Background**
```bash
nohup ./run.sh > bot_output.log 2>&1 &
```

### **Reiniciar Sistema**
```bash
pkill -f anti_lag_bot && sleep 5 && ./run.sh
```

### **Verificar Processo**
```bash
ps aux | grep anti_lag_bot
```

### **Verificar Uso de Memória**
```bash
ps aux | grep anti_lag_bot | awk '{print $4, $6}'
```

---

## 🛠️ **COMANDOS DE MANUTENÇÃO**

### **Backup de Logs**
```bash
cp anti_lag_bot.log backups/anti_lag_bot_$(date +%Y%m%d).log
```

### **Limpar Logs**
```bash
> anti_lag_bot.log
```

### **Verificar Dependências**
```bash
python3 setup_production.py
```

### **Testar Login TCAdmin**
```bash
python3 test_login.py
```

---

## 📊 **COMANDOS DE ANÁLISE**

### **Contar Pedidos Processados**
```bash
grep -c "Pedido.*processado" anti_lag_bot.log
```

### **Contar Erros**
```bash
grep -c "ERROR" anti_lag_bot.log
```

### **Ver Últimas 10 Linhas**
```bash
tail -10 anti_lag_bot.log
```

### **Ver Logs de Hoje**
```bash
grep "$(date +%Y-%m-%d)" anti_lag_bot.log
```

---

## 🚨 **COMANDOS DE EMERGÊNCIA**

### **Parar Tudo**
```bash
pkill -f anti_lag_bot
pkill -f chrome
```

### **Limpar Tudo e Reiniciar**
```bash
pkill -f anti_lag_bot
> anti_lag_bot.log
./run.sh
```

### **Verificar Recursos do Sistema**
```bash
free -h
df -h
top
```

### **Verificar Conexões de Rede**
```bash
netstat -tulpn | grep python
```

---

## 📁 **ESTRUTURA DE ARQUIVOS**

```
tcadmin_bot/
├── anti_lag_bot.py          # Sistema principal
├── start_production.py      # Script de inicialização
├── monitor.py              # Monitor de status
├── diagnostico.py          # Diagnóstico completo
├── run.sh                  # Script de execução
├── variables.env           # Configurações
├── anti_lag_bot.log        # Log principal
└── backups/               # Backups de logs
```

---

## 🎯 **FLUXO DE TRABALHO TÍPICO**

### **1. Iniciar Sistema**
```bash
./run.sh
```

### **2. Monitorar (em outro terminal)**
```bash
python3 monitor.py
```

### **3. Ver Logs (em outro terminal)**
```bash
tail -f anti_lag_bot.log
```

### **4. Parar quando necessário**
```bash
Ctrl + C
```

---

## 📞 **COMANDOS DE SUPORTE**

### **Diagnóstico Completo**
```bash
python3 diagnostico.py
```

### **Verificar Configuração**
```bash
cat variables.env
```

### **Testar Conexões**
```bash
python3 test_login.py
```

### **Verificar Status**
```bash
python3 monitor.py --full
```

---

**🎯 Sistema pronto para produção!** 🚀
