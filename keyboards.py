from aiogram import types

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📤 Sotish", "📥 Sotib olish")
    kb.add("💰 Hisob", "🆘 Yordam")
    return kb

def account_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ To‘ldirish", "➖ Yechish")
    kb.add("🔙 Orqaga")
    return kb

def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Balans qo‘shish", "➖ Balans yechish")
    return kb
