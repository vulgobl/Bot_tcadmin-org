#!/usr/bin/env python3
"""
Bot TCAdmin Simplificado - Sem Sistema Anti-Lag
Processa pedidos individuais quando chamado via webhook
Baseado no bot original que já funciona
"""

import time
import logging
import random
import string
import secrets
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import requests
import json

class TCAdminBotSimple:
    def __init__(self, headless=False):
        """Inicializa o bot simplificado"""
        self.driver = None
        self.wait = None
        self.headless = headless
        self.setup_logging()

        # Configurações do Supabase
        self.supabase_url = "https://gxvcovuwtbpkvzqdbcbr.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd4dmNvdnV3dGJwa3Z6cWRiY2JyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODIwNTQzOCwiZXhwIjoyMDYzNzgxNDM4fQ.Yw61sbaz1UsSeTgou9yiwjRMOug4mtePzbVTeBr5lQY"

    def setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_simple.log'),
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
                self.logger.info("🖥️ Modo VISUAL ativado - você verá o navegador")

            # Configurações otimizadas
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            if self.headless:
                chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

            # Para modo visual, maximizar janela
            if not self.headless:
                chrome_options.add_argument('--start-maximized')

            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)

            self.logger.info("Driver do Chrome inicializado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar o driver: {str(e)}")
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
                data = response.json()
                if data and len(data) > 0:
                    order = data[0]
                    self.logger.info(f"✅ Pedido encontrado: {order['id']}")
                    return order
                else:
                    self.logger.error(f"❌ Pedido {order_id} não encontrado")
                    return None
            else:
                self.logger.error(f"❌ Erro na API do Supabase: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar pedido: {str(e)}")
            return None

    def get_user_from_supabase(self, user_id):
        """Busca dados do usuário no Supabase"""
        try:
            self.logger.info(f"👤 Buscando usuário {user_id} no Supabase...")

            url = f"{self.supabase_url}/rest/v1/profiles"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }

            params = {
                'id': f'eq.{user_id}',
                'select': 'id,email,full_name,phone'
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    user = data[0]
                    self.logger.info(f"✅ Usuário encontrado: {user['email']}")
                    return user
                else:
                    self.logger.error(f"❌ Usuário {user_id} não encontrado")
                    return None
            else:
                self.logger.error(f"❌ Erro na API do Supabase: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar usuário: {str(e)}")
            return None

    def get_plan_from_supabase(self, plan_id):
        """Busca dados do plano no Supabase"""
        try:
            self.logger.info(f"📋 Buscando plano {plan_id} no Supabase...")

            url = f"{self.supabase_url}/rest/v1/plans"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }

            params = {
                'id': f'eq.{plan_id}',
                'select': 'id,name,price,player_slots'
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    plan = data[0]
                    self.logger.info(f"✅ Plano encontrado: {plan['name']}")
                    return plan
                else:
                    self.logger.error(f"❌ Plano {plan_id} não encontrado")
                    return None
            else:
                self.logger.error(f"❌ Erro na API do Supabase: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar plano: {str(e)}")
            return None

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

    def login_tcadmin(self):
        """Faz login no TCAdmin - usando o fluxo que já funciona"""
        try:
            self.logger.info("🔐 Fazendo login no TCAdmin...")
            print("🖥️ Abrindo TCAdmin no navegador...")
            
            # Navega para o TCAdmin primeiro
            if not self.navigate_to_admin_panel():
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
            username_field.send_keys("bernardol")
            self.logger.info("✅ Usuário inserido")
            print("✅ Usuário inserido")
            
            password_field.clear()
            password_field.send_keys("Xyr+(191oTPZ7i")
            self.logger.info("✅ Senha inserida")
            print("✅ Senha inserida")
            
            # Clica no botão de login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            self.logger.info("✅ Botão de login clicado")
            print("✅ Botão de login clicado")
            
            # Aguarda o redirecionamento
            time.sleep(8)
            
            # Verifica se o login foi bem-sucedido
            if self.is_logged_in():
                self.logger.info("🎉 Login realizado com sucesso!")
                print("🎉 Login realizado com sucesso!")
                return True
            else:
                self.logger.warning("⚠️ Falha no login")
                print("⚠️ Falha no login")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro durante o login: {str(e)}")
            print(f"❌ Erro durante o login: {str(e)}")
            return False

    def is_logged_in(self):
        """Verifica se o usuário está logado"""
        try:
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
            print("🖱️ Navegando para User Management → Create a User...")
            
            # 1. Clica em "User Management"
            self.logger.info("🔍 Procurando 'User Management'...")
            print("🔍 Procurando 'User Management'...")
            
            # Tenta diferentes estratégias para encontrar o link
            user_management_link = None
            
            # Estratégia 1: Busca por texto exato
            try:
                user_management_link = self.driver.find_element(By.LINK_TEXT, "User Management")
                self.logger.info("✅ Encontrado por LINK_TEXT")
                print("✅ Encontrado por LINK_TEXT")
            except:
                pass
            
            # Estratégia 2: Busca por texto parcial
            if not user_management_link:
                try:
                    user_management_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "User Management")
                    self.logger.info("✅ Encontrado por PARTIAL_LINK_TEXT")
                    print("✅ Encontrado por PARTIAL_LINK_TEXT")
                except:
                    pass
            
            # Estratégia 3: Busca por XPath com texto
            if not user_management_link:
                try:
                    user_management_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'User Management')]")
                    self.logger.info("✅ Encontrado por XPath")
                    print("✅ Encontrado por XPath")
                except:
                    pass
            
            # Estratégia 4: Busca em todos os links
            if not user_management_link:
                user_management_links = self.driver.find_elements(By.XPATH, "//a")
                for link in user_management_links:
                    if "user management" in link.text.lower():
                        user_management_link = link
                        self.logger.info("✅ Encontrado por busca em todos os links")
                        print("✅ Encontrado por busca em todos os links")
                        break
            
            if user_management_link:
                user_management_link.click()
                self.logger.info("✅ Clicado em 'User Management'")
                print("✅ Clicado em 'User Management'")
                time.sleep(3)
            else:
                self.logger.error("❌ Link 'User Management' não encontrado")
                print("❌ Link 'User Management' não encontrado")
                return False
            
            # 2. Clica em "Create a User"
            self.logger.info("🔍 Procurando 'Create a User'...")
            print("🔍 Procurando 'Create a User'...")
            
            # Tenta diferentes estratégias para encontrar o link
            create_user_link = None
            
            # Estratégia 1: Busca por texto exato
            try:
                create_user_link = self.driver.find_element(By.LINK_TEXT, "Create a User")
                self.logger.info("✅ Encontrado por LINK_TEXT")
                print("✅ Encontrado por LINK_TEXT")
            except:
                pass
            
            # Estratégia 2: Busca por texto parcial
            if not create_user_link:
                try:
                    create_user_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Create a User")
                    self.logger.info("✅ Encontrado por PARTIAL_LINK_TEXT")
                    print("✅ Encontrado por PARTIAL_LINK_TEXT")
                except:
                    pass
            
            # Estratégia 3: Busca por XPath com texto
            if not create_user_link:
                try:
                    create_user_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Create a User')]")
                    self.logger.info("✅ Encontrado por XPath")
                    print("✅ Encontrado por XPath")
                except:
                    pass
            
            # Estratégia 4: Busca em todos os links
            if not create_user_link:
                create_user_links = self.driver.find_elements(By.XPATH, "//a")
                for link in create_user_links:
                    if "create a user" in link.text.lower():
                        create_user_link = link
                        self.logger.info("✅ Encontrado por busca em todos os links")
                        print("✅ Encontrado por busca em todos os links")
                        break
            
            if create_user_link:
                create_user_link.click()
                self.logger.info("✅ Clicado em 'Create a User'")
                print("✅ Clicado em 'Create a User'")
                time.sleep(10)  # Aguarda carregar
            else:
                self.logger.error("❌ Link 'Create a User' não encontrado")
                print("❌ Link 'Create a User' não encontrado")
                return False
            
            self.logger.info(f"📄 Página atual: {self.driver.title}")
            self.logger.info(f"🔗 URL atual: {self.driver.current_url}")
            print(f"📄 Página atual: {self.driver.title}")
            print(f"🔗 URL atual: {self.driver.current_url}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao navegar para criação de usuário: {str(e)}")
            print(f"❌ Erro ao navegar para criação de usuário: {str(e)}")
            return False

    def switch_to_create_user_iframe(self):
        """Muda para o iframe de criação de usuário"""
        try:
            self.logger.info("🖼️ Procurando iframe de criação de usuário...")
            print("🖼️ Procurando iframe de criação de usuário...")
            
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
                print("✅ Mudou para iframe de criação de usuário")
                time.sleep(3)
                return True
            else:
                self.logger.error("❌ Iframe de criação de usuário não encontrado")
                print("❌ Iframe de criação de usuário não encontrado")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao mudar para iframe: {str(e)}")
            print(f"❌ Erro ao mudar para iframe: {str(e)}")
            return False

    def generate_random_password(self, length=12):
        """Gera senha aleatória"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(characters) for _ in range(length))

    def create_user_in_tcadmin(self, user_data, order_data, plan_data):
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
            print(f"👤 Criando usuário para pedido {order_data['id']}:")
            print(f"   📝 Nome: {username}")
            print(f"   💳 Billing ID: {billing_id}")
            print(f"   🔐 Senha: {password}")
            
            # Navega para a página de criação de usuário primeiro
            if not self.navigate_to_create_user():
                self.logger.error("❌ Falha ao navegar para página de criação de usuário")
                print("❌ Falha ao navegar para página de criação de usuário")
                return False
            
            # Muda para o iframe
            if not self.switch_to_create_user_iframe():
                return False
            
            # === ETAPA 1: DADOS INICIAIS ===
            self.logger.info("📋 Preenchendo dados iniciais...")
            print("📋 Preenchendo dados iniciais...")
            
            # Preenche campo de username
            username_field = self.wait.until(EC.presence_of_element_located((
                By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxLabelUserNameTextBox']"
            )))
            username_field.clear()
            username_field.send_keys(username)
            self.logger.info("✅ Username preenchido")
            print("✅ Username preenchido")
            
            # Preenche campo de password
            password_field = self.driver.find_element(
                By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxPassword']"
            )
            password_field.clear()
            password_field.send_keys(password)
            self.logger.info("✅ Password preenchido")
            print("✅ Password preenchido")
            
            # Preenche campo de billing ID
            billing_field = self.driver.find_element(
                By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxBillingId']"
            )
            billing_field.clear()
            billing_field.send_keys(billing_id)
            self.logger.info("✅ Billing ID preenchido")
            print("✅ Billing ID preenchido")
            
            # === ETAPA 2: SEÇÃO PERFIL ===
            self.logger.info("👤 Acessando seção de perfil...")
            print("👤 Acessando seção de perfil...")
            
            # Procura pelo botão "Perfil" ou "Profile"
            try:
                profile_button = self.driver.find_element(By.XPATH, "//*[@id='TabProfile']")
                profile_button.click()
                self.logger.info("✅ Clicado em 'Perfil'")
                print("✅ Clicado em 'Perfil'")
                time.sleep(3)
                
                # Preenche celular (campo celular, não telefone residencial)
                try:
                    phone_field = self.driver.find_element(By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxMobilePhoneTextBox']")
                    phone_field.clear()
                    phone_field.send_keys(user_data.get('phone', ''))
                    self.logger.info(f"✅ Celular preenchido: {user_data.get('phone', '')}")
                    print(f"✅ Celular preenchido: {user_data.get('phone', '')}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao preencher celular: {str(e)}")
                
                # Preenche email primário
                try:
                    email_field = self.driver.find_element(By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TextBoxPrimaryEmailTextBox']")
                    email_field.clear()
                    email_field.send_keys(user_data.get('email', ''))
                    self.logger.info(f"✅ Email primário preenchido: {user_data.get('email', '')}")
                    print(f"✅ Email primário preenchido: {user_data.get('email', '')}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao preencher email primário: {str(e)}")
                
                # Configura fuso horário para Brasília
                try:
                    timezone_field = self.driver.find_element(By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_DropDownListTimeZone']")
                    timezone_field.send_keys("America/Sao_Paulo")
                    self.logger.info("✅ Fuso horário configurado para Brasília")
                    print("✅ Fuso horário configurado para Brasília")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao configurar fuso horário: {str(e)}")
                
                self.logger.info("✅ Seção de perfil preenchida com sucesso")
                print("✅ Seção de perfil preenchida com sucesso")
            except:
                self.logger.warning("⚠️ Botão 'Perfil' não encontrado, continuando sem dados de perfil")
                print("⚠️ Botão 'Perfil' não encontrado, continuando sem dados de perfil")
            
            # === ETAPA 3: CLICAR EM SALVE ===
            try:
                self.logger.info("💾 Procurando botão 'Salve'...")
                print("💾 Procurando botão 'Salve'...")
                
                # Procura pelo botão "Salve" ou "Save"
                try:
                    save_button = self.driver.find_element(By.XPATH, "//*[@id='ContentPlaceHolderMain_UserDetails1_TabToolBar1_RadToolBar1']/div[1]/div[1]/div[1]/ul[1]/li[1]/a[1]")
                    save_button.click()
                    self.logger.info("✅ Botão 'Salve' clicado com sucesso!")
                    print("✅ Botão 'Salve' clicado com sucesso!")
                    time.sleep(5)
                    
                    if self.verify_user_created(username):
                        self.logger.info(f"🎉 Usuário {username} criado com sucesso!")
                        print(f"🎉 Usuário {username} criado com sucesso!")
                        return True
                    else:
                        self.logger.warning(f"⚠️ Usuário {username} pode não ter sido criado")
                        print(f"⚠️ Usuário {username} pode não ter sido criado")
                        return False
                except:
                    self.logger.info("🔄 Tentando submit via JavaScript...")
                    print("🔄 Tentando submit via JavaScript...")
                    self.driver.execute_script("document.forms[0].submit();")
                    self.logger.info("✅ Submit via JavaScript executado")
                    print("✅ Submit via JavaScript executado")
                    time.sleep(5)
                    
                    if self.verify_user_created(username):
                        self.logger.info(f"🎉 Usuário {username} criado com sucesso!")
                        print(f"🎉 Usuário {username} criado com sucesso!")
                        return True
                    else:
                        self.logger.warning(f"⚠️ Usuário {username} pode não ter sido criado")
                        print(f"⚠️ Usuário {username} pode não ter sido criado")
                        return False
                    
            except Exception as e:
                self.logger.error(f"❌ Erro ao clicar em Salve: {str(e)}")
                print(f"❌ Erro ao clicar em Salve: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar usuário: {str(e)}")
            print(f"❌ Erro ao criar usuário: {str(e)}")
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

    def update_order_status(self, order_id, status):
        """Atualiza o status do pedido no Supabase"""
        try:
            self.logger.info(f"🔄 Atualizando status do pedido {order_id} para {status}...")
            print(f"🔄 Atualizando status do pedido {order_id} para {status}...")

            url = f"{self.supabase_url}/rest/v1/orders"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation' # Retorna o registro atualizado
            }

            payload = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }

            response = requests.patch(url, headers=headers, params={'id': f'eq.{order_id}'}, data=json.dumps(payload))

            if response.status_code == 200:
                self.logger.info(f"✅ Status atualizado para {status}")
                print(f"✅ Status atualizado para {status}")
                return True
            else:
                self.logger.error(f"❌ Erro ao atualizar status: {response.status_code} - {response.text}")
                print(f"❌ Erro ao atualizar status: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar status: {str(e)}")
            print(f"❌ Erro ao atualizar status: {str(e)}")
            return False

    def process_order(self, order_id):
        """Processa um pedido completo"""
        try:
            self.logger.info(f"🚀 ===== PROCESSANDO PEDIDO {order_id} =====")
            print(f"🚀 ===== PROCESSANDO PEDIDO {order_id} =====")

            # 1. Buscar dados do pedido
            print("🔍 Buscando dados do pedido...")
            order_data = self.get_order_from_supabase(order_id)
            if not order_data:
                self.logger.error("❌ Pedido não encontrado")
                print("❌ Pedido não encontrado")
                return False

            # 2. Buscar dados do usuário
            print("👤 Buscando dados do usuário...")
            user_data = self.get_user_from_supabase(order_data['user_id'])
            if not user_data:
                self.logger.error("❌ Usuário não encontrado")
                print("❌ Usuário não encontrado")
                return False

            # 3. Buscar dados do plano
            print("📋 Buscando dados do plano...")
            plan_data = self.get_plan_from_supabase(order_data['plan_id'])
            if not plan_data:
                self.logger.error("❌ Plano não encontrado")
                print("❌ Plano não encontrado")
                return False

            # 4. Atualizar status para processing
            print("🔄 Atualizando status para 'processing'...")
            self.update_order_status(order_id, 'processing')

            # 5. Inicializar driver
            print("🖥️ Inicializando navegador...")
            if not self.setup_driver():
                self.logger.error("❌ Falha ao inicializar driver")
                print("❌ Falha ao inicializar driver")
                return False

            # 6. Fazer login no TCAdmin
            print("🔐 Fazendo login no TCAdmin...")
            if not self.login_tcadmin():
                self.logger.error("❌ Falha no login TCAdmin")
                print("❌ Falha no login TCAdmin")
                return False

            # 7. Criar usuário
            print("👤 Criando usuário no TCAdmin...")
            if not self.create_user_in_tcadmin(user_data, order_data, plan_data):
                self.logger.error("❌ Falha ao criar usuário")
                print("❌ Falha ao criar usuário")
                return False

            # 8. Atualizar status para completed
            print("✅ Atualizando status para 'completed'...")
            self.update_order_status(order_id, 'completed')

            self.logger.info(f"✅ Pedido {order_id} processado com sucesso!")
            print(f"✅ Pedido {order_id} processado com sucesso!")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao processar pedido: {str(e)}")
            print(f"❌ Erro ao processar pedido: {str(e)}")
            # Atualizar status para failed
            self.update_order_status(order_id, 'failed')
            print(f"❌ Falha ao processar pedido {order_id}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("🔚 Driver fechado")
                print("🔚 Driver fechado")

if __name__ == "__main__":
    """Função principal"""
    # Verificar se foi passado um order_id
    if len(sys.argv) < 2:
        print("❌ Uso: python3 bot_tcadmin_simple.py <order_id>")
        sys.exit(1)

    order_id = sys.argv[1]

    # Criar e executar bot com interface visual
    bot = TCAdminBotSimple(headless=False)
    success = bot.process_order(order_id)

    if success:
        print(f"✅ Pedido {order_id} processado com sucesso!")
        sys.exit(0)
    else:
        print(f"❌ Falha ao processar pedido {order_id}")
        sys.exit(1)