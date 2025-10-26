from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from strings.en import *

db = Database()

async def available_accounts_callback(client, callback_query):
    accounts = db.get_available_accounts()
    country_stats = db.get_accounts_by_country()
    
    if not accounts:
        await callback_query.edit_message_text(NO_ACCOUNTS_AVAILABLE)
        return
    
    text = AVAILABLE_ACCOUNTS_TITLE
    for stat in country_stats:
        text += ACCOUNT_COUNTRY_STATS.format(
            country=stat["_id"], 
            count=stat["count"]
        ) + "\n"
    
    text += TOTAL_ACCOUNTS.format(total=len(accounts))
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_REFRESH, callback_data="available_accounts")],
        [InlineKeyboardButton(BUTTON_BACK, callback_data="back_to_main")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def solded_accounts_callback(client, callback_query):
    today_stats = db.get_today_sales()
    
    text = SOLDED_TITLE + SOLDED_TODAY_STATS.format(
        sold_today=today_stats["total_sold"],
        profit_today=today_stats["total_profit"]
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(SOLDED_BUTTONS["set_price"], callback_data="set_price")],
        [InlineKeyboardButton(SOLDED_BUTTONS["seven_days"], callback_data="seven_days")],
        [InlineKeyboardButton(BUTTON_BACK, callback_data="back_to_main")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def set_price_callback(client, callback_query):
    await callback_query.edit_message_text(
        SET_PRICE_PROMPT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_BACK, callback_data="solded")]])
    )

async def handle_set_price(client, message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text(INVALID_PRICE_FORMAT)
            return
        
        country = parts[0].upper()
        price = float(parts[1])
        
        db.set_country_price(country, price)
        
        await message.reply_text(
            PRICE_SET_SUCCESS.format(country=country, price=price),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_BACK, callback_data="solded")]])
        )
    except ValueError:
        await message.reply_text(INVALID_PRICE_FORMAT)

async def back_to_main(client, callback_query):
    from handlers.start import start_command
    await start_command(client, callback_query.message)

accounts_handlers = [
    filters.callback_query("available_accounts"),
    filters.callback_query("solded"),
    filters.callback_query("set_price"),
    filters.callback_query("seven_days"),
    filters.callback_query("back_to_main"),
    filters.private & filters.text
]
