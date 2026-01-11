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

# --- CẤU HÌNH WEB SERVER ĐỂ CHẠY FREE TRÊN RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

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
user_data = {} # (Giữ nguyên các hàm load_data/save_data như cũ)

# ... (Giữ nguyên toàn bộ logic xử lý nút bấm và nhiệm vụ mình đã gửi ở trên) ...

if __name__ == "__main__":
    print("--- KHỞI CHẠY WEB SERVER ---")
    keep_alive() # Mở cổng 8080 để Render không báo lỗi đỏ
    print("--- BOT ZEUS ĐÃ CHẠY ---")
    bot.polling(none_stop=True)
