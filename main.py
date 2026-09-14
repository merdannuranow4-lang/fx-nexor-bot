import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
from locales import TEXTS

TOKEN = os.getenv("BOT_TOKEN")

USER_LANGUAGES = {}

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

def get_main_menu(lang="tk"):
    t = TEXTS.get(lang, TEXTS["tk"])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_signals"], callback_data="vip_signals"),
         InlineKeyboardButton(text=t["btn_news"], callback_data="market_news")],
        [InlineKeyboardButton(text=t["btn_stats"], callback_data="statistics"),
         InlineKeyboardButton(text=t["btn_profile"], callback_data="my_profile")],
        [InlineKeyboardButton(text=t["btn_lang"], callback_data="change_lang")]
    ])
    return keyboard

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    lang = USER_LANGUAGES.get(user_id, "tk")
    t = TEXTS[lang]
    await message.answer(t["welcome"], reply_markup=get_main_menu(lang))

@dp.callback_query(F.data == "change_lang")
async def lang_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Türkmençe 🇹🇲", callback_data="set_lang_tk"),
         InlineKeyboardButton(text="Türkçe 🇹🇷", callback_data="set_lang_tr")]
    ])
    await callback.message.edit_text("Dil saýlaň / Dil seçin:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "set_lang_tk")
async def set_tk(callback: types.CallbackQuery):
    USER_LANGUAGES[callback.from_user.id] = "tk"
    await callback.message.edit_text(TEXTS["tk"]["lang_changed"], reply_markup=get_main_menu("tk"))
    await callback.answer()

@dp.callback_query(F.data == "set_lang_tr")
async def set_tr(callback: types.CallbackQuery):
    USER_LANGUAGES[callback.from_user.id] = "tr"
    await callback.message.edit_text(TEXTS["tr"]["lang_changed"], reply_markup=get_main_menu("tr"))
    await callback.answer()

@dp.callback_query(F.data.in_({"vip_signals", "market_news", "statistics", "my_profile"}))
async def dummy_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = USER_LANGUAGES.get(user_id, "tk")
    actions = {
        "vip_signals": "💎 VIP Signallar bölümi taýýarlanýar...",
        "market_news": "📰 Bazar Habarlary bölümi taýýarlanýar...",
        "statistics": "📊 Statistikalar bölümi taýýarlanýar...",
        "my_profile": "👤 Şahsy Profil bölümi taýýarlanýar..."
    }
    await callback.answer(actions.get(callback.data, "Ýalňyşlyk!"), show_alert=True)

async def handle_ping(request):
    return web.Response(text="FX_Nexor Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    logging.basicConfig(level=logging.INFO)
    print("FX_Nexor Bot işe girizildi...")
    asyncio.create_task(web_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
