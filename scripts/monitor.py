#!/usr/bin/env python3
"""
Monitor do Sistema Anti-Lag
Verifica status e performance do sistema
"""

import os
import time
import json
from datetime import datetime, timedelta

def check_log_file():
    """Verifica se o arquivo de log existe e está sendo atualizado"""
    log_file = "../anti_lag_bot.log"
    
    if not os.path.exists(log_file):
        return False, "Arquivo de log não encontrado"
    
    # Verifica se foi modificado nos últimos 5 minutos
    mod_time = os.path.getmtime(log_file)
    last_mod = datetime.fromtimestamp(mod_time)
    now = datetime.now()
    
    if (now - last_mod).seconds > 300:  # 5 minutos
        return False, f"Log não atualizado desde {last_mod.strftime('%H:%M:%S')}"
    
    return True, f"Log atualizado em {last_mod.strftime('%H:%M:%S')}"

def get_system_status():
    """Obtém status do sistema"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "log_status": check_log_file(),
        "uptime": "N/A",
        "last_activity": "N/A"
    }
    
    # Verifica arquivo de log para extrair informações
    log_file = "../anti_lag_bot.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Conta diferentes tipos de logs
            total_logs = len(lines)
            error_logs = len([l for l in lines if 'ERROR' in l])
            warning_logs = len([l for l in lines if 'WARNING' in l])
            info_logs = len([l for l in lines if 'INFO' in l])
            
            # Última atividade
            if lines:
                last_line = lines[-1].strip()
                status["last_activity"] = last_line
            
            status.update({
                "total_logs": total_logs,
                "error_logs": error_logs,
                "warning_logs": warning_logs,
                "info_logs": info_logs
            })
            
        except Exception as e:
            status["log_error"] = str(e)
    
    return status

def display_status():
    """Exibe status do sistema"""
    print("📊 MONITOR DO SISTEMA ANTI-LAG TCADMIN")
    print("=" * 50)
    
    status = get_system_status()
    
    print(f"⏰ Verificação: {status['timestamp']}")
    print(f"📋 Status do Log: {status['log_status'][1]}")
    
    if 'total_logs' in status:
        print(f"📊 Total de Logs: {status['total_logs']}")
        print(f"❌ Erros: {status['error_logs']}")
        print(f"⚠️ Avisos: {status['warning_logs']}")
        print(f"ℹ️ Informações: {status['info_logs']}")
    
    if status['last_activity'] != 'N/A':
        print(f"🔄 Última Atividade: {status['last_activity']}")
    
    # Verifica saúde do sistema
    if status['log_status'][0]:
        print("✅ Sistema funcionando normalmente")
    else:
        print("⚠️ Sistema pode estar com problemas")
    
    print("-" * 50)

def monitor_continuous():
    """Monitor contínuo"""
    print("🔄 Iniciando monitor contínuo...")
    print("🛑 Para parar: Ctrl+C")
    
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            display_status()
            time.sleep(30)  # Atualiza a cada 30 segundos
    except KeyboardInterrupt:
        print("\n🛑 Monitor interrompido")

def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor_continuous()
    else:
        display_status()

if __name__ == "__main__":
    main()
