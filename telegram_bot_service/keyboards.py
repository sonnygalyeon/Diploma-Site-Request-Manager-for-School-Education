# keyboards.py
from telegram import ReplyKeyboardMarkup

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [["📝 Подать заявку", "📋 Мои заявки"]],
        resize_keyboard=True
    )


async def handle_view_applications(update, context):
    await update.message.reply_text(
        "Ваши заявки:\n...",
        reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
    )
