import telebot
from telebot import types
import random
import string
import requests
import json
import os
from datetime import datetime
from flask import Flask
from threading import Thread

# --- CẤU HÌNH WEB SERVER (ĐỂ CHẠY FREE TRÊN RENDER) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Zeus is Live!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CẤU HÌNH BOT ---
API_TOKEN = '8253854117:AAGW3fnvJGcHqRS1ahTFmB6sNtwdJTaQe50'
LINK4M_API = '66334c6e06854a07b62bbd8d' 
LAYMA_TOKEN = 'a3b8987dff9f812f7619296cabf79703'
ADMIN_ID = 6365444122 
DATA_FILE = "database.json"

bot = telebot.TeleBot(API_TOKEN)

# --- QUẢN LÝ DỮ LIỆU ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

user_data = load_data()
pending_tokens = {}
MENU_BUTTONS = [
    "🚀 Kiếm Kim Cương", "👤 Tài Khoản",
    "💳 Rút Thưởng", "🏆 Bảng Xếp Hạng",
    "📌 Thông Tin", "📚 Hướng Dẫn",
    "☎️ Hỗ Trợ", "📩 Chia sẻ bot"
]

# --- HÀM RÚT GỌN LINK ---
def get_link4m(url):
    try:
        api_url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API}&url={url}"
        res = requests.get(api_url).json()
        return res.get('shortenedUrl') if res.get('status') == 'success' else url
    except: return url

def get_layma(url):
    try:
        api_url = f"https://api.layma.net/api/admin/shortlink/quicklink?tokenUser={LAYMA_TOKEN}&format=json&url={url}"
        res = requests.get(api_url).json()
        return res.get('shortlink') if res.get('status') == 'success' else url
    except: return url

def check_limit(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    user = user_data[user_id]
    if user.get('last_day') != today:
        user['last_day'] = today
        user['count_link4m'] = 0
        user['count_layma'] = 0
        save_data()
    return user

# --- XỬ LÝ LỆNH ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    args = message.text.split()
    
    if user_id not in user_data:
        msg = bot.send_message(user_id, "👋 Chào mừng! Hãy nhập **Tên người dùng** muốn đặt:")
        bot.register_next_step_handler(msg, process_username)
        return

    if len(args) > 1:
        token = args[1]
        if token in pending_tokens and pending_tokens[token]['id'] == user_id:
            task_type = pending_tokens[token]['type']
            user_data[user_id]['points'] += 5
            user_data[user_id][f'count_{task_type}'] += 1
            del pending_tokens[token]
            save_data()
            bot.send_message(user_id, f"✅ Thành công! Bạn nhận được 5 💎 từ nhiệm vụ {task_type.upper()}.")
            return

    bot.send_message(user_id, f"🌟 Chào mừng trở lại, {user_data[user_id].get('username')}!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🚀 Kiếm Kim Cương")
def task_menu(message):
    user_id = str(message.chat.id)
    user = check_limit(user_id)
    total_tasks = user['count_link4m'] + user['count_layma']
    
    text = (f"🎯 **CHỌN NHÀ CUNG CẤP**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 Nhiệm vụ hôm nay: {total_tasks}/3\n\n"
            f"Chọn nhiệm vụ bạn muốn làm:")

    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton(f"LINK4M ({user['count_link4m']}/2)", callback_data="task_link4m"),
        types.InlineKeyboardButton(f"LAYMA ({user['count_layma']}/1)", callback_data="task_layma"),
        types.InlineKeyboardButton("SẮP RA MẮT", callback_data="soon"),
        types.InlineKeyboardButton("SẮP RA MẮT", callback_data="soon")
    ]
    markup.add(*btns)
    bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def handle_task(call):
    user_id = str(call.message.chat.id)
    task_type = call.data.replace("task_", "")
    user = check_limit(user_id)
    
    limit = 2 if task_type == "link4m" else 1
    if user[f'count_{task_type}'] >= limit:
        bot.answer_callback_query(call.id, f"❌ Hết lượt {task_type.upper()} hôm nay!", show_alert=True)
        return

    tk = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    pending_tokens[tk] = {'id': user_id, 'type': task_type}
    dest = f"https://t.me/ZeiusKCbot?start={tk}"
    short = get_link4m(dest) if task_type == "link4m" else get_layma(dest)
    bot.edit_message_text(f"🚀 **NHIỆM VỤ {task_type.upper()}:**\nVượt link để nhận 5 💎:\n🔗 {short}", user_id, call.message.message_id, parse_mode="Markdown")

# --- QUY TRÌNH ĐĂNG KÝ ---
def process_username(message):
    user_id = str(message.chat.id)
    user_data[user_id] = {'username': message.text, 'uid': 'Chưa đặt', 'points': 0, 'last_day': '', 'count_link4m': 0, 'count_layma': 0}
    msg = bot.send_message(user_id, f"Chào **{message.text}**! Bây giờ hãy nhập **UID Free Fire**:")
    bot.register_next_step_handler(msg, process_initial_uid)

def process_initial_uid(message):
    user_id = str(message.chat.id)
    user_data[user_id]['uid'] = message.text
    save_data()
    bot.send_message(user_id, "🎉 Đăng ký thành công!", reply_markup=main_menu())

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*MENU_BUTTONS)
    return markup

# --- CHẠY SONG SONG WEB SERVER VÀ BOT ---
if __name__ == "__main__":
    keep_alive() # Mở cổng để Render không lỗi
    print("--- BOT ZEUS ĐÃ SẴN SÀNG ---")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    print("--- KHỞI CHẠY WEB SERVER ---")
    keep_alive() # Mở cổng 8080 để Render không báo lỗi đỏ
    print("--- BOT ZEUS ĐÃ CHẠY ---")
    bot.polling(none_stop=True)
