import telebot
from telebot import types
import random
import string
import requests
import json
import os

# 1. THÔNG TIN CẤU HÌNH
API_TOKEN = '8253854117:AAGW3fnvJGcHqRS1ahTFmB6sNtwdJTaQe50'
LINK4M_API = '66334c6e06854a07b62bbd8d' 
DATA_FILE = "database.json"
bot = telebot.TeleBot(API_TOKEN)

# --- QUẢN LÝ DỮ LIỆU ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

user_data = load_data()
pending_tokens = {}
MENU_BUTTONS = ["🚀 Kiếm Kim Cương", "👤 Tài Khoản", "💳 Rút Thưởng", "🏆 Bảng Xếp Hạng"]

def get_shortlink(destination_url):
    try:
        api_url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API}&url={destination_url}"
        response = requests.get(api_url).json()
        if response.get('status') == 'success':
            return response.get('shortenedUrl')
    except: pass
    return destination_url

def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*MENU_BUTTONS)
    return markup

# --- XỬ LÝ CHÍNH ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    args = message.text.split()
    if user_id not in user_data:
        user_data[user_id] = {'uid': 'Chưa đặt', 'points': 0}
        save_data()
    
    if len(args) > 1:
        token = args[1]
        if token in pending_tokens and pending_tokens[token] == user_id:
            user_data[user_id]['points'] += 5
            del pending_tokens[token]
            save_data()
            bot.send_message(user_id, "✅ **XÁC MINH THÀNH CÔNG!** +5 Kim Cương.", reply_markup=main_menu())
            return
    
    bot.send_message(user_id, "👋 Chào mừng bạn đến với **ZeiusKC**!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in MENU_BUTTONS)
def handle_menu(message):
    user_id = str(message.chat.id)
    if user_id not in user_data: user_data[user_id] = {'uid': 'Chưa đặt', 'points': 0}
    
    cmd = message.text
    if cmd == "👤 Tài Khoản":
        data = user_data[user_id]
        if data['uid'] == 'Chưa đặt':
            msg = bot.send_message(user_id, "⚠️ Bạn chưa đặt UID. Vui lòng nhập **UID Free Fire**:")
            bot.register_next_step_handler(msg, process_save_uid)
        else:
            # Hiện thông tin và nút SỬA UID
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⚙️ Sửa UID", callback_data="change_uid"))
            bot.send_message(user_id, f"👤 **TÀI KHOẢN**\n🆔 UID: `{data['uid']}`\n💎 Số dư: `{data['points']}` KC", 
                             parse_mode="Markdown", reply_markup=markup)

    elif cmd == "🚀 Kiếm Kim Cương":
        if user_data[user_id]['uid'] == 'Chưa đặt':
            bot.send_message(user_id, "❌ Bạn phải nhập UID trước khi làm nhiệm vụ!")
            return
        bot.send_message(user_id, "⏳ Đang tạo link nhiệm vụ...")
        tk = generate_token()
        pending_tokens[tk] = user_id
        short = get_shortlink(f"https://t.me/ZeiusKCbot?start={tk}")
        bot.send_message(user_id, f"🚀 **NHIỆM VỤ:**\nVượt link để nhận 5 KC:\n🔗 {short}")

    elif cmd == "💳 Rút Thưởng":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💎 50 KC", callback_data="r_50"))
        bot.send_message(user_id, "🎁 Chọn mốc muốn rút:", reply_markup=markup)

# Hàm lưu UID
def process_save_uid(message):
    user_id = str(message.chat.id)
    if message.text in MENU_BUTTONS:
        bot.send_message(user_id, "❌ Đã hủy nhập UID.", reply_markup=main_menu())
        return
    user_data[user_id]['uid'] = message.text
    save_data()
    bot.send_message(user_id, f"✅ Đã cập nhật UID: **{message.text}**", reply_markup=main_menu())

# Xử lý các nút bấm Inline (Sửa UID, Rút tiền)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    
    # Nút Sửa UID
    if call.data == "change_uid":
        msg = bot.send_message(user_id, "🆕 Vui lòng nhập **UID Mới** của bạn:")
        bot.register_next_step_handler(msg, process_save_uid)
    
    # Nút Rút tiền
    elif call.data.startswith("r_"):
        amount = int(call.data.split("_")[1])
        if user_data[user_id]['points'] >= amount:
            user_data[user_id]['points'] -= amount
            save_data()
            bot.send_message(user_id, f"✅ Đã gửi yêu cầu rút {amount} KC thành công!")
        else:
            bot.answer_callback_query(call.id, "❌ Bạn không đủ Kim cương!", show_alert=True)

print("--- BOT ĐANG CHẠY (CÓ CHỨC NĂNG SỬA UID) ---")
bot.polling(none_stop=True)
