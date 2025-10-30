#!/usr/bin/env python3
"""
Setup do Sistema Anti-Lag para Produção
Configura e valida o ambiente
"""

import os
import sys
import subprocess
from datetime import datetime

def check_dependencies():
    """Verifica dependências necessárias"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'selenium',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - FALTANDO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Instalando pacotes faltantes: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} instalado")
            except subprocess.CalledProcessError:
                print(f"❌ Erro ao instalar {package}")
                return False
    
    return True

def check_chrome_driver():
    """Verifica se o ChromeDriver está disponível"""
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

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios...")
    
    directories = [
        'logs',
        'backups'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ {directory}")
        else:
            print(f"✅ {directory} já existe")

def validate_config():
    """Valida configurações"""
    print("\n⚙️ Validando configurações...")
    
    # Verifica arquivos necessários
    required_files = [
        '../anti_lag_bot.py',
        '../start_production.py',
        'monitor.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - FALTANDO")
            return False
    
    return True

def create_systemd_service():
    """Cria serviço systemd (opcional)"""
    print("\n🔧 Criando serviço systemd...")
    
    service_content = f"""[Unit]
Description=Sistema Anti-Lag TCAdmin
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} {os.path.join(os.getcwd(), 'start_production.py')}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/tmp/anti-lag-tcadmin.service"
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Arquivo de serviço criado: {service_file}")
        print("💡 Para instalar o serviço:")
        print(f"   sudo cp {service_file} /etc/systemd/system/")
        print("   sudo systemctl daemon-reload")
        print("   sudo systemctl enable anti-lag-tcadmin")
        print("   sudo systemctl start anti-lag-tcadmin")
        
    except Exception as e:
        print(f"❌ Erro ao criar serviço: {e}")

def main():
    """Função principal de setup"""
    print("🚀 SETUP DO SISTEMA ANTI-LAG TCADMIN")
    print("=" * 50)
    print(f"⏰ Setup iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verifica dependências
    if not check_dependencies():
        print("❌ Falha na verificação de dependências")
        return False
    
    # Verifica ChromeDriver
    if not check_chrome_driver():
        print("⚠️ ChromeDriver com problemas, mas continuando...")
    
    # Cria diretórios
    create_directories()
    
    # Valida configurações
    if not validate_config():
        print("❌ Falha na validação de configurações")
        return False
    
    # Cria serviço systemd
    create_systemd_service()
    
    print("\n" + "=" * 50)
    print("✅ SETUP CONCLUÍDO COM SUCESSO!")
    print()
    print("🚀 Para iniciar o sistema:")
    print("   python3 start_production.py")
    print()
    print("📊 Para monitorar:")
    print("   python3 monitor.py")
    print()
    print("📋 Logs serão salvos em: anti_lag_bot.log")
    print("🛑 Para parar: Ctrl+C")
    
    return True

if __name__ == "__main__":
    main()
