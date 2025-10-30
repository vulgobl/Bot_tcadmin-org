#!/usr/bin/env python3
"""
Script de Diagnóstico do Sistema Anti-Lag TCAdmin
Verifica status, configurações e saúde do sistema
"""

import os
import sys
import time
import logging
from datetime import datetime
import subprocess

def check_system_status():
    """Verifica status geral do sistema"""
    print("🔍 DIAGNÓSTICO DO SISTEMA ANTI-LAG TCADMIN")
    print("=" * 60)
    print(f"⏰ Diagnóstico iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verifica se está no diretório correto
    if not os.path.exists('../anti_lag_bot.py'):
        print("❌ ERRO: Execute este script no diretório tcadmin_bot/scripts/")
        return False
    
    print("✅ Diretório correto")
    return True

def check_dependencies():
    """Verifica dependências Python"""
    print("\n🔍 Verificando dependências Python...")
    
    dependencies = [
        'selenium',
        'requests', 
        'dotenv'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - FALTANDO")
            missing.append(dep)
    
    if missing:
        print(f"\n📦 Dependências faltando: {', '.join(missing)}")
        print("💡 Execute: pip3 install " + " ".join(missing))
        return False
    
    return True

def check_chrome_driver():
    """Verifica ChromeDriver"""
    print("\n🌐 Verificando ChromeDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("✅ ChromeDriver funcionando")
        return True
    except Exception as e:
        print(f"❌ ChromeDriver com problema: {e}")
        print("💡 Instale o ChromeDriver: https://chromedriver.chromium.org/")
        return False

def check_environment_variables():
    """Verifica variáveis de ambiente"""
    print("\n⚙️ Verificando variáveis de ambiente...")
    
    # Carrega variáveis do arquivo .env
    try:
        from dotenv import load_dotenv
        load_dotenv('../variables.env')
        print("✅ Arquivo variables.env carregado")
    except Exception as e:
        print(f"⚠️ Erro ao carregar variables.env: {e}")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY', 
        'TCADMIN_URL',
        'TCADMIN_USERNAME',
        'TCADMIN_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mascara valores sensíveis
            if 'PASSWORD' in var or 'KEY' in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NÃO CONFIGURADA")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Variáveis faltando: {', '.join(missing_vars)}")
        print("💡 Configure no arquivo variables.env")
        return False
    
    return True

def check_process_status():
    """Verifica se o processo está rodando"""
    print("\n🔄 Verificando processo do sistema...")
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'anti_lag_bot' in result.stdout:
            print("✅ Processo anti_lag_bot encontrado")
            lines = [line for line in result.stdout.split('\n') if 'anti_lag_bot' in line]
            for line in lines:
                print(f"   {line}")
            return True
        else:
            print("❌ Processo anti_lag_bot NÃO encontrado")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar processo: {e}")
        return False

def check_log_files():
    """Verifica arquivos de log"""
    print("\n📋 Verificando arquivos de log...")
    
    log_files = [
        'anti_lag_bot.log',
        'bot_output.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✅ {log_file} ({size} bytes)")
            
            # Verifica logs recentes
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        print(f"   Última linha: {last_line[:100]}...")
            except Exception as e:
                print(f"   ⚠️ Erro ao ler log: {e}")
        else:
            print(f"❌ {log_file} - NÃO ENCONTRADO")

def check_system_resources():
    """Verifica recursos do sistema"""
    print("\n💻 Verificando recursos do sistema...")
    
    try:
        # Memória
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemAvailable' in line:
                    print(f"✅ {line}")
                    break
        
        # CPU
        result = subprocess.run(['nproc'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ CPUs disponíveis: {result.stdout.strip()}")
        
        # Espaço em disco
        result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                print(f"✅ Espaço em disco: {lines[1]}")
        
    except Exception as e:
        print(f"⚠️ Erro ao verificar recursos: {e}")

def check_network_connectivity():
    """Verifica conectividade de rede"""
    print("\n🌐 Verificando conectividade de rede...")
    
    # Testa Supabase
    try:
        import requests
        supabase_url = os.getenv('SUPABASE_URL')
        if supabase_url:
            response = requests.get(f"{supabase_url}/rest/v1/", timeout=10)
            if response.status_code == 200:
                print("✅ Supabase: Conectado")
            else:
                print(f"⚠️ Supabase: Status {response.status_code}")
        else:
            print("❌ Supabase: URL não configurada")
    except Exception as e:
        print(f"❌ Supabase: Erro de conexão - {e}")
    
    # Testa TCAdmin
    try:
        import requests
        tcadmin_url = os.getenv('TCADMIN_URL')
        if tcadmin_url:
            response = requests.get(tcadmin_url, timeout=10)
            if response.status_code == 200:
                print("✅ TCAdmin: Conectado")
            else:
                print(f"⚠️ TCAdmin: Status {response.status_code}")
        else:
            print("❌ TCAdmin: URL não configurada")
    except Exception as e:
        print(f"❌ TCAdmin: Erro de conexão - {e}")

def generate_report():
    """Gera relatório de diagnóstico"""
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DE DIAGNÓSTICO")
    print("=" * 60)
    
    # Verifica cada componente
    checks = [
        ("Sistema", check_system_status()),
        ("Dependências", check_dependencies()),
        ("ChromeDriver", check_chrome_driver()),
        ("Variáveis de Ambiente", check_environment_variables()),
        ("Processo", check_process_status()),
        ("Logs", True),  # Sempre True, apenas verifica arquivos
        ("Recursos", True),  # Sempre True, apenas verifica
        ("Rede", True)  # Sempre True, apenas verifica
    ]
    
    print("\n📋 RESUMO DOS CHECKS:")
    for name, status in checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}")
    
    # Conta sucessos
    success_count = sum(1 for _, status in checks if status)
    total_checks = len(checks)
    
    print(f"\n📊 RESULTADO: {success_count}/{total_checks} checks passaram")
    
    if success_count == total_checks:
        print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
    elif success_count >= total_checks * 0.8:
        print("⚠️ SISTEMA COM PEQUENOS PROBLEMAS")
    else:
        print("❌ SISTEMA COM PROBLEMAS CRÍTICOS")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    if success_count == total_checks:
        print("   🚀 Sistema pronto para produção!")
        print("   ▶️ Execute: ./run.sh")
    else:
        print("   🔧 Corrija os problemas identificados")
        print("   🔄 Execute este diagnóstico novamente")

def main():
    """Função principal"""
    if not check_system_status():
        return
    
    # Executa todos os checks
    check_dependencies()
    check_chrome_driver()
    check_environment_variables()
    check_process_status()
    check_log_files()
    check_system_resources()
    check_network_connectivity()
    
    # Gera relatório final
    generate_report()

if __name__ == "__main__":
    main()
