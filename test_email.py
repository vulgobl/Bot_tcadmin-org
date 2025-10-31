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
        '{{WEBSITE_URL}}': 'https://cloudbasehosting.store'
    }
    
    for key, value in replacements.items():
        html_content = html_content.replace(key, str(value))
    
    print(f"✅ Template processado com variáveis")
    print()
    
    # Envia email
    try:
        print("📧 Enviando email de teste...")
        
        # Prepara parâmetros
        params = {
            "from": RESEND_FROM_EMAIL,
            "to": [test_data['email']],
            "subject": "🎉 Teste - Seu host foi criado com sucesso! - CloudBase Hosting",
            "html": html_content
        }
        
        print(f"📤 Enviando para: {test_data['email']}")
        
        # Tenta diferentes formas de usar o Resend
        email_response = None
        
        # Método 1: resend.Emails diretamente com api_key
        try:
            if hasattr(resend, 'Emails'):
                emails_api = resend.Emails(api_key=RESEND_API_KEY)
                email_response = emails_api.send(params)
                print("✅ Método 1: resend.Emails() funcionou")
            else:
                raise AttributeError("Emails não encontrado")
        except Exception as e1:
            print(f"⚠️ Método 1 falhou: {e1}")
            
            # Método 2: resend.emails.send com api_key configurada
            try:
                resend.api_key = RESEND_API_KEY
                if hasattr(resend, 'emails') and hasattr(resend.emails, 'send'):
                    email_response = resend.emails.send(params)
                    print("✅ Método 2: resend.emails.send() funcionou")
                else:
                    raise AttributeError("emails.send não encontrado")
            except Exception as e2:
                print(f"⚠️ Método 2 falhou: {e2}")
                
                # Método 3: Usar Requests diretamente (fallback)
                try:
                    import requests
                    headers = {
                        "Authorization": f"Bearer {RESEND_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    response = requests.post(
                        "https://api.resend.com/emails",
                        headers=headers,
                        json=params,
                        timeout=30
                    )
                    if response.status_code == 200:
                        email_response = response.json()
                        print("✅ Método 3: API direta funcionou")
                    else:
                        raise Exception(f"API retornou {response.status_code}: {response.text}")
                except Exception as e3:
                    print(f"❌ Método 3 falhou: {e3}")
                    print(f"❌ Todos os métodos falharam")
                    import traceback
                    traceback.print_exc()
                    return False
        
        if email_response is None:
            print("❌ Nenhum método funcionou")
            return False
    
        print(f"✅ Email enviado com sucesso!")
        print(f"📧 Response: {email_response}")
        
        # Extrai ID do email da resposta
        email_id = 'N/A'
        if isinstance(email_response, dict):
            email_id = email_response.get('id') or email_response.get('data', {}).get('id', 'N/A')
        elif hasattr(email_response, 'id'):
            email_id = email_response.id
        
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

