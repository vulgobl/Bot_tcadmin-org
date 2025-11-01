#!/usr/bin/env python3
"""
Sistema Anti-Lag TCAdmin - Versão Otimizada
Sistema inteligente que se adapta à demanda e protege contra sobrecarga

CONFIGURAÇÕES:
- Horário Comercial: 9h às 18h
- Intervalos (Comercial): IDLE=5min, ACTIVE=1min, BUSY=30s
- Intervalos (Fora): IDLE=10min, ACTIVE=5min, BUSY=1min
- Proteção: 100 requisições/hora
- Modo: Visual (navegador visível)

COMO USAR:
1. cd /home/codexbl/test/cloudbase-hosting-site/tcadmin_bot
2. ./run.sh
3. O sistema funciona automaticamente!

FUNCIONAMENTO:
- Detecta pedidos pagos automaticamente
- Processa tudo automaticamente
- Cria usuários e serviços no TCAdmin
- Protege contra sobrecarga
"""

import time
import logging
import threading
import os
import sys
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Adiciona o diretório pai ao path para importar o módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    # Quando o projeto completo está em um nível acima (monorepo)
    from tcadmin_bot.bot_tcadmin import TCAdminBot
except ModuleNotFoundError:
    # Quando roda standalone dentro do diretório tcadmin_bot (Railway)
    from bot_tcadmin import TCAdminBot

