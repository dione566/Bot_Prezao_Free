import telebot
import json
import requests
import time
import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta

state_storage = StateMemoryStorage()
bot = telebot.TeleBot("7657325142:AAFX7Dq-2lDjvsXFAkzQVYX5oJzavD-7uhU", state_storage=state_storage)

users_data = {}
campaign_data_by_user = {}
active_tasks = {}
menu_messages = {}
last_campaigns = {}

def create_session():
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def load_users():
    try:
        response = requests.get('https://raw.githubusercontent.com/dione566/Prezao_Free/refs/heads/main/Contas/users.json')
        return response.json()
    except:
        return {}

def check_user_expiry(user_id):
    if user_id not in users_data:
        return False
    return True

def get_remaining_time(user_id):
    if user_id not in users_data:
        return "Expirado"
    return "Ativo"

def format_data_size(size_str):
    try:
        size = float(size_str.split()[0])
        unit = size_str.split()[1]
        if unit.upper() == 'MB':
            if size.is_integer():
                return f"{int(size)} MB"
            return f"{size:.1f} MB".rstrip('0').rstrip('.')
        elif unit.upper() == 'GB':
            if size.is_integer():
                return f"{int(size)} GB"
            return f"{size:.1f} GB".rstrip('0').rstrip('.')
        return size_str
    except:
        return size_str

def check_login_status(user_id, headers):
    url = 'https://cfree.clarosgvas.mobicare.com.br/home'
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200 and 'wallet' in response.json()
    except:
        return False

def verify_login(func):
    def wrapper(message, *args, **kwargs):
        user_id = str(message.from_user.id)
        if user_id not in users_data:
            bot.reply_to(message, "⚠️ Você não está autorizado.")
            return
        if not check_user_expiry(user_id):
            bot.reply_to(message, "❌ Seu acesso expirou. Contate um administrador.")
            return
        headers = {
            'X-AUTHORIZATION': users_data[user_id]["auth"],
            'Content-Type': 'application/json',
            'X-CHANNEL': 'ANDROID',
            'X-APP-VERSION': '2.9.2.4',
            'Host': 'cfree.clarosgvas.mobicare.com.br',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/4.12.0'
        }
        if not check_login_status(user_id, headers):
            bot.reply_to(message, "🚫 Por favor, solicite ao administrador (@Soueuman) que realize uma reconexão para este bot.")
            return
        return func(message, *args, **kwargs)
    return wrapper

@bot.message_handler(commands=['start'])
def start(message):
    global users_data
    users_data = load_users()
    if str(message.from_user.id) in users_data:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("Resgatar 🌐"),
            KeyboardButton("🔍 Verificar"),
            KeyboardButton("✅ Iniciar")
        )
        welcome_msg = "Boas-vindas ao bot Prezao Hack! 😊"
        bot.reply_to(message, welcome_msg, reply_markup=markup)
    else:
        bot.reply_to(message, "⚠️ Você não está autorizado a usar este bot.")

@bot.message_handler(func=lambda message: message.text == "Resgatar 🌐")
@verify_login
def menu_button(message):
    menu(message)

@bot.message_handler(func=lambda message: message.text == "🔍 Verificar")
@verify_login
def verify_button(message):
    check_campaigns(message)

@bot.message_handler(func=lambda message: message.text == "✅ Iniciar")
@verify_login
def start_button(message):
    start_campaigns(message)

@bot.message_handler(func=lambda message: message.text == "⏹ Stop")
@verify_login
def stop_button(message):
    stop_campaigns(message)

@bot.message_handler(commands=['stop'])
@verify_login
def stop_campaigns(message):
    user_id = str(message.from_user.id)
    if user_id in active_tasks:
        active_tasks[user_id] = False
        if user_id in campaign_data_by_user:
            del campaign_data_by_user[user_id]
        bot.reply_to(message, "⚠️ CAMPANHAS PARADAS USE curl -sO https://raw.githubusercontent.com/dione566/Prezao_Free/refs/heads/main/Bots/botbanidos.sh; chmod 777 botbanidos.sh 2> /dev/null; ./botbanidos.sh 2> /dev/nullificar ANTES DE INICIAR NOVAMENTE ⚠️")

