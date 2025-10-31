#!/usr/bin/env python3
"""
Script de teste para envio de email via Resend
Teste local antes de integrar no bot
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv('variables.env')

# Importa Resend
try:
    import resend
    print("✅ Biblioteca resend importada com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar resend: {e}")
    sys.exit(1)

# Configurações
RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
RESEND_FROM_EMAIL = os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
TCADMIN_URL = os.getenv('TCADMIN_URL', 'https://tcadmin.xyz/')

def test_send_email():
    """Testa envio de email"""
    
    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY não configurada!")
        print("   Configure em variables.env ou como variável de ambiente")
        return False
    
    print(f"📧 Configurações:")
    print(f"   API Key: {RESEND_API_KEY[:20]}...")
    print(f"   From: {RESEND_FROM_EMAIL}")
    print(f"   TCAdmin URL: {TCADMIN_URL}")
    print()
    
    # Dados de teste
    test_data = {
        'email': 'bernardoff683@gmail.com',
        'full_name': 'Bernardo Linhares Nascimento',
        'username': 'testuser123',
        'password': 'TestPass123!',
        'plan_name': 'Host MTA/SAMP - Starter',
        'server_name': 'CloudBase Hosting'
    }
    
    # Carrega template
    template_path = 'email_template.html'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"✅ Template carregado: {template_path}")
    except Exception as e:
        print(f"❌ Erro ao carregar template: {e}")
        return False
    
    # Substitui variáveis
    replacements = {
        '{{FULL_NAME}}': test_data['full_name'],
        '{{COMPANY_NAME}}': test_data['server_name'],
        '{{USERNAME}}': test_data['username'],
        '{{PASSWORD}}': test_data['password'],
        '{{PLAN_NAME}}': test_data['plan_name'],
        '{{TCADMIN_URL}}': TCADMIN_URL,
        '{{TCADMIN_ALTERNATIVE_URL}}': TCADMIN_URL,
        '{{WEBSITE_URL}}': 'https://cloudbasehosting.com.br'
    }
    
    for key, value in replacements.items():
        html_content = html_content.replace(key, str(value))
    
    print(f"✅ Template processado com variáveis")
    print()
    
    # Envia email
    try:
        print("📧 Enviando email de teste...")
        
        # Tenta diferentes formas de usar o Resend
        try:
            # Método 1: resend.Resend()
            if hasattr(resend, 'Resend'):
                resend_client = resend.Resend(api_key=RESEND_API_KEY)
                print("✅ Método 1: resend.Resend() funcionou")
            else:
                # Método 2: resend.Client()
                if hasattr(resend, 'Client'):
                    resend_client = resend.Client(api_key=RESEND_API_KEY)
                    print("✅ Método 2: resend.Client() funcionou")
                else:
                    # Método 3: Usar diretamente
                    resend.api_key = RESEND_API_KEY
                    resend_client = resend
                    print("✅ Método 3: Usando resend diretamente")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar Resend: {e}")
            print("🔄 Tentando método alternativo...")
            resend_client = resend
        
        # Tenta enviar
        params = {
            "from": RESEND_FROM_EMAIL,
            "to": [test_data['email']],
            "subject": "🎉 Teste - Seu host foi criado com sucesso! - CloudBase Hosting",
            "html": html_content
        }
        
        print(f"📤 Enviando para: {test_data['email']}")
        
        # Tenta diferentes formas de enviar
        email_response = None
        try:
            if hasattr(resend_client, 'emails') and hasattr(resend_client.emails, 'send'):
                email_response = resend_client.emails.send(params)
            elif hasattr(resend_client, 'send'):
                email_response = resend_client.send(params)
            elif hasattr(resend, 'send'):
                email_response = resend.send(params)
            else:
                print("❌ Não encontrei método de envio no resend")
                print(f"   Atributos disponíveis: {dir(resend_client)}")
                return False
        except Exception as e:
            print(f"❌ Erro ao enviar: {e}")
            print(f"   Tipo de erro: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
        
        print(f"✅ Email enviado com sucesso!")
        print(f"📧 Response: {email_response}")
        
        if isinstance(email_response, dict):
            email_id = email_response.get('id', email_response.get('data', {}).get('id', 'N/A'))
            print(f"📧 Email ID: {email_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 === TESTE DE ENVIO DE EMAIL ===")
    print()
    
    success = test_send_email()
    
    print()
    if success:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("❌ TESTE FALHOU")
        sys.exit(1)

