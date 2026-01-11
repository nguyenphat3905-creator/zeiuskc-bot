import telebot
from telebot import types
import random
import string
import requests
import json
import os

# --- CẤU HÌNH ---
API_TOKEN = '8253854117:AAGW3fnvJGcHqRS1ahTFmB6sNtwdJTaQe50'
LINK4M_API = '66334c6e06854a07b62bbd8d' 
ADMIN_ID = 6365444122  # THAY ID CỦA BẠN VÀO ĐÂY
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
MENU_BUTTONS = ["🚀 Kiếm Kim Cương", "👤 Tài Khoản", "💳 Rút Thưởng", "🏆 Bảng Xếp Hạng"]

# --- HÀM TRỢ GIÚP ---
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

# --- XỬ LÝ ĐĂNG NHẬP / START ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    args = message.text.split()
    
    # Nếu chưa có trong dữ liệu -> Bắt đầu quy trình đăng ký
    if user_id not in user_data:
        msg = bot.send_message(user_id, "👋 Chào mừng bạn! Để bắt đầu, hãy nhập **Tên người dùng** (Username) bạn muốn đặt:")
        bot.register_next_step_handler(msg, process_username)
        return

    # Nếu đã đăng ký và có link xác nhận (vượt link xong)
    if len(args) > 1:
        token = args[1]
        if token in pending_tokens and pending_tokens[token] == user_id:
            user_data[user_id]['points'] += 5
            del pending_tokens[token]
            save_data()
            bot.send_message(user_id, "✅ **XÁC MINH THÀNH CÔNG!**\nBạn nhận được +5 Kim Cương 💎", reply_markup=main_menu())
            return

    bot.send_message(user_id, f"🌟 Chào mừng trở lại, **{user_data[user_id].get('username', 'Bạn')}**!", reply_markup=main_menu())

# Bước 1: Nhận Username
def process_username(message):
    user_id = str(message.chat.id)
    username = message.text
    if username in MENU_BUTTONS: return
    
    user_data[user_id] = {'username': username, 'uid': 'Chưa đặt', 'points': 0}
    msg = bot.send_message(user_id, f"Chào **{username}**! Bây giờ hãy nhập **UID Free Fire** của bạn:")
    bot.register_next_step_handler(msg, process_initial_uid)

# Bước 2: Nhận UID lần đầu
def process_initial_uid(message):
    user_id = str(message.chat.id)
    uid = message.text
    if uid in MENU_BUTTONS: return
    
    if not uid.isdigit() or len(uid) < 5:
        msg = bot.send_message(user_id, "❌ UID phải là dãy số (ít nhất 5 số). Nhập lại nhé:")
        bot.register_next_step_handler(msg, process_initial_uid)
        return

    user_data[user_id]['uid'] = uid
    save_data()
    bot.send_message(user_id, "🎉 **ĐĂNG KÝ HOÀN TẤT!**\nBạn có thể bắt đầu kiếm Kim Cương ngay bây giờ.", reply_markup=main_menu())

# --- XỬ LÝ MENU ---
@bot.message_handler(func=lambda m: m.text in MENU_BUTTONS)
def handle_menu(message):
    user_id = str(message.chat.id)
    if user_id not in user_data:
        start(message)
        return
    
    cmd = message.text
    if cmd == "👤 Tài Khoản":
        data = user_data[user_id]
        text = (f"👤 **THÔNG TIN TÀI KHOẢN**\n\n"
                f"📛 Tên: `{data['username']}`\n"
                f"🆔 UID FF: `{data['uid']}`\n"
                f"💎 Số dư: `{data['points']}` KC")
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⚙️ Sửa UID", callback_data="change_uid"))
        bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)

    elif cmd == "🚀 Kiếm Kim Cương":
        msg = bot.send_message(user_id, "⏳ Đang tạo link nhiệm vụ...")
        tk = generate_token()
        pending_tokens[tk] = user_id
        short = get_shortlink(f"https://t.me/ZeiusKCbot?start={tk}")
        bot.edit_message_text(f"🚀 **NHIỆM VỤ:**\nVượt link để nhận 5 Kim Cương:\n🔗 {short}", user_id, msg.message_id)

    elif cmd == "💳 Rút Thưởng":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💎 50 KC", callback_data="r_50"),
                   types.InlineKeyboardButton("💎 100 KC", callback_data="r_100"))
        bot.send_message(user_id, "🎁 **CHỌN MỐC RÚT:**", reply_markup=markup)

    elif cmd == "🏆 Bảng Xếp Hạng":
        top = sorted(user_data.items(), key=lambda x: x[1]['points'], reverse=True)[:5]
        text = "🏆 **TOP 5 ĐẠI GIA KIM CƯƠNG**\n\n"
        for i, (uid, info) in enumerate(top, 1):
            text += f"{i}. {info['username']} - {info['points']} 💎\n"
        bot.send_message(user_id, text)

# Hàm sửa UID riêng (nếu người dùng bấm nút Sửa)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    if call.data == "change_uid":
        msg = bot.send_message(user_id, "⌨️ Nhập UID Free Fire mới:")
        bot.register_next_step_handler(msg, process_initial_uid)
    elif call.data.startswith("r_"):
        # (Giữ nguyên logic rút thưởng cũ của bạn)
        amount = int(call.data.split("_")[1])
        if user_data[user_id]['points'] >= amount:
            user_data[user_id]['points'] -= amount
            save_data()
            bot.send_message(user_id, "✅ Đã gửi yêu cầu rút!")
            bot.send_message(ADMIN_ID, f"🔔 **RÚT TIỀN:** {user_data[user_id]['username']} | UID: {user_data[user_id]['uid']} | {amount} KC")
        else:
            bot.answer_callback_query(call.id, "❌ Không đủ điểm!", show_alert=True)

print("--- BOT ZEUS (LOGIN MODE) ĐÃ CHẠY ---")
bot.polling(none_stop=True)