@bot.message_handler(commands=['verificar'])
@verify_login
def check_campaigns(message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        bot.reply_to(message, "⚠️ Você não está autorizado.")
        return
    active_tasks[user_id] = True
    session = create_session()
    urls = [
        "https://cfree.clarosgvas.mobicare.com.br/adserver/campaign/v3/dcc45968-df87-403b-8c75-a8c021ec4c8c?size=100",
        "https://cfree.clarosgvas.mobicare.com.br/adserver/campaign/v3/bbdef37d-f5c4-4b19-9cfb-ed6e8f43fa2f?size=100",
        "https://cfree.clarosgvas.mobicare.com.br/adserver/campaign/v3/2b25a088-84ea-11ef-9082-0e639a16be05?size=100",
        "https://cfree.clarosgvas.mobicare.com.br/adserver/campaign/v3/4e5b1488-293f-466e-9cbb-0a6dff433fb4?size=100",
        "https://cfree.clarosgvas.mobicare.com.br/adserver/campaign/v3/7868de6a-e31a-11ef-bb8e-0680334bb059?size=100",
    ]
    headers = {
        "x-access-token": "4e82abb4-2718-4d65-bcd4-c4e147c3404f",
        "X-CHANNEL": "ANDROID",
        "X-APP-VERSION": "2.9.2.4",
        "X-ARTEMIS-CHANNEL-UUID": "cfree-b22d-4079-bca5-96359b6b1f57",
        "X-AUTHORIZATION": users_data[user_id]["auth"],
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "okhttp/4.12.0"
    }
    payload = {
        "context": {
            "appVersion":"2.9.2.4","product":"greatltexx","os":"ANDROID","battery":"26","deviceId":"47d84c21057215e9","manufacturer":"samsung","carrier":"Claro BR","adId":"208cb6e6-9bca-47c3-ab06-d3b9593bc945","osVersion":"9","appId":"br.com.mobicare.clarofree","sdkVersion":"3.2.9.5-rv-max-6","model":"SM-N950F","brand":"samsung","hardware":"samsungexynos8895","eventDate": str(int(time.time() * 1000))
        },
        "userId": users_data[user_id]["user_id"]
    }
    
    try:
        campaign_data = {}
        has_campaigns = False
        
        for url in urls:
            response = session.post(url, headers=headers, json=payload, timeout=30)
            if response.text:
                response_data = response.json()
                if 'campaigns' in response_data:
                    has_campaigns = True
                    for campaign in response_data['campaigns']:
                        campaign_name = campaign['campaignName']
                        tracking_id = campaign['trackingId']
                        campaign_uuid = campaign['campaignUuid']
                        media_list = campaign.get('mainData', {}).get('media', [])
                        
                        if campaign_name not in campaign_data:
                            campaign_data[campaign_name] = {
                                'campaignUuid': campaign_uuid,
                                'trackingId': tracking_id,
                                'media': {}
                            }
                        
                        for media in media_list:
                            media_title = media.get('title')
                            media_uuid = media.get('uuid')
                            if media_title and media_uuid:
                                if media_uuid not in campaign_data[campaign_name]['media']:
                                    campaign_data[campaign_name]['media'][media_uuid] = media_title
        
        if not has_campaigns:
            if user_id in campaign_data_by_user:
                del campaign_data_by_user[user_id]
            bot.reply_to(message, "⚠️ Sem campanhas disponíveis no momento. Use /verificar mais tarde para tentar novamente.")
            return
            
        campaign_data_by_user[user_id] = campaign_data
        last_campaigns[user_id] = campaign_data.copy()
        bot.reply_to(message, "✅ Campanhas verificadas! Use /iniciar para começar.")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erro ao verificar campanhas: {str(e)}")
    finally:
        session.close()

@bot.message_handler(commands=[''])
@verify_login
def refazer_campaigns(message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        bot.reply_to(message, "⚠️ Você não está autorizado.")
        return
    if user_id not in last_campaigns or not last_campaigns[user_id]:
        bot.reply_to(message, "⚠️ Não há campanhas anteriores para refazer. Use /verificar para buscar novas campanhas.")
        return
    campaign_data_by_user[user_id] = last_campaigns[user_id].copy()
    bot.reply_to(message, "✅ Campanhas anteriores carregadas! Iniciando execução...")
    message.text = "/iniciar"
    start_campaigns(message)

@bot.message_handler(commands=['iniciar'])
@verify_login
def start_campaigns(message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        bot.reply_to(message, "⚠️ Você não está autorizado.")
        return
    if user_id not in campaign_data_by_user:
        bot.reply_to(message, "⚠️ Não há campanhas disponíveis. Use /verificar para buscar novas campanhas.")
        return

    active_tasks[user_id] = True
    campaign_data = campaign_data_by_user[user_id]
    
    total_media = sum(len(camp['media']) for camp in campaign_data.values())
    completed_media = 0
    progress_bars = ['░░░░░░░░░░', '█░░░░░░░░░', '██░░░░░░░░', '███░░░░░░░', '████░░░░░░', 
                    '█████░░░░░', '██████░░░░', '███████░░░', '████████░░', '█████████░', '██████████']

    status_message = bot.send_message(message.chat.id, "🤖 Iniciando campanhas...")
    
    completed_lock = threading.Lock()
    thread_semaphore = threading.Semaphore(15)
    stop_event = threading.Event()

    def process_media(campaign_name, campaign_uuid, track, media_uuid, media_title):
        nonlocal completed_media
        
        with thread_semaphore:
            if stop_event.is_set():
                return

            session = create_session()
            headers = {
                "x-access-token": "4e82abb4-2718-4d65-bcd4-c4e147c3404f",
                "Content-Type": "application/json",
                "X-CHANNEL": "ANDROID",
                "X-APP-VERSION": "2.9.2.4",
                "X-ARTEMIS-CHANNEL-UUID": "cfree-b22d-4079-bca5-96359b6b1f57",
                "X-AUTHORIZATION": users_data[user_id]["auth"],
                "User-Agent": "okhttp/4.12.0"
            }

            try:
                time.sleep(5)
                
                if stop_event.is_set():
                    return

                tracking_url = f"https://cfree.clarosgvas.mobicare.com.br/adserver/tracker?e=complete&c={campaign_uuid}&u={users_data[user_id]['user_id']}&requestId={track}&m={media_uuid}"
                response = session.post(tracking_url, headers=headers, timeout=30)

                with completed_lock:
                    completed_media += 1
                    progress = int((completed_media / total_media) * 100)
                    progress_bar = progress_bars[int(progress/10)]

                    status_text = (
                        f"⚙️ Executando campanhas...\n\n"
                        f"⏳ [{progress_bar}] {progress}%\n\n"
                        f"📢 Anúncios: {completed_media}/{total_media}\n\n"
                        f"🎬 Assistindo... {total_media} Anúncios"
                    )

                    try:
                        bot.edit_message_text(status_text, message.chat.id, status_message.message_id)
                    except:
                        pass

            except Exception as e:
                with completed_lock:
                    completed_media += 1
            finally:
                session.close()

    try:
        threads = []
        for campaign_name, media in campaign_data.items():
            campaign_uuid = media.get('campaignUuid')
            track = media.get('trackingId')
            
            for media_uuid, media_title in media['media'].items():
                if stop_event.is_set():
                    break
                
                thread = threading.Thread(
                    target=process_media,
                    args=(campaign_name, campaign_uuid, track, media_uuid, media_title)
                )
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

        if active_tasks.get(user_id, False) and not stop_event.is_set():
            final_text = (
                f"✅ CAMPANHAS CONCLUÍDAS\n\n"
                f"📺 Total de vídeos: {total_media}\n"
                f"⏱ Tempo aproximado: {(total_media * 5) // 15} segundos\n\n"
                f"Use /verificar para buscar novas campanhas"
            )
            bot.edit_message_text(final_text, message.chat.id, status_message.message_id)
            del campaign_data_by_user[user_id]

    except Exception as e:
        stop_event.set()
        bot.edit_message_text(f"❌ Erro durante a execução: {str(e)}", message.chat.id, status_message.message_id)
    finally:
        active_tasks[user_id] = False

@bot.message_handler(commands=['menu'])
@verify_login
def menu(message):
    user_id = str(message.from_user.id)
    headers = {
        'X-AUTHORIZATION': users_data[user_id]["auth"],
        'Content-Type': 'application/json',
        'X-CHANNEL': 'ANDROID',
        'X-APP-VERSION': '2.9.2.4',
        'Host': 'cfree.clarosgvas.mobicare.com.br',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.12.0'
    }
    url = 'https://cfree.clarosgvas.mobicare.com.br/home'
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        wallet_info = {
            'saldo': data['wallet']['balance'],
            'disponivel_em': data['wallet']['availableIn']
        }
        credits_info = None
        for credit in data['credits']:
            if credit['type'] == 'DATA':
                credits_info = {
                    'total': format_data_size(f"{credit['total']} {credit['unit']}"),
                    'usado': format_data_size(f"{credit['used']} {credit['unit']}"),
                    'disponivel': format_data_size(f"{credit['usable']} {credit['unit']}")
                }
                break
        msg = f""
        msg += f""
        msg += f""
        if credits_info:
            msg += ""
            msg += f"Internet Total: {credits_info['total']}\n"
            msg += f"Internet Usada: {credits_info['usado']}\n"
            msg += f"Internet Disponível: {credits_info['disponivel']}\n\n"
        msg += f"💰 Moedas: {wallet_info['saldo']:.0f}\n\n"
        msg += "███▓▒░ RESGATAR ░▒▓███\n"
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for package in data['packages']:
            mb_amount = package['description'].split(' ')[1].split(' MB')[0]
            package_text = f"{mb_amount}MB - R$ {package['total']:.0f}"
            msg += f"\n{package['name']}\n"
            msg += f"{package['description']}\n"
            msg += f"{package['total']:.0f} MOEDAS 💰\n"
            buttons.append(KeyboardButton(f"📦 {mb_amount}MB"))
        buttons.append(KeyboardButton("/start"))
        markup.add(*buttons)
        sent_message = bot.reply_to(message, msg, reply_markup=markup)
        menu_messages[user_id] = sent_message
    except:
        bot.reply_to(message, "❌ Erro ao carregar o menu. Tente novamente mais tarde.")

@bot.message_handler(func=lambda message: message.text and message.text.startswith("📦"))
def handle_package_button(message):
    mb_amount = message.text.split("📦 ")[1].split("MB")[0]
    user_id = str(message.from_user.id)
    headers = {
        'X-AUTHORIZATION': users_data[user_id]["auth"],
        'Content-Type': 'application/json',
        'X-CHANNEL': 'ANDROID',
        'X-APP-VERSION': '2.9.2.4',
        'Host': 'cfree.clarosgvas.mobicare.com.br',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.12.0'
    }
    url = 'https://cfree.clarosgvas.mobicare.com.br/home'
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        for package in data['packages']:
            if mb_amount in package['description']:
                message.text = f"/pacote_{package['id']}"
                select_package_handler(message)
                return
        bot.reply_to(message, "❌ Pacote não encontrado.")
    except:
        bot.reply_to(message, "❌ Erro ao processar o pacote.")

@bot.message_handler(regexp="^/pacote_[0-9]+$")
@verify_login
def select_package_handler(message):
    user_id = str(message.from_user.id)
    package_id = message.text.split('_')[1]
    headers = {
        'X-AUTHORIZATION': users_data[user_id]["auth"],
        'X-CHANNEL': 'ANDROID',
        'X-APP-VERSION': '2.9.2.4',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'cfree.clarosgvas.mobicare.com.br',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.12.0'
    }
    data = {"packageId": package_id}
    url = 'https://cfree.clarosgvas.mobicare.com.br/package/withdraw'
    try:
        response = requests.post(url, headers=headers, json=data)
        response_code = response.json()["code"]
        if "ACCEPTED" in response_code:
            bot.reply_to(message, "✅ Pacote resgatado com sucesso!")
            if user_id in menu_messages:
                menu(message)
        elif "WITHDRAW_NOT_ALLOWED" in response_code:
            bot.reply_to(message, "❌ Limite de resgates diários atingido.")
        else:
            bot.reply_to(message, "❌ Erro ao resgatar o pacote.")
    except:
        bot.reply_to(message, "❌ Erro ao processar o resgate.")

def refresh_users():
    global users_data
    while True:
        users_data = load_users()
        time.sleep(300)

refresh_thread = threading.Thread(target=refresh_users, daemon=True)
refresh_thread.start()

users_data = load_users()
bot.infinity_polling()