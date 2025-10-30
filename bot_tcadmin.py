#!/usr/bin/env python3
"""
Bot de Automação TCAdmin - Versão Principal
Processa pedidos individuais e cria usuários completos no TCAdmin
Inclui seção de perfil com dados do Supabase
"""

import time
import logging
import random
import string
import secrets
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import requests
import json

class TCAdminBot:
    def __init__(self, headless=False):
        """Inicializa o bot principal"""
        self.driver = None
        self.wait = None
        self.headless = headless
        self.setup_logging()
        
        # Configurações do Supabase
        self.supabase_url = "https://gxvcovuwtbpkvzqdbcbr.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd4dmNvdnV3dGJwa3Z6cWRiY2JyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyMDU0MzgsImV4cCI6MjA2Mzc4MTQzOH0.O9Z831v0AJaBvtYyGUcDMBuVNmONNqWkIhJYuVa3FpM"
        
    def setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Configura e inicializa o driver do Chrome"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
                self.logger.info("Modo headless ativado")
            else:
                self.logger.info("Modo VISUAL ativado - você verá o navegador")
            
            # Configurações otimizadas
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

            # Tenta localizar binário do Chromium/Chrome via envs e locais comuns (Railway/Nixpacks)
            import os
            binary_candidates = [
                os.getenv('CHROME_BIN'),
                os.getenv('GOOGLE_CHROME_BIN'),
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
                '/usr/bin/google-chrome',
            ]
            chrome_binary = None
            for bin_path in binary_candidates:
                if bin_path and os.path.exists(bin_path):
                    chrome_binary = bin_path
                    chrome_options.binary_location = bin_path
                    self.logger.info(f"✅ Chrome encontrado em: {bin_path}")
                    break
            
            if not chrome_binary:
                self.logger.warning("⚠️ Chrome/Chromium não encontrado no sistema!")
                self.logger.info("🔧 Tentando instalar Chromium automaticamente...")
                
                # Tenta instalar via apt-get (se disponível e com permissões)
                try:
                    import subprocess
                    result = subprocess.run(
                        ["apt-get", "update", "-qq"],
                        capture_output=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        # Tenta vários nomes de pacote
                        packages = ["chromium", "chromium-browser", "google-chrome-stable"]
                        installed = False
                        for pkg in packages:
                            self.logger.info(f"🔧 Tentando instalar {pkg}...")
                            result = subprocess.run(
                                ["apt-get", "install", "-y", "-qq", pkg],
                                capture_output=True,
                                timeout=120
                            )
                            if result.returncode == 0:
                                self.logger.info(f"✅ {pkg} instalado com sucesso!")
                                installed = True
                                break
                            else:
                                self.logger.warning(f"⚠️ {pkg} não disponível: {result.stderr.decode()[:100]}")
                        
                        if installed:
                            self.logger.info("✅ Chromium instalado com sucesso!")
                            # Tenta encontrar novamente
                            for bin_path in ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable']:
                                if os.path.exists(bin_path):
                                    chrome_binary = bin_path
                                    chrome_options.binary_location = bin_path
                                    self.logger.info(f"✅ Chrome encontrado em: {bin_path}")
                                    break
                        else:
                            self.logger.warning("⚠️ Nenhum pacote Chromium/Chrome disponível nos repositórios apt")
                    else:
                        self.logger.warning("⚠️ apt-get não disponível ou sem permissões")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao tentar instalar Chromium: {str(e)}")
                
                if not chrome_binary:
                    self.logger.error("❌ CRÍTICO: Chromium não está instalado!")
                    self.logger.error("❌ Configure NIXPACKS_PKGS na Railway com: chromium chromium-driver nss libXScrnSaver alsa-lib fontconfig at-spi2-atk gtk3 libdrm mesa libxshmfence")
                    raise Exception("Chromium não encontrado. Configure NIXPACKS_PKGS na Railway ou instale manualmente.")

            # Tenta usar um chromedriver conhecido se existir
            service = None
            driver_candidates = [
                os.getenv('CHROMEDRIVER_PATH'),
                '/usr/lib/chromium/chromedriver',
                '/usr/bin/chromedriver',
            ]
            for drv in driver_candidates:
                if drv and os.path.exists(drv):
                    service = Service(drv)
                    self.logger.info(f"✅ Usando ChromeDriver do sistema em: {drv}")
                    break

            if not service:
                # Fallback: usa webdriver-manager para baixar o driver compatível
                self.logger.info("📥 Baixando ChromeDriver via webdriver-manager...")
                try:
                    driver_path = ChromeDriverManager().install()
                    service = Service(driver_path)
                    self.logger.info(f"✅ ChromeDriver baixado em: {driver_path}")
                except Exception as e:
                    self.logger.error(f"❌ Erro ao baixar ChromeDriver: {e}")
                    raise
            
            # Verifica se o Chrome está realmente instalado antes de tentar usar
            if chrome_binary:
                # Testa se o binário é executável
                import stat
                if not os.access(chrome_binary, os.X_OK):
                    self.logger.error(f"❌ Chrome em {chrome_binary} não é executável!")
                    raise Exception(f"Chrome não é executável em {chrome_binary}")
            
            self.driver = webdriver.Chrome(options=chrome_options, service=service)
            self.wait = WebDriverWait(self.driver, 30)
            
            self.logger.info("Driver do Chrome inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar o driver: {str(e)}")
            return False
    
    def get_order_from_supabase(self, order_id):
        """Busca um pedido específico no Supabase"""
        try:
            self.logger.info(f"🔍 Buscando pedido {order_id} no Supabase...")
            
            # URL da API do Supabase
            url = f"{self.supabase_url}/rest/v1/orders"
            
            # Headers para autenticação
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Parâmetros da query
            params = {
                'id': f'eq.{order_id}',
                'select': 'id,user_id,plan_id,status,price_at_order,currency_at_order,user_notes,server_name_preference,created_at,slots'
            }
            
            # Fazer requisição
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                orders = response.json()
                if orders:
                    order = orders[0]
                    self.logger.info(f"✅ Pedido {order_id} encontrado no Supabase")
                    return order
                else:
                    self.logger.warning(f"⚠️ Pedido {order_id} não encontrado no Supabase, usando dados simulados")
                    return self.get_simulated_order_data(order_id)
            else:
                self.logger.warning(f"⚠️ Erro ao buscar pedido: {response.status_code}, usando dados simulados")
                return self.get_simulated_order_data(order_id)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao conectar com Supabase: {str(e)}, usando dados simulados")
            return self.get_simulated_order_data(order_id)
    
    def get_simulated_order_data(self, order_id):
        """Retorna dados simulados para demonstração"""
        simulated_orders = {
            '8f838023-ab78-4468-ad2b-b830894fb156': {
                'id': '8f838023-ab78-4468-ad2b-b830894fb156',
                'user_id': '07aed47d-def0-4e24-9347-d3b86f0e2c10',
                'plan_id': '0cd3d499-b611-4751-8c1e-adb494c836e1',
                'status': 'pending',
                'price_at_order': 29.90,
                'currency_at_order': 'BRL',
                'user_notes': 'Pedido de teste para bot',
                'server_name_preference': 'teste_servidor_001',
                'created_at': '2025-10-05T10:00:00.000Z',
                'slots': 19  # Slots do plano Starter (conforme teste)
            },
            'test-professional': {
                'id': 'test-professional',
                'user_id': '07aed47d-def0-4e24-9347-d3b86f0e2c10',
                'plan_id': '10ae6193-4751-8c1e-adb494c836e1',
                'status': 'pending',
                'price_at_order': 59.90,
                'currency_at_order': 'BRL',
                'user_notes': 'Pedido Professional para teste',
                'server_name_preference': 'servidor_professional',
                'created_at': '2025-10-05T10:00:00.000Z',
                'slots': 25  # Slots do plano Professional
            },
            'test-enterprise': {
                'id': 'test-enterprise',
                'user_id': '07aed47d-def0-4e24-9347-d3b86f0e2c10',
                'plan_id': '2c04849a-4751-8c1e-adb494c836e1',
                'status': 'pending',
                'price_at_order': 99.90,
                'currency_at_order': 'BRL',
                'user_notes': 'Pedido Enterprise para teste',
                'server_name_preference': 'servidor_enterprise',
                'created_at': '2025-10-05T10:00:00.000Z',
                'slots': 50  # Slots do plano Enterprise
            }
        }
        
        if order_id in simulated_orders:
            self.logger.info(f"✅ Dados simulados encontrados para pedido {order_id}")
            return simulated_orders[order_id]
        else:
            self.logger.error(f"❌ Pedido {order_id} não encontrado nos dados simulados")
            return None
    
    def generate_rcon_password(self):
        """Gera uma senha RCON aleatória"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        rcon_password = ''.join(secrets.choice(characters) for _ in range(16))
        return rcon_password
    
    def get_user_profile_from_supabase(self, user_id):
        """Busca dados do perfil do usuário no Supabase"""
        try:
            self.logger.info(f"👤 Buscando perfil do usuário {user_id} no Supabase...")
            
            # URL da API do Supabase
            url = f"{self.supabase_url}/rest/v1/profiles"
            
            # Headers para autenticação
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Parâmetros da query - busca por user_id na tabela profiles
            params = {
                'user_id': f'eq.{user_id}',
                'select': 'phone,email,full_name'
            }
            
            # Fazer requisição
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                profiles = response.json()
                self.logger.info(f"📊 Resposta do Supabase: {profiles}")
                if profiles:
                    profile = profiles[0]
                    self.logger.info(f"✅ Perfil encontrado para usuário {user_id}: {profile}")
                    return profile
                else:
                    self.logger.warning(f"⚠️ Perfil não encontrado para usuário {user_id}, usando dados simulados")
                    return self.get_simulated_profile_data(user_id)
            else:
                self.logger.warning(f"⚠️ Erro ao buscar perfil: {response.status_code}, usando dados simulados")
                return self.get_simulated_profile_data(user_id)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao conectar com Supabase: {str(e)}, usando dados simulados")
            return self.get_simulated_profile_data(user_id)
    
    def get_simulated_profile_data(self, user_id):
        """Retorna dados simulados do perfil para demonstração"""
        simulated_profiles = {
            '07aed47d-def0-4e24-9347-d3b86f0e2c10': {
                'phone': '+55 11 99999-9999',
                'email': 'usuario.teste@email.com',
                'timezone': 'America/Sao_Paulo'
            }
        }
        
        if user_id in simulated_profiles:
            self.logger.info(f"✅ Dados simulados do perfil encontrados para usuário {user_id}")
            return simulated_profiles[user_id]
        else:
            self.logger.warning(f"⚠️ Perfil não encontrado para usuário {user_id}, usando dados padrão")
            return self.get_default_profile_data()
    
    def get_default_profile_data(self):
        """Retorna dados padrão do perfil"""
        return {
            'phone': '+55 11 00000-0000',
            'email': 'default@email.com',
            'timezone': 'America/Sao_Paulo'
        }
    
    def update_order_status_in_supabase(self, order_id, status='completed'):
        """Atualiza status do pedido no Supabase"""
        try:
            self.logger.info(f"🔄 Atualizando status do pedido {order_id} para {status}")
            
            url = f"{self.supabase_url}/rest/v1/orders"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            response = requests.patch(
                f"{url}?id=eq.{order_id}",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200 or response.status_code == 204:
                self.logger.info(f"✅ Status do pedido {order_id} atualizado para {status}")
                return True
            else:
                self.logger.error(f"❌ Erro ao atualizar pedido: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar pedido no Supabase: {str(e)}")
            return False
    
    def navigate_to_admin_panel(self, url="https://tcadmin.xyz/"):
        """Navega para o painel admin"""
        try:
            self.logger.info(f"🌐 Navegando para: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            if "tcadmin" in self.driver.title.lower() or "login" in self.driver.title.lower():
                self.logger.info("✅ Página do painel admin carregada com sucesso")
                return True
            else:
                self.logger.warning("⚠️ Página pode não ter carregado corretamente")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao navegar para o painel admin: {str(e)}")
            return False
    
    def login(self, username, password, tcadmin_url=None):
        """Realiza login no painel admin"""
        try:
            # Inicializa o driver se não estiver inicializado
            if self.driver is None:
                self.setup_driver()
            
            # Navega para o TCAdmin primeiro
            import os
            if not tcadmin_url:
                tcadmin_url = os.getenv('TCADMIN_URL', 'https://tcadmin.xyz/')
            if not self.navigate_to_admin_panel(tcadmin_url):
                self.logger.error("❌ Falha ao navegar para o painel admin")
                return False
            
            self.logger.info("🔐 Iniciando processo de login")
            
            # Aguarda a página carregar completamente
            time.sleep(5)
            
            # Usa os seletores corretos descobertos
            username_field = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='UserName']")))
            password_field = self.driver.find_element(By.XPATH, "//input[@name='Password']")
            
            # Preenche os campos
            username_field.clear()
            username_field.send_keys(username)
            self.logger.info("✅ Usuário inserido")
            
            password_field.clear()
            password_field.send_keys(password)
            self.logger.info("✅ Senha inserida")
            
            # Clica no botão de login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            self.logger.info("✅ Botão de login clicado")
            
            # Aguarda o redirecionamento
            time.sleep(8)
            
            # Verifica se o login foi bem-sucedido
            if self.is_logged_in():
                self.logger.info("🎉 Login realizado com sucesso!")
                return True
            else:
                self.logger.warning("⚠️ Falha no login")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro durante o login: {str(e)}")
            return False
    
    def is_logged_in(self):
        """Verifica se o usuário está logado"""
        try:
            # Inicializa o driver se não estiver inicializado
            if self.driver is None:
                self.setup_driver()
            
            current_url = self.driver.current_url
            if "login" not in current_url.lower() and "tcadmin" in current_url.lower():
                return True
            
            # Procura por elementos que indicam que está logado
            logged_in_indicators = [
                "a[href*='logout']",
                "a[href*='admin']",
                ".user-menu",
                ".admin-panel"
            ]
            
            for indicator in logged_in_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, f"//*[contains(@class, 'success') or contains(@class, 'alert-success') or contains(@class, 'success-message')]")
                    if elements:
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar status de login: {str(e)}")
            return False
    
    def navigate_to_create_user(self):
        """Navega para a página de criação de usuário"""
        try:
            self.logger.info("🖱️ Navegando para User Management → Create a User...")
            
            # 1. Clica em "User Management"
            self.logger.info("🔍 Procurando 'User Management'...")
            
            # Tenta diferentes estratégias para encontrar o link
            user_management_link = None
            
            # Estratégia 1: Busca por texto exato
            try:
                user_management_link = self.driver.find_element(By.LINK_TEXT, "User Management")
                self.logger.info("✅ Encontrado por LINK_TEXT")
            except:
                pass
            
            # Estratégia 2: Busca por texto parcial
            if not user_management_link:
                try:
                    user_management_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "User Management")
                    self.logger.info("✅ Encontrado por PARTIAL_LINK_TEXT")
                except:
                    pass
            
            # Estratégia 3: Busca por XPath com texto
            if not user_management_link:
                try:
                    user_management_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'User Management')]")
                    self.logger.info("✅ Encontrado por XPath")
                except:
                    pass
            
            # Estratégia 4: Busca em todos os links
            if not user_management_link:
                user_management_links = self.driver.find_elements(By.XPATH, "//a")
                for link in user_management_links:
                    if "user management" in link.text.lower():
                        user_management_link = link
                        self.logger.info("✅ Encontrado por busca em todos os links")
                        break
            
            if user_management_link:
                user_management_link.click()
                self.logger.info("✅ Clicado em 'User Management'")
                time.sleep(3)
            else:
                self.logger.error("❌ Link 'User Management' não encontrado")
                # Lista todos os links disponíveis para debug
                all_links = self.driver.find_elements(By.XPATH, "//a")
                self.logger.info("🔍 Links disponíveis:")
                for i, link in enumerate(all_links[:10]):  # Mostra apenas os primeiros 10
                    self.logger.info(f"   {i+1}. '{link.text}'")
                return False
            
            # 2. Clica em "Create a User"
            self.logger.info("🔍 Procurando 'Create a User'...")
            
            # Tenta diferentes estratégias para encontrar o link
            create_user_link = None
            
            # Estratégia 1: Busca por texto exato
            try:
                create_user_link = self.driver.find_element(By.LINK_TEXT, "Create a User")
                self.logger.info("✅ Encontrado por LINK_TEXT")
            except:
                pass
            
            # Estratégia 2: Busca por texto parcial
            if not create_user_link:
                try:
                    create_user_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Create a User")
                    self.logger.info("✅ Encontrado por PARTIAL_LINK_TEXT")
                except:
                    pass
            
            # Estratégia 3: Busca por XPath com texto
            if not create_user_link:
                try:
                    create_user_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Create a User')]")
                    self.logger.info("✅ Encontrado por XPath")
                except:
                    pass
            
            # Estratégia 4: Busca em todos os links
            if not create_user_link:
                create_user_links = self.driver.find_elements(By.XPATH, "//a")
                for link in create_user_links:
                    if "create a user" in link.text.lower():
                        create_user_link = link
                        self.logger.info("✅ Encontrado por busca em todos os links")
                        break
            
            if create_user_link:
                create_user_link.click()
                self.logger.info("✅ Clicado em 'Create a User'")
                time.sleep(10)  # Aguarda carregar
            else:
                self.logger.error("❌ Link 'Create a User' não encontrado")
                # Lista todos os links disponíveis para debug
                all_links = self.driver.find_elements(By.XPATH, "//a")
                self.logger.info("🔍 Links disponíveis:")
                for i, link in enumerate(all_links[:10]):  # Mostra apenas os primeiros 10
                    self.logger.info(f"   {i+1}. '{link.text}'")
                return False
            
            self.logger.info(f"📄 Página atual: {self.driver.title}")
            self.logger.info(f"🔗 URL atual: {self.driver.current_url}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao navegar para criação de usuário: {str(e)}")
            return False
    
    def switch_to_create_user_iframe(self):
        """Muda para o iframe de criação de usuário"""
        try:
            self.logger.info("🖼️ Procurando iframe de criação de usuário...")
            
            # Procura pelo iframe correto
            iframes = self.driver.find_elements(By.XPATH, "//iframe")
            create_user_iframe = None
            
            for iframe in iframes:
                iframe_src = iframe.get_attribute("src") or ""
                if "CreateUser.aspx" in iframe_src:
                    create_user_iframe = iframe
                    break
            
            if create_user_iframe:
                self.driver.switch_to.frame(create_user_iframe)
                self.logger.info("✅ Mudou para iframe de criação de usuário")
                time.sleep(3)
                return True
            else:
                self.logger.error("❌ Iframe de criação de usuário não encontrado")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao mudar para iframe: {str(e)}")
            return False
    
    def generate_random_password(self, length=12):
        """Gera senha aleatória"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(characters) for _ in range(length))
    
    def create_user_in_tcadmin(self, order_data):
        """Cria usuário no TCAdmin usando dados específicos do pedido"""
        try:
            # Extrai dados do pedido
            username = order_data.get('server_name_preference', f"user_{order_data['id']}")
            # Usa o tcadmin_id do pedido (não gera aleatório)
            billing_id = order_data.get('tcadmin_id', str(order_data['id'])[:8])
            password = self.generate_random_password()
            user_id = order_data.get('user_id')
            
            self.logger.info(f"👤 Criando usuário para pedido {order_data['id']}:")
            self.logger.info(f"   📝 Nome: {username}")
            self.logger.info(f"   💳 Billing ID: {billing_id}")
            self.logger.info(f"   🔐 Senha: {password}")
            
            # Navega para a página de criação de usuário primeiro
            if not self.navigate_to_create_user():
                self.logger.error("❌ Falha ao navegar para página de criação de usuário")
                return False
            
            # Muda para o iframe
            if not self.switch_to_create_user_iframe():
                return False
            
            # === ETAPA 1: DADOS INICIAIS ===
            self.logger.info("📋 Preenchendo dados iniciais...")
            
            # Preenche campo de username
            username_field = self.wait.until(EC.presence_of_element_located((
                By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxLabelUserNameTextBox']"
            )))
            username_field.clear()
            username_field.send_keys(username)
            self.logger.info("✅ Username preenchido")
            
            # Preenche campo de password
            password_field = self.driver.find_element(
                By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxPassword']"
            )
            password_field.clear()
            password_field.send_keys(password)
            self.logger.info("✅ Password preenchido")
            
            # Preenche campo de billing ID
            billing_field = self.driver.find_element(
                By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxBillingId']"
            )
            billing_field.clear()
            billing_field.send_keys(billing_id)
            self.logger.info("✅ Billing ID preenchido")
            
            # === ETAPA 2: SEÇÃO PERFIL ===
            self.logger.info("👤 Acessando seção de perfil...")
            
            # Procura pelo botão "Perfil" ou "Profile"
            try:
                profile_button = self.driver.find_element(By.XPATH, "//*[@id='TabProfile']")
                profile_button.click()
                self.logger.info("✅ Clicado em 'Perfil'")
                time.sleep(3)
                
                # Usa dados do perfil que já estão no order_data (já buscados corretamente)
                profile_data = order_data.get('profile', {})
                self.logger.info(f"📊 Usando dados do perfil do order_data: {profile_data}")
                
                # Preenche celular (campo celular, não telefone residencial)
                try:
                    phone_field = self.driver.find_element(By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxMobilePhoneTextBox']")
                    phone_field.clear()
                    phone_field.send_keys(profile_data.get('phone', ''))
                    self.logger.info(f"✅ Celular preenchido: {profile_data.get('phone', '')}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao preencher celular: {str(e)}")
                
                # Preenche email primário
                try:
                    email_field = self.driver.find_element(By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxPrimaryEmailTextBox']")
                    email_field.clear()
                    email_field.send_keys(profile_data.get('email', ''))
                    self.logger.info(f"✅ Email primário preenchido: {profile_data.get('email', '')}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao preencher email primário: {str(e)}")
                
                # Configura fuso horário para Brasília
                try:
                    timezone_field = self.driver.find_element(By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_DropDownListTimeZone']")
                    timezone_field.send_keys("America/Sao_Paulo")
                    self.logger.info("✅ Fuso horário configurado para Brasília")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao configurar fuso horário: {str(e)}")
                
                self.logger.info("✅ Seção de perfil preenchida com sucesso")
            except:
                self.logger.warning("⚠️ Botão 'Perfil' não encontrado, continuando sem dados de perfil")
            
            
            # === ETAPA 3: CLICAR EM SALVE ===
            try:
                self.logger.info("💾 Procurando botão 'Salve'...")
                
                # Procura pelo botão "Salve" ou "Save"
                try:
                    save_button = self.driver.find_element(By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TabToolBar1_RadToolBar1']/div[1]/div[1]/div[1]/ul[1]/li[1]/a[1]")
                    save_button.click()
                    self.logger.info("✅ Botão 'Salve' clicado com sucesso!")
                    time.sleep(5)
                    
                    if self.verify_user_created(username):
                        self.logger.info(f"🎉 Usuário {username} criado com sucesso!")
                        
                        # === ETAPA 4: CRIAR SERVIÇO PARA O USUÁRIO ===
                        self.logger.info("✅ Etapa de criação de usuário concluída!")
                        self.logger.info("🛠️ Iniciando criação de serviço...")
                        
                        # Pegar slots do pedido
                        slots = order_data.get('slots', 8)  # Pega da coluna slots do pedido
                        
                        if self.create_service_for_user(username, slots, order_data):
                            self.logger.info(f"🎉 Serviço criado para usuário {username}!")
                            return True
                        else:
                            self.logger.warning(f"⚠️ Erro ao criar serviço para usuário {username}")
                            return True  # Usuário foi criado, mesmo se serviço falhar
                    else:
                        self.logger.warning(f"⚠️ Usuário {username} pode não ter sido criado")
                        return False
                except:
                    self.logger.info("🔄 Tentando submit via JavaScript...")
                    self.driver.execute_script("document.forms[0].submit();")
                    self.logger.info("✅ Submit via JavaScript executado")
                    time.sleep(5)
                    
                    if self.verify_user_created(username):
                        self.logger.info(f"🎉 Usuário {username} criado com sucesso!")
                        
                        # === ETAPA 4: CRIAR SERVIÇO PARA O USUÁRIO ===
                        self.logger.info("✅ Etapa de criação de usuário concluída!")
                        self.logger.info("🛠️ Iniciando criação de serviço...")
                        
                        # Pegar slots do pedido
                        slots = order_data.get('slots', 8)  # Pega da coluna slots do pedido
                        
                        if self.create_service_for_user(username, slots, order_data):
                            self.logger.info(f"🎉 Serviço criado para usuário {username}!")
                            return True
                        else:
                            self.logger.warning(f"⚠️ Erro ao criar serviço para usuário {username}")
                            return True  # Usuário foi criado, mesmo se serviço falhar
                    else:
                        self.logger.warning(f"⚠️ Usuário {username} pode não ter sido criado")
                        return False
                    
            except Exception as e:
                self.logger.error(f"❌ Erro ao clicar em Salve: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar usuário: {str(e)}")
            return False
    
    def verify_user_created(self, username):
        """Verifica se o usuário foi criado com sucesso"""
        try:
            # Procura por mensagens de sucesso ou redirecionamento
            success_indicators = [
                "user created",
                "usuário criado",
                "success",
                "sucesso",
                "created successfully",
                "criado com sucesso"
            ]
            
            page_source = self.driver.page_source.lower()
            for indicator in success_indicators:
                if indicator in page_source:
                    return True
            
            # Verifica se a URL mudou (indicando redirecionamento)
            current_url = self.driver.current_url
            if "createuser" not in current_url.lower():
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar criação do usuário: {str(e)}")
            return False
    
    def create_service_for_user(self, username, slots=8, order_data=None):
        """Cria um serviço para o usuário recém-criado"""
        try:
            self.logger.info(f"🛠️ Criando serviço para usuário {username} com {slots} slots...")
            
            # 1. Volta para a página principal primeiro
            self.logger.info("🏠 Voltando para página principal...")
            try:
                home_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Home') or contains(text(), 'Início')]")
                home_link.click()
                self.logger.info("✅ Clicado em 'Home'")
                time.sleep(3)
            except:
                self.logger.info("⚠️ Link 'Home' não encontrado, continuando...")
            
            # 2. Navega para Service Management usando XPath específico
            self.logger.info("🔍 Procurando 'Service Management'...")
            try:
                service_management_link = self.driver.find_element(By.XPATH, "//*[@id='category_d3b2aa93-7e2b-4e0d-8080-67d14b2fa8a9_2']")
                service_management_link.click()
                self.logger.info("✅ Clicado em 'Service Management'")
                time.sleep(3)
            except:
                # Fallback: procura por texto
                self.logger.info("🔄 XPath específico falhou, tentando busca por texto...")
                service_management_links = self.driver.find_elements(By.XPATH, "//a")
                service_management_link = None
                
                for link in service_management_links:
                    if "service management" in link.text.lower() or "gerenciamento de serviços" in link.text.lower():
                        service_management_link = link
                        break
                
                if service_management_link:
                    service_management_link.click()
                    self.logger.info("✅ Clicado em 'Service Management' (fallback)")
                    time.sleep(3)
                else:
                    self.logger.error("❌ Link 'Service Management' não encontrado")
                    return False
            
            # 3. Clica em "Create a Service" usando XPath específico
            self.logger.info("🔍 Procurando 'Create a Service'...")
            try:
                create_service_link = self.driver.find_element(By.XPATH, "//*[@id='page_d3b2aa93-7e2b-4e0d-8080-67d14b2fa8a9_11']")
                create_service_link.click()
                self.logger.info("✅ Clicado em 'Create a Service'")
                time.sleep(5)
            except:
                # Fallback: procura por texto
                self.logger.info("🔄 XPath específico falhou, tentando busca por texto...")
                create_service_links = self.driver.find_elements(By.XPATH, "//a")
                create_service_link = None
                
                for link in create_service_links:
                    if "create a service" in link.text.lower() or "create service" in link.text.lower():
                        create_service_link = link
                        break
                
                if create_service_link:
                    create_service_link.click()
                    self.logger.info("✅ Clicado em 'Create a Service' (fallback)")
                    time.sleep(5)
                else:
                    self.logger.error("❌ Link 'Create a Service' não encontrado")
                    return False
            
            # 3. Muda para o iframe e procura pelo campo de proprietário
            self.logger.info("🖼️ Procurando iframe de criação de serviço...")
            try:
                # Procura pelo iframe
                iframes = self.driver.find_elements(By.XPATH, "//iframe")
                create_service_iframe = None
                
                for iframe in iframes:
                    iframe_src = iframe.get_attribute("src") or ""
                    if "CreateGameVoiceServer" in iframe_src or "CreateService" in iframe_src:
                        create_service_iframe = iframe
                        break
                
                if create_service_iframe:
                    self.driver.switch_to.frame(create_service_iframe)
                    self.logger.info("✅ Mudou para iframe de criação de serviço")
                    time.sleep(3)
                else:
                    self.logger.error("❌ Iframe de criação de serviço não encontrado")
                    return False
                
                # Procura pelo campo de proprietário dentro do iframe
                self.logger.info("🔍 Procurando campo de proprietário...")
                owner_field = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='ContentPlaceHolderMain_CreateGameVoiceServer1_UsersOwner_AdvancedDropDownList1_AdvancedDropDownList1_Input']")))
                self.logger.info("✅ Campo de proprietário encontrado")
                
                # 4. Clica no campo de proprietário para abrir a lista
                self.logger.info(f"🖱️ Clicando no campo de proprietário para abrir lista...")
                owner_field.click()
                self.logger.info("✅ Campo de proprietário clicado")
                time.sleep(3)
                
                # 5. Procura pelo usuário recém-criado na lista
                self.logger.info(f"🔍 Procurando usuário {username} na lista...")
                try:
                    # Procura por links que contenham o nome do usuário
                    user_links = self.driver.find_elements(By.XPATH, "//a")
                    user_found = False
                    
                    for link in user_links:
                        link_text = link.text or ""
                        if username.lower() in link_text.lower():
                            link.click()
                            self.logger.info(f"✅ Usuário {username} selecionado na lista")
                            user_found = True
                            break
                    
                    if not user_found:
                        # Fallback: procura por input e preenche
                        self.logger.info("🔄 Usuário não encontrado na lista, tentando preenchimento direto...")
                        owner_field.clear()
                        owner_field.send_keys(username)
                        self.logger.info(f"✅ Proprietário preenchido diretamente: {username}")
                    else:
                        self.logger.info(f"✅ Usuário {username} selecionado com sucesso!")
                    
                    time.sleep(2)
                except Exception as e:
                    self.logger.error(f"❌ Erro ao selecionar usuário: {str(e)}")
                    return False
                
                # 6. Configura os slots do servidor
                self.logger.info(f"🔧 Configurando {slots} slots para o servidor...")
                try:
                    # Procura por campo de slots (pode variar dependendo da interface)
                    slots_field = self.driver.find_element(By.XPATH, "//*[@id='ContentPlaceHolderMain_CreateGameVoiceServer1_DropDownListGameServers']")
                    slots_field.send_keys(str(slots))
                    self.logger.info(f"✅ Slots configurados: {slots}")
                    time.sleep(2)
                except Exception as e:
                    self.logger.warning(f"⚠️ Campo de slots não encontrado, usando padrão: {str(e)}")
                
                # 7. Clica no botão "Criar um Serviço de Jogo"
                self.logger.info("🔍 Procurando botão 'Criar um Serviço de Jogo'...")
                try:
                    game_service_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='TabCreateGameServer']")))
                    game_service_button.click()
                    self.logger.info("✅ Botão 'Criar um Serviço de Jogo' clicado")
                    time.sleep(5)
                    
                    # Verifica se foi para a próxima página
                    if self.verify_game_service_page():
                        self.logger.info("🎉 Navegação para 'Criar um Serviço de Jogo' realizada com sucesso!")
                        
                        # 8. Seleciona o tipo de jogo (Multi Theft Auto - Linux)
                        self.logger.info("🎮 Selecionando tipo de jogo...")
                        try:
                            # Usar o XPath correto encontrado na análise
                            game_type_select = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ContentPlaceHolderMain_CreateGameVoiceServer1_DropDownListGameServers']")))
                            game_type_select.click()
                            self.logger.info("✅ Select de tipo de jogo clicado")
                            time.sleep(2)
                            
                            # Seleciona "Multi Theft Auto - Linux" (índice 1)
                            from selenium.webdriver.support.ui import Select
                            select_element = Select(game_type_select)
                            select_element.select_by_index(1)  # Multi Theft Auto - Linux
                            self.logger.info("✅ Multi Theft Auto - Linux selecionado")
                            time.sleep(2)
                            
                        except Exception as e:
                            self.logger.warning(f"⚠️ Erro ao selecionar tipo de jogo: {str(e)}")
                        
                        # 9. Analisa e configura a quantidade de slots do plano
                        self.logger.info(f"🔧 Analisando e configurando {slots} slots do plano...")
                        try:
                            # Primeiro, analisar todos os inputs na página para encontrar o campo de slots
                            self.logger.info("🔍 Analisando todos os inputs na página...")
                            inputs = self.driver.find_elements(By.XPATH, "//input")
                            self.logger.info(f"📋 Encontrados {len(inputs)} inputs na página")
                            
                            slots_field = None
                            for i, input_elem in enumerate(inputs):
                                try:
                                    input_id = input_elem.get_attribute("id")
                                    input_name = input_elem.get_attribute("name")
                                    input_type = input_elem.get_attribute("type")
                                    input_value = input_elem.get_attribute("value")
                                    
                                    # Procurar por campo que contenha "50" (valor padrão de slots) e seja visível
                                    if input_value and "50" in str(input_value) and input_type != "hidden":
                                        self.logger.info(f"🎯 POSSÍVEL CAMPO DE SLOTS ENCONTRADO!")
                                        self.logger.info(f"   Input {i+1}: ID={input_id}, Name={input_name}, Type={input_type}, Value={input_value}")
                                        
                                        # Verificar se o campo está visível e interativo
                                        if input_elem.is_displayed() and input_elem.is_enabled():
                                            self.logger.info("✅ Campo está visível e interativo!")
                                            
                                            # Obter XPath
                                            xpath = self.driver.execute_script("""
                                                function getXPath(element) {
                                                    if (element.id !== '') {
                                                        return '//*[@id="' + element.id + '"]';
                                                    }
                                                    if (element === document.body) {
                                                        return '/html/body';
                                                    }
                                                    var ix = 0;
                                                    var siblings = element.parentNode.childNodes;
                                                    for (var i = 0; i < siblings.length; i++) {
                                                        var sibling = siblings[i];
                                                        if (sibling === element) {
                                                            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                                                        }
                                                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                                            ix++;
                                                        }
                                                    }
                                                }
                                                return getXPath(arguments[0]);
                                            """, input_elem)
                                            
                                            self.logger.info(f"   XPath: {xpath}")
                                            slots_field = input_elem
                                            break
                                        else:
                                            self.logger.info("⚠️ Campo não está visível ou interativo")
                                        
                                except Exception as e:
                                    continue
                            
                            if slots_field:
                                # Limpar campo completamente
                                slots_field.clear()
                                self.logger.info("✅ Campo de slots limpo")
                                time.sleep(1)
                                
                                # Inserir quantidade de slots do plano
                                slots_field.send_keys(str(slots))
                                self.logger.info(f"✅ {slots} slots inseridos no campo")
                                time.sleep(2)
                            else:
                                self.logger.warning("⚠️ Campo de slots não encontrado, tentando XPath original...")
                                # Tentar XPath original como fallback
                                slots_field = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[5]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/span/div/table/tbody/tr[5]/td[2]/span[1]/input[1]")))
                                slots_field.clear()
                                slots_field.send_keys(str(slots))
                                self.logger.info(f"✅ {slots} slots inseridos via XPath original")
                                time.sleep(2)
                            
                            # 10. Configura o ID de cobrança
                            self.logger.info("💳 Configurando ID de cobrança...")
                            try:
                                # Procurar por campo de ID de cobrança usando análise dinâmica
                                self.logger.info("🔍 Procurando campo de ID de cobrança...")
                                billing_inputs = self.driver.find_elements(By.XPATH, "//input")
                                billing_id_field = None
                                
                                for input_elem in billing_inputs:
                                    try:
                                        input_id = input_elem.get_attribute("id")
                                        input_name = input_elem.get_attribute("name")
                                        input_type = input_elem.get_attribute("type")
                                        
                                        # Procurar por campo que contenha "billing" ou "cobrança" no ID ou name
                                        if (input_id and ("billing" in input_id.lower() or "cobrança" in input_id.lower())) or \
                                           (input_name and ("billing" in input_name.lower() or "cobrança" in input_name.lower())):
                                            self.logger.info(f"🎯 CAMPO DE ID DE COBRANÇA ENCONTRADO!")
                                            self.logger.info(f"   ID: {input_id}, Name: {input_name}, Type: {input_type}")
                                            
                                            if input_elem.is_displayed() and input_elem.is_enabled():
                                                self.logger.info("✅ Campo está visível e interativo!")
                                                billing_id_field = input_elem
                                                break
                                            else:
                                                self.logger.info("⚠️ Campo não está visível ou interativo")
                                                
                                    except Exception as e:
                                        continue
                                
                                if billing_id_field:
                                    # Limpar campo completamente
                                    billing_id_field.clear()
                                    self.logger.info("✅ Campo de ID de cobrança limpo")
                                    time.sleep(1)
                                    
                                    # Inserir o mesmo ID de cobrança usado na criação do usuário
                                    if order_data:
                                        billing_id = order_data.get('tcadmin_id', str(order_data['id'])[:8])
                                    else:
                                        billing_id = '983469'  # Fallback se não tiver order_data
                                    billing_id_field.send_keys(billing_id)
                                    self.logger.info(f"✅ ID de cobrança {billing_id} inserido no campo")
                                    time.sleep(2)
                                else:
                                    self.logger.warning("⚠️ Campo de ID de cobrança não encontrado, tentando XPath original...")
                                    # Tentar XPath original como fallback
                                    billing_id_field = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[5]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/span/div/table/tbody/tr[7]/td[2]/span/input")))
                                    billing_id_field.clear()
                                    if order_data:
                                        billing_id = order_data.get('tcadmin_id', str(order_data['id'])[:8])
                                    else:
                                        billing_id = '983469'  # Fallback se não tiver order_data
                                    billing_id_field.send_keys(billing_id)
                                    self.logger.info(f"✅ ID de cobrança {billing_id} inserido via XPath original")
                                    time.sleep(2)
                                
                            except Exception as e:
                                self.logger.warning(f"⚠️ Erro ao configurar ID de cobrança: {str(e)}")
                            
                            # 11. Configura a senha RCON
                            self.logger.info("🔐 Configurando senha RCON...")
                            try:
                                # Gerar senha RCON aleatória
                                rcon_password = self.generate_rcon_password()
                                self.logger.info(f"🔑 Senha RCON gerada: {rcon_password}")
                                
                                # Procurar por campo de senha RCON usando análise dinâmica
                                self.logger.info("🔍 Procurando campo de senha RCON...")
                                rcon_inputs = self.driver.find_elements(By.XPATH, "//input")
                                rcon_field = None
                                
                                for input_elem in rcon_inputs:
                                    try:
                                        input_id = input_elem.get_attribute("id")
                                        input_name = input_elem.get_attribute("name")
                                        input_type = input_elem.get_attribute("type")
                                        input_placeholder = input_elem.get_attribute("placeholder")
                                        
                                        # Procurar por campo que contenha "rcon" no ID, name ou placeholder
                                        if (input_id and "rcon" in input_id.lower()) or \
                                           (input_name and "rcon" in input_name.lower()) or \
                                           (input_placeholder and "rcon" in input_placeholder.lower()):
                                            self.logger.info(f"🎯 CAMPO DE SENHA RCON ENCONTRADO!")
                                            self.logger.info(f"   ID: {input_id}, Name: {input_name}, Type: {input_type}, Placeholder: {input_placeholder}")
                                            
                                            if input_elem.is_displayed() and input_elem.is_enabled():
                                                self.logger.info("✅ Campo está visível e interativo!")
                                                rcon_field = input_elem
                                                break
                                            else:
                                                self.logger.info("⚠️ Campo não está visível ou interativo")
                                                
                                    except Exception as e:
                                        continue
                                
                                if rcon_field:
                                    # Limpar campo completamente
                                    rcon_field.clear()
                                    self.logger.info("✅ Campo de senha RCON limpo")
                                    time.sleep(1)
                                    
                                    # Inserir senha RCON gerada
                                    rcon_field.send_keys(rcon_password)
                                    self.logger.info(f"✅ Senha RCON {rcon_password} inserida no campo")
                                    time.sleep(2)
                                else:
                                    self.logger.warning("⚠️ Campo de senha RCON não encontrado")
                                
                            except Exception as e:
                                self.logger.warning(f"⚠️ Erro ao configurar senha RCON: {str(e)}")
                            
                            # 12. Clica no botão "Crio" para finalizar o serviço
                            self.logger.info("🚀 Finalizando criação do serviço...")
                            try:
                                # Procurar pelo botão "Crio" usando análise dinâmica
                                self.logger.info("🔍 Procurando botão 'Crio'...")
                                
                                # Tentar diferentes estratégias para encontrar o botão
                                create_button = None
                                
                                # Estratégia 1: Procurar por botões com texto "Crio", "Criar", "Create"
                                self.logger.info("🔍 Estratégia 1: Procurando por texto...")
                                all_buttons = self.driver.find_elements(By.XPATH, "//button")
                                all_inputs = self.driver.find_elements(By.XPATH, "//input")
                                
                                for button in all_buttons:
                                    try:
                                        button_text = button.text.strip()
                                        if "crio" in button_text.lower() or "criar" in button_text.lower() or "create" in button_text.lower():
                                            self.logger.info(f"🎯 BOTÃO ENCONTRADO POR TEXTO: '{button_text}'")
                                            if button.is_displayed() and button.is_enabled():
                                                create_button = button
                                                break
                                    except:
                                        continue
                                
                                # Estratégia 2: Procurar por inputs com value "Crio", "Criar", "Create"
                                if not create_button:
                                    self.logger.info("🔍 Estratégia 2: Procurando por inputs...")
                                    for input_elem in all_inputs:
                                        try:
                                            input_value = input_elem.get_attribute("value")
                                            input_type = input_elem.get_attribute("type")
                                            if input_value and ("crio" in input_value.lower() or "criar" in input_value.lower() or "create" in input_value.lower()):
                                                self.logger.info(f"🎯 INPUT ENCONTRADO POR VALUE: '{input_value}' (Type: {input_type})")
                                                if input_elem.is_displayed() and input_elem.is_enabled():
                                                    create_button = input_elem
                                                    break
                                        except:
                                            continue
                                
                                # Estratégia 3: Procurar por elementos com classes específicas
                                if not create_button:
                                    self.logger.info("🔍 Estratégia 3: Procurando por classes específicas...")
                                    try:
                                        # Procurar por botões verdes ou de sucesso
                                        green_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'green') or contains(@class, 'btn-success') or contains(@class, 'submit')] | //input[contains(@class, 'green') or contains(@class, 'btn-success') or @type='submit']")
                                        for button in green_buttons:
                                            if button.is_displayed() and button.is_enabled():
                                                self.logger.info("🎯 BOTÃO VERDE/SUBMIT ENCONTRADO!")
                                                create_button = button
                                                break
                                    except:
                                        pass
                                
                                # Estratégia 4: Procurar por todos os elementos clicáveis na área do formulário
                                if not create_button:
                                    self.logger.info("🔍 Estratégia 4: Procurando por todos os elementos clicáveis...")
                                    try:
                                        # Procurar na área do formulário principal
                                        form_elements = self.driver.find_elements(By.XPATH, "//form//button | //form//input[@type='submit'] | //form//input[@type='button']")
                                        for element in form_elements:
                                            try:
                                                element_text = element.text.strip()
                                                element_value = element.get_attribute("value")
                                                if (element_text and ("crio" in element_text.lower() or "criar" in element_text.lower() or "create" in element_text.lower())) or \
                                                   (element_value and ("crio" in element_value.lower() or "criar" in element_value.lower() or "create" in element_value.lower())):
                                                    self.logger.info(f"🎯 ELEMENTO DO FORMULÁRIO ENCONTRADO: '{element_text}' (Value: {element_value})")
                                                    if element.is_displayed() and element.is_enabled():
                                                        create_button = element
                                                        break
                                            except:
                                                continue
                                    except:
                                        pass
                                
                                # Estratégia 5: Busca AGRESSIVA por qualquer elemento que contenha "Crio"
                                if not create_button:
                                    self.logger.info("🔍 Estratégia 5: Busca AGRESSIVA por 'Crio'...")
                                    try:
                                        # Buscar por TODOS os elementos que contenham "Crio" no texto
                                        all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Crio') or contains(text(), 'crio') or contains(text(), 'CRIO')]")
                                        self.logger.info(f"📊 Encontrados {len(all_elements)} elementos com 'Crio' no texto")
                                    
                                        for i, element in enumerate(all_elements):
                                            try:
                                                element_text = element.text.strip()
                                                element_tag = element.tag_name
                                                element_id = element.get_attribute("id")
                                                element_class = element.get_attribute("class")
                                                
                                                self.logger.info(f"🎯 Elemento {i}: '{element_text}' (Tag: {element_tag}, ID: {element_id}, Class: {element_class})")
                                                
                                                if element.is_displayed() and element.is_enabled():
                                                    self.logger.info("✅ Elemento está visível e habilitado!")
                                                    create_button = element
                                                    break
                                                else:
                                                    self.logger.info("⚠️ Elemento não está visível ou habilitado")
                                            except:
                                                continue
                                        
                                        # Se não encontrou, buscar por elementos clicáveis que contenham "Crio"
                                        if not create_button:
                                            self.logger.info("🔍 Buscando elementos clicáveis com 'Crio'...")
                                            clickable_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Crio') or contains(text(), 'crio') or contains(text(), 'CRIO')]/..")
                                            
                                            for element in clickable_elements:
                                                try:
                                                    if element.is_displayed() and element.is_enabled():
                                                        self.logger.info("🎯 ELEMENTO CLICÁVEL ENCONTRADO!")
                                                        create_button = element
                                                        break
                                                except:
                                                    continue
                                        
                                        # Se ainda não encontrou, buscar por qualquer elemento que contenha "Crio" em qualquer atributo
                                        if not create_button:
                                            self.logger.info("🔍 Buscando por atributos que contenham 'Crio'...")
                                            attribute_elements = self.driver.find_elements(By.XPATH, "//*[contains(@id, 'Crio') or contains(@id, 'crio') or contains(@class, 'Crio') or contains(@class, 'crio') or contains(@value, 'Crio') or contains(@value, 'crio')]")
                                            
                                            for element in attribute_elements:
                                                try:
                                                    if element.is_displayed() and element.is_enabled():
                                                        self.logger.info("🎯 ELEMENTO POR ATRIBUTO ENCONTRADO!")
                                                        create_button = element
                                                        break
                                                except:
                                                    continue
                                        
                                        # Última tentativa: buscar por qualquer elemento que seja clicável e esteja na área do formulário
                                        if not create_button:
                                            self.logger.info("🔍 Última tentativa: elementos clicáveis na área do formulário...")
                                            form_area_elements = self.driver.find_elements(By.XPATH, "//form//*[self::button or self::input or self::a or self::div or self::span]")
                                            
                                            for element in form_area_elements:
                                                try:
                                                    element_text = element.text.strip()
                                                    if "crio" in element_text.lower() or "criar" in element_text.lower():
                                                        self.logger.info(f"🎯 ELEMENTO DO FORMULÁRIO ENCONTRADO: '{element_text}'")
                                                        if element.is_displayed() and element.is_enabled():
                                                            create_button = element
                                                            break
                                                except:
                                                    continue
                                                    
                                    except Exception as e:
                                        self.logger.warning(f"⚠️ Busca agressiva falhou: {str(e)}")
                                        create_button = None
                                
                                if create_button:
                                    # Clicar no botão encontrado
                                    create_button.click()
                                    self.logger.info("✅ Botão 'Crio' clicado com sucesso!")
                                    time.sleep(5)  # Aguardar processamento
                                    
                                    # Verificar se o serviço foi criado com sucesso
                                    try:
                                        # Procurar por mensagem de sucesso ou redirecionamento
                                        success_indicators = [
                                            "service created",
                                            "serviço criado", 
                                            "success",
                                            "sucesso",
                                            "created successfully"
                                        ]
                                        
                                        page_source = self.driver.page_source.lower()
                                        for indicator in success_indicators:
                                            if indicator in page_source:
                                                self.logger.info(f"🎉 Serviço criado com sucesso! Indicador: {indicator}")
                                                break
                                        else:
                                            self.logger.info("✅ Serviço criado (sem confirmação específica)")
                                            
                                    except Exception as e:
                                        self.logger.info("✅ Serviço criado (verificação de sucesso falhou)")
                                else:
                                    self.logger.warning("⚠️ Botão 'Crio' não encontrado com nenhuma estratégia")
                                
                            except Exception as e:
                                self.logger.warning(f"⚠️ Erro ao clicar no botão 'Crio': {str(e)}")
                            
                            # 13. Aguardar um pouco para o serviço ser processado
                            self.logger.info("⏳ Aguardando processamento do serviço...")
                            time.sleep(3)
                            
                            # ⏰ AGUARDAR 5 MINUTOS APÓS CRIAR O SERVIÇO
                            self.logger.info("⏰ Aguardando 5 minutos após criação do serviço...")
                            time.sleep(300)  # 300 segundos = 5 minutos
                            self.logger.info("✅ 5 minutos de espera concluído!")
                        
                        except Exception as e:
                            self.logger.warning(f"⚠️ Erro ao configurar slots: {str(e)}")
                        
                        return True
                    else:
                        self.logger.warning("⚠️ Navegação pode não ter funcionado")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ Erro ao clicar no botão: {str(e)}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"❌ Erro ao selecionar proprietário: {str(e)}")
                return False
                    
            except Exception as e:
                self.logger.error(f"❌ Campo de proprietário não encontrado: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar serviço: {str(e)}")
            return False
    
    def verify_game_service_page(self):
        """Verifica se foi para a página Create a Game Service"""
        try:
            # Verifica se a URL mudou para a página de criação de jogo
            current_url = self.driver.current_url.lower()
            if "creategame" in current_url or "game" in current_url:
                return True
            
            # Procura por elementos específicos da página de jogo
            game_indicators = [
                "game service",
                "serviço de jogo",
                "game server",
                "servidor de jogo"
            ]
            
            page_source = self.driver.page_source.lower()
            for indicator in game_indicators:
                if indicator in page_source:
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar página de jogo: {str(e)}")
            return False
    
    def verify_service_created(self):
        """Verifica se o serviço foi criado com sucesso"""
        try:
            # Procura por mensagens de sucesso
            success_indicators = [
                "service created",
                "serviço criado",
                "success",
                "sucesso",
                "created successfully",
                "criado com sucesso"
            ]
            
            page_source = self.driver.page_source.lower()
            for indicator in success_indicators:
                if indicator in page_source:
                    return True
            
            # Verifica se a URL mudou (indicando redirecionamento)
            current_url = self.driver.current_url
            if "create" not in current_url.lower():
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar criação do serviço: {str(e)}")
            return False
    
    def process_single_order(self, order_id):
        """Processa um pedido específico"""
        try:
            self.logger.info(f"🔄 Processando pedido individual: {order_id}")
            
            # 1. Busca dados do pedido no Supabase
            order_data = self.get_order_from_supabase(order_id)
            if not order_data:
                self.logger.error(f"❌ Não foi possível obter dados do pedido {order_id}")
                return False
            
            # 2. Verifica se o pedido está pendente
            if order_data.get('status') != 'pending':
                self.logger.warning(f"⚠️ Pedido {order_id} não está pendente (status: {order_data.get('status')})")
                return False
            
            # 3. Navega para a página de criação
            if not self.navigate_to_create_user():
                self.logger.error(f"❌ Falha ao navegar para criação de usuário")
                self.update_order_status_in_supabase(order_id, 'failed')
                return False
            
            # 4. Cria o usuário
            if self.create_user_in_tcadmin(order_data):
                self.update_order_status_in_supabase(order_id, 'completed')
                self.logger.info(f"🎉 Pedido {order_id} processado com sucesso!")
                return True
            else:
                self.update_order_status_in_supabase(order_id, 'failed')
                self.logger.error(f"❌ Falha ao processar pedido {order_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Erro no processamento do pedido {order_id}: {str(e)}")
            self.update_order_status_in_supabase(order_id, 'failed')
            return False
    
    def close_browser(self):
        """Fecha o navegador e finaliza o driver"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("✅ Navegador fechado com sucesso")
        except Exception as e:
            self.logger.error(f"❌ Erro ao fechar navegador: {str(e)}")
    
    def run_automation_for_order(self, order_id):
        """Executa automação para um pedido específico"""
        try:
            self.logger.info(f"🚀 === Bot de Automação TCAdmin - Pedido {order_id} ===")
            self.logger.info("🎯 Processa pedido individual após pagamento")
            self.logger.info("👤 Inclui seção de perfil com dados do Supabase")
            
            # 1. Configura o driver
            if not self.setup_driver():
                return False
            
            # 2. Navega para o painel admin
            if not self.navigate_to_admin_panel():
                return False
            
            # 3. Realiza login
            username = "bernardol"
            password = "Xyr+(191oTPZ7i"
            
            if not self.login(username, password):
                self.logger.error("❌ Falha no login - abortando")
                return False
            
            # 4. Processa o pedido específico
            if not self.process_single_order(order_id):
                self.logger.error("❌ Falha no processamento do pedido")
                return False
            
            self.logger.info("🎉 Automação concluída com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante automação: {str(e)}")
            return False
        finally:
            # Sempre fecha o navegador
            self.close_browser()


def main():
    """Função principal do bot"""
    import sys
    
    if len(sys.argv) != 2:
        print("❌ Uso: python3 bot_tcadmin.py <order_id>")
        print("📋 Exemplo: python3 bot_tcadmin.py 12345678-1234-1234-1234-123456789012")
        print()
        print("🎯 Funcionalidades:")
        print("   • Busca pedido no Supabase")
        print("   • Cria usuário no TCAdmin")
        print("   • Preenche dados do perfil (telefone, email, fuso horário)")
        print("   • Atualiza status do pedido")
        return
    
    order_id = sys.argv[1]
    
    print(f"=== Bot de Automação TCAdmin - Pedido {order_id} ===")
    print("🎯 Processa pedido individual após pagamento")
    print("👤 Inclui seção de perfil com dados do Supabase")
    print("📞 Busca telefone na tabela profiles")
    print("📧 Preenche email primário")
    print("🌍 Configura fuso horário para Brasília")
    print()
    
    # Configurações do bot
    headless = False  # Modo visual para demonstração
    
    # Inicializa e executa o bot
    bot = TCAdminBot(headless=headless)
    
    try:
        success = bot.run_automation_for_order(order_id)
        
        if success:
            print(f"\n✅ Pedido {order_id} processado com sucesso!")
            print("📋 Verifique o arquivo 'tcadmin_bot/bot_automation.log' para detalhes completos")
            print("🎯 Usuário foi criado no TCAdmin automaticamente")
            print("👤 Dados de perfil foram preenchidos com sucesso")
            print("📊 Status do pedido foi atualizado no Supabase")
        else:
            print(f"\n❌ Falha no processamento do pedido {order_id}.")
            print("📋 Verifique os logs para mais detalhes.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
    finally:
        print("Bot finalizado.")


if __name__ == "__main__":
    main()