class AntiLagBot:
    def __init__(self):
        """Inicializa o sistema anti-lag"""
        
        # ===========================================
        # CONFIGURAÇÕES DO SUPABASE
        # ===========================================
        # Carrega variáveis de ambiente
        from dotenv import load_dotenv
        load_dotenv('variables.env')
        
        # URL do seu projeto Supabase (carregada do variables.env)
        self.supabase_url = os.getenv('SUPABASE_URL', "https://gxvcovuwtbpkvzqdbcbr.supabase.co")
        
        # Service Role Key do Supabase (carregada do variables.env)
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd4dmNvdnV3dGJwa3Z6cWRiY2JyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODIwNTQzOCwiZXhwIjoyMDYzNzgxNDM4fQ.8f838023-ab78-4468-ad2b-b830894fb156")
        
        # ===========================================
        # CONFIGURAÇÕES DO TCADMIN
        # ===========================================
        # URL do seu TCAdmin (carregada do variables.env)
        self.tcadmin_url = os.getenv('TCADMIN_URL', "https://tcadmin.xyz/")
        
        # Usuário do TCAdmin (carregado do variables.env)
        self.tcadmin_username = os.getenv('TCADMIN_USERNAME', "bernardol")
        
        # Senha do TCAdmin (carregada do variables.env)
        self.tcadmin_password = os.getenv('TCADMIN_PASSWORD', "Xyr+(191oTPZ7i")
        
        # ===========================================
        # ESTADOS DO SISTEMA (não mude)
        # ===========================================
        self.state = "idle"  # idle, active, busy, overload
        self.consecutive_empty_checks = 0
        self.last_activity = None
        self.bot_instance = None
        
        # ===========================================
        # PROTEÇÃO CONTRA SOBRECARGA
        # ===========================================
        self.request_count = 0
        self.last_reset = datetime.now()
        # Máximo de requisições por hora (pode ajustar se necessário)
        self.max_requests_per_hour = 100
        
        # ===========================================
        # CONFIGURAÇÕES DE HORÁRIO COMERCIAL
        # ===========================================
        # Horário comercial (9h às 18h) - pode ajustar se necessário
        self.business_hours = {"start": 9, "end": 18}
        
        # ===========================================
        # CONFIGURAÇÕES DE INTERVALOS (em segundos)
        # ===========================================
        # Intervalos durante horário comercial (9h-18h)
        self.intervals = {
            "business_hours": {
                "idle": 30,     # 5 minutos quando parado (pode ajustar)
                "active": 60,     # 1 minuto quando ativo (pode ajustar)
                "busy": 30        # 30 segundos quando processando (pode ajustar)
            },
            # Intervalos fora do horário comercial (18h-9h)
            "off_hours": {
                "idle": 30,     # 10 minutos quando parado (pode ajustar)
                "active": 30,   # 5 minutos quando ativo (pode ajustar)
                "busy": 30       # 1 minuto quando processando (pode ajustar)
            }
        }
        
        # ===========================================
        # CONFIGURAÇÃO DE LOGS
        # ===========================================
        # Configuração de logging (não mude)
        logging.basicConfig(
            level=logging.INFO,  # Nível de log (INFO, DEBUG, WARNING, ERROR)
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('anti_lag_bot.log', encoding='utf-8'),  # Arquivo de log
                logging.StreamHandler()  # Console
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🚀 Sistema Anti-Lag TCAdmin inicializado")
        self.logger.info("🛡️ Proteção contra sobrecarga ativada")
        self.logger.info("⏰ Intervalos inteligentes configurados")
    
    def is_business_hours(self) -> bool:
        """
        Verifica se está em horário comercial
        Retorna True se estiver entre 9h e 18h (configurável acima)
        """
        current_hour = datetime.now().hour
        return self.business_hours["start"] <= current_hour <= self.business_hours["end"]
    
    def get_interval_config(self) -> Dict[str, int]:
        """Retorna configuração de intervalos baseada no horário"""
        if self.is_business_hours():
            return self.intervals["business_hours"]
        return self.intervals["off_hours"]
    
    def can_make_request(self) -> bool:
        """
        Verifica se pode fazer nova requisição (proteção contra sobrecarga)
        Limite: 100 requisições por hora (configurável acima)
        """
        now = datetime.now()
        
        # Reset contador a cada hora
        if (now - self.last_reset).seconds >= 3600:
            self.request_count = 0
            self.last_reset = now
            self.logger.info("🔄 Contador de requisições resetado")
        
        # Verifica limite (configurável em max_requests_per_hour)
        if self.request_count >= self.max_requests_per_hour:
            self.logger.warning(f"⚠️ Limite de requisições atingido ({self.request_count}/{self.max_requests_per_hour})")
            return False
        
        return True
    
    def record_request(self):
        """Registra requisição feita"""
        self.request_count += 1
        self.logger.debug(f"📊 Requisições na última hora: {self.request_count}")
    
    def get_paid_orders_from_supabase(self) -> List[Dict]:
        """Busca pedidos com status 'paid' no Supabase"""
        try:
            self.logger.info("🔍 Verificando pedidos pagos no Supabase...")
            
            url = f"{self.supabase_url}/rest/v1/orders"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'status': 'eq.paid',
                'select': 'id,user_id,plan_id,status,price_at_order,currency_at_order,user_notes,server_name_preference,created_at,slots,tcadmin_id'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                orders = response.json()
                self.logger.info(f"📊 Encontrados {len(orders)} pedidos pagos")
                return orders
            else:
                self.logger.error(f"❌ Erro ao buscar pedidos: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar pedidos: {str(e)}")
            return []
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Busca perfil do usuário no Supabase"""
        try:
            self.logger.info(f"👤 Buscando perfil do usuário {user_id}...")
            
            url = f"{self.supabase_url}/rest/v1/profiles"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'id': f'eq.{user_id}',
                'select': 'phone,email,full_name'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                profiles = response.json()
                if profiles:
                    profile = profiles[0]
                    self.logger.info(f"✅ Perfil encontrado: {profile}")
                    return profile
                else:
                    self.logger.warning(f"⚠️ Perfil não encontrado para usuário {user_id}")
                    # Tenta buscar email direto do auth.users como fallback
                    return self.get_user_email_fallback(user_id)
            else:
                self.logger.error(f"❌ Erro ao buscar perfil: {response.status_code}")
                self.logger.error(f"❌ Response: {response.text[:200]}")
                # Tenta buscar email direto do auth.users como fallback
                return self.get_user_email_fallback(user_id)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar perfil: {str(e)}")
            # Tenta buscar email direto do auth.users como fallback
            return self.get_user_email_fallback(user_id)
    
    def get_user_email_fallback(self, user_id: str) -> Optional[Dict]:
        """Busca email direto do auth.users como fallback"""
        try:
            self.logger.info(f"🔄 Tentando buscar email do auth.users para {user_id}...")
            
            url = f"{self.supabase_url}/rest/v1/auth/users"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Tenta buscar via auth.admin API ou direto da tabela profiles com id
            # Como auth.users não é acessível via REST diretamente, tenta novamente profiles com id
            url = f"{self.supabase_url}/rest/v1/profiles"
            params = {
                'id': f'eq.{user_id}',
                'select': 'email,full_name,phone'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                profiles = response.json()
                if profiles and len(profiles) > 0:
                    profile = profiles[0]
                    email = profile.get('email', '')
                    if email:
                        self.logger.info(f"✅ Email encontrado no profiles via id: {email}")
                        return {'email': email, 'full_name': profile.get('full_name', 'Cliente'), 'phone': profile.get('phone', '')}
            
            self.logger.warning("⚠️ Email não encontrado no profiles via id")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar email do auth.users: {str(e)}")
            return None
    
    def get_plan_name(self, plan_id: str) -> str:
        """Busca nome do plano no Supabase"""
        try:
            if not plan_id:
                self.logger.warning("⚠️ plan_id não fornecido, usando nome padrão")
                return 'Host MTA/SAMP'
            
            self.logger.info(f"📋 Buscando nome do plano {plan_id}...")
            
            url = f"{self.supabase_url}/rest/v1/plans"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'id': f'eq.{plan_id}',
                'select': 'name'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                plans = response.json()
                if plans and len(plans) > 0:
                    plan = plans[0]
                    plan_name = plan.get('name', 'Host MTA/SAMP')
                    self.logger.info(f"✅ Nome do plano encontrado: {plan_name}")
                    return plan_name
            
            self.logger.warning(f"⚠️ Plano {plan_id} não encontrado, usando nome padrão")
            return 'Host MTA/SAMP'
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar nome do plano: {str(e)}")
            return 'Host MTA/SAMP'
    
    def update_order_status(self, order_id: str, status: str) -> bool:
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
                json=data,
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 204:
                self.logger.info(f"✅ Status do pedido {order_id} atualizado para {status}")
                return True
            else:
                self.logger.error(f"❌ Erro ao atualizar pedido: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar pedido: {str(e)}")
            return False
    
    def update_state(self, has_orders: bool):
        """Atualiza estado do sistema baseado na atividade"""
        if has_orders:
            self.state = "busy"
            self.consecutive_empty_checks = 0
            self.last_activity = datetime.now()
            self.logger.info("🎯 Estado: BUSY (processando pedidos)")
        else:
            self.consecutive_empty_checks += 1
            
            if self.consecutive_empty_checks == 1:
                self.state = "active"
                self.logger.info("🟡 Estado: ACTIVE (acabou de processar)")
            elif self.consecutive_empty_checks >= 3:
                self.state = "idle"
                self.logger.info("🟢 Estado: IDLE (sem atividade)")
            else:
                self.state = "active"
                self.logger.info("🟡 Estado: ACTIVE (aguardando)")
    
    def get_next_interval(self) -> int:
        """Retorna próximo intervalo baseado no estado e horário"""
        intervals = self.get_interval_config()
        
        if self.state == "overload":
            return 3600  # 1 hora se sobrecarregado
        
        interval = intervals.get(self.state, 300)
        
        # Log do intervalo
        if self.state == "idle":
            self.logger.info(f"😴 Nenhum pedido encontrado, aguardando {interval}s")
        elif self.state == "active":
            self.logger.info(f"🟡 Aguardando {interval}s (modo ativo)")
        elif self.state == "busy":
            self.logger.info(f"🔴 Processando pedidos, próxima verificação em {interval}s")
        
        return interval
    
    def process_single_order(self, order_data: Dict) -> bool:
        """
        Processa um pedido individual
        Esta função é chamada automaticamente quando encontra um pedido pago
        """
        order_id = order_data['id']
        self.logger.info(f"⚙️ Processando pedido {order_id}...")
        
        try:
            # ===========================================
            # INICIALIZAÇÃO DO BOT TCADMIN
            # ===========================================
            # Inicializa bot TCAdmin se necessário
            if not self.bot_instance:
                # Modo visual (headless=False) - navegador visível
                # Para modo invisível, mude para headless=True
                self.bot_instance = TCAdminBot(headless=True)  # Modo headless para produção
                self.logger.info("🤖 Bot TCAdmin inicializado")
            
            # ===========================================
            # VERIFICAÇÃO DE SESSÃO
            # ===========================================
            # Verifica se a sessão ainda está válida
            try:
                if self.bot_instance.driver and not self.bot_instance.is_logged_in():
                    self.logger.info("🔄 Sessão perdida, reinicializando...")
                    self.bot_instance.close_browser()
                    self.bot_instance = TCAdminBot(headless=True)
                    self.logger.info("🤖 Bot TCAdmin reinicializado")
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao verificar sessão: {str(e)}")
                self.logger.info("🔄 Reinicializando bot...")
                self.bot_instance = TCAdminBot(headless=True)
                self.logger.info("🤖 Bot TCAdmin reinicializado")
            
            # ===========================================
            # LOGIN NO TCADMIN
            # ===========================================
            # Verifica se está logado
            if not self.bot_instance.is_logged_in():
                self.logger.info("🔐 Fazendo login no TCAdmin...")
                if not self.bot_instance.login(self.tcadmin_username, self.tcadmin_password, self.tcadmin_url):
                    raise Exception("Falha no login do TCAdmin")
            
            # ===========================================
            # BUSCA DADOS DO USUÁRIO E PLANO
            # ===========================================
            # Busca perfil do usuário no Supabase
            user_profile = self.get_user_profile(order_data['user_id'])
            order_data['profile'] = user_profile
            
            # Busca nome do plano para o email
            plan_id = order_data.get('plan_id')
            plan_name = self.get_plan_name(plan_id) if plan_id else 'Host MTA/SAMP'
            order_data['plan_name'] = plan_name
            self.logger.info(f"📋 Plano do pedido: {plan_name}")
            
            # ===========================================
            # PROCESSAMENTO DO PEDIDO
            # ===========================================
            # Cria usuário e serviço no TCAdmin automaticamente
            success = self.bot_instance.create_user_in_tcadmin(order_data)
            
            if success:
                # Marca pedido como concluído no Supabase
                self.update_order_status(order_id, 'completed')
                self.logger.info(f"🎉 Pedido {order_id} processado com sucesso!")
                
                # ===========================================
                # CRIAÇÃO DE ASSINATURA AUTOMÁTICA
                # ===========================================
                # TODO: Implementar criação de assinatura se necessário
                # self.logger.info("💳 Criando assinatura automática...")
                # subscription_created = self.create_subscription(order_data)
                
                # NOTA: O navegador será fechado no loop principal após processar
                # Isso garante que tudo é fechado antes de processar próximo pedido
                return True
            else:
                # Marca pedido como falhou no Supabase
                self.update_order_status(order_id, 'failed')
                self.logger.error(f"❌ Falha ao processar pedido {order_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar pedido {order_id}: {str(e)}")
            # Marca pedido como falhou em caso de erro
            self.update_order_status(order_id, 'failed')
            
            # Garantir fechamento do navegador mesmo em erro
            try:
                if self.bot_instance and self.bot_instance.driver:
                    self.logger.info("🔄 Fechando navegador após erro...")
                    self.bot_instance.close_browser()
                    self.bot_instance = None
            except:
                pass
                
            return False
    
    def run_anti_lag_system(self):
        """
        Executa o sistema anti-lag principal
        IMPORTANTE: Processa apenas o pedido recebido via webhook e termina completamente
        NÃO busca pedidos diretamente no Supabase - só processa via webhook
        """
        self.logger.info("🚀 Iniciando Sistema Anti-Lag TCAdmin")
        self.logger.info("📌 MODO: Processa pedido via webhook e termina completamente")
        
        # Não usa loop infinito - processa pedido do webhook e termina
        try:
            # ===========================================
            # 1. VERIFICAR SE HÁ PEDIDO VIA WEBHOOK
            # ===========================================
            # Busca ORDER_ID e ORDER_DATA passados pelo webhook via variáveis de ambiente
            order_id = os.getenv('ORDER_ID', '')
            order_data_str = os.getenv('ORDER_DATA', '')
            
            if not order_id or not order_data_str:
                self.logger.info("📭 Nenhum pedido recebido via webhook. Finalizando execução.")
                return
            
            # Parse do JSON do pedido
            try:
                order_to_process = json.loads(order_data_str)
                self.logger.info(f"📥 Pedido recebido via webhook: {order_id}")
            except json.JSONDecodeError as e:
                self.logger.error(f"❌ Erro ao parsear ORDER_DATA do webhook: {str(e)}")
                return
            
            # ===========================================
            # 2. PROCESSAR APENAS ESTE PEDIDO
            # ===========================================
            try:
                # Processa APENAS o pedido recebido via webhook
                success = self.process_single_order(order_to_process)
                
                if success:
                    self.logger.info(f"✅ Pedido {order_id} processado com sucesso!")
                else:
                    self.logger.error(f"❌ Falha ao processar pedido {order_id}")
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao processar pedido {order_id}: {str(e)}")
            
            # ===========================================
            # SEMPRE: FECHAR TUDO após processar QUALQUER pedido
            # ===========================================
            finally:
                # GARANTIR que navegador SEMPRE é fechado após processar
                try:
                    if self.bot_instance and self.bot_instance.driver:
                        self.logger.info("🔄 Fechando navegador após processamento...")
                        self.bot_instance.close_browser()
                        self.bot_instance = None
                        self.logger.info("✅ Navegador fechado completamente")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao fechar navegador: {str(e)}")
                
                # SEMPRE TERMINAR após processar qualquer pedido
                self.logger.info("✅ Execução finalizada completamente. Aguardando próximo webhook.")
                return  # Termina SEMPRE
        
        except KeyboardInterrupt:
            # Usuário pressionou Ctrl+C
            self.logger.info("🛑 Sistema interrompido pelo usuário")
            # Garantir fechamento antes de sair
            try:
                if self.bot_instance and self.bot_instance.driver:
                    self.bot_instance.close_browser()
                    self.bot_instance = None
            except:
                pass
            return
        
        except Exception as e:
            # Erro inesperado - sempre fechar e terminar
            self.logger.error(f"❌ Erro no processamento: {str(e)}")
            try:
                if self.bot_instance and self.bot_instance.driver:
                    self.bot_instance.close_browser()
                    self.bot_instance = None
            except:
                pass
            self.logger.info("❌ Finalizando execução após erro.")
            return
    
    def log_status(self):
        """Log de status do sistema"""
        status_info = {
            "estado": self.state,
            "verificacoes_vazias": self.consecutive_empty_checks,
            "requisicoes_ultima_hora": self.request_count,
            "horario_comercial": self.is_business_hours(),
            "ultima_atividade": self.last_activity.isoformat() if self.last_activity else "Nunca"
        }
        
        self.logger.info(f"📊 Status: {json.dumps(status_info, indent=2)}")

def main():
    """
    Função principal do sistema
    Esta função é executada quando você roda ./run.sh
    """
    print("🚀 Sistema Anti-Lag TCAdmin")
    print("🛡️ Proteção contra sobrecarga")
    print("⏰ Intervalos inteligentes")
    print("📊 Monitoramento contínuo")
    print()
    
    try:
        # ===========================================
        # INICIALIZAÇÃO DO SISTEMA
        # ===========================================
        # Cria instância do bot anti-lag
        bot = AntiLagBot()
        
        # ===========================================
        # EXECUÇÃO DO SISTEMA
        # ===========================================
        # Inicia o loop principal do sistema
        bot.run_anti_lag_system()
        
    except KeyboardInterrupt:
        # Usuário pressionou Ctrl+C para parar
        print("\n⚠️ Sistema interrompido pelo usuário")
    except Exception as e:
        # Erro inesperado
        print(f"\n❌ Erro inesperado: {str(e)}")
    finally:
        # Sempre executa ao final
        print("Sistema finalizado.")

if __name__ == "__main__":
    main()
