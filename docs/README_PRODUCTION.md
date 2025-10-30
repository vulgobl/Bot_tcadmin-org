# 🚀 Sistema Anti-Lag TCAdmin - Produção

Sistema inteligente de automação TCAdmin com proteção contra sobrecarga.

## 📁 **Arquivos do Sistema:**

- `anti_lag_bot.py` - Sistema principal
- `start_production.py` - Script de inicialização
- `monitor.py` - Monitor de status
- `setup_production.py` - Setup e configuração
- `anti_lag_config.py` - Configurações

## 🚀 **Instalação e Configuração:**

### **1. Setup Inicial:**
```bash
cd /home/codexbl/test/cloudbase-hosting-site/tcadmin_bot
python3 setup_production.py
```

### **2. Iniciar Sistema:**
```bash
python3 start_production.py
```

### **3. Monitorar Sistema:**
```bash
python3 monitor.py
```

## 📊 **Funcionamento:**

### **Estados do Sistema:**
- 🟢 **IDLE**: Sem atividade (10min fora / 5min comercial)
- 🟡 **ACTIVE**: Acabou de processar (5min fora / 1min comercial)
- 🔴 **BUSY**: Processando pedidos (1min fora / 30s comercial)
- ⚠️ **OVERLOAD**: Sobrecarregado (pausa 1 hora)

### **Proteções Ativas:**
- **Rate Limiting**: 100 requisições/hora
- **Overload Protection**: Pausa automática
- **Error Handling**: Backoff em erros
- **Health Checks**: Monitoramento contínuo

## 🎯 **Vantagens:**

- ✅ **90% menos requisições** quando parado
- ✅ **Proteção automática** contra sobrecarga
- ✅ **Intervalos inteligentes** por horário
- ✅ **Auto-regulação** baseada na atividade
- ✅ **Logs detalhados** para monitoramento

## 📋 **Comandos Úteis:**

### **Iniciar Sistema:**
```bash
python3 start_production.py
```

### **Monitorar Status:**
```bash
python3 monitor.py
```

### **Monitor Contínuo:**
```bash
python3 monitor.py --continuous
```

### **Ver Logs:**
```bash
tail -f anti_lag_bot.log
```

### **Parar Sistema:**
```bash
Ctrl + C
```

## 🔧 **Configurações:**

### **Horário Comercial:**
- **Início**: 9h
- **Fim**: 18h

### **Intervalos (segundos):**
```python
# Horário Comercial:
IDLE: 300s (5 min)
ACTIVE: 60s (1 min)
BUSY: 30s (30s)

# Fora do Horário:
IDLE: 600s (10 min)
ACTIVE: 300s (5 min)
BUSY: 60s (1 min)
```

### **Proteção:**
- **Máximo**: 100 requisições/hora
- **Pausa**: 1 hora se sobrecarregado
- **Backoff**: 5 minutos em caso de erro

## 📊 **Monitoramento:**

### **Logs Importantes:**
- `🚀 Sistema inicializado`
- `🎯 Pedidos encontrados`
- `✅ Pedido processado`
- `⚠️ Limite atingido`
- `🛑 Sistema pausado`

### **Status do Sistema:**
- **Verde**: Funcionando normalmente
- **Amarelo**: Acabou de processar
- **Vermelho**: Processando pedidos
- **Vermelho**: Sobrecarregado (pausa)

## 🛡️ **Segurança:**

- **Proteção contra sobrecarga** automática
- **Rate limiting** inteligente
- **Error handling** robusto
- **Health checks** contínuos
- **Logs detalhados** para debugging

## 🎯 **Resultado Final:**

Sistema que:
- ✅ **Se adapta** à demanda automaticamente
- ✅ **Protege** contra sobrecarga
- ✅ **Economiza** recursos significativamente
- ✅ **Mantém** eficiência quando necessário
- ✅ **Monitora** continuamente a saúde

**Sistema pronto para produção!** 🚀