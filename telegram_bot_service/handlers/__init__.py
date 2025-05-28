from .commands import handle_application, handle_view_applications, handle_course_stats
# from .keyboards import main_keyboard


def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"^📋 Просмотр заявок$"),
        handle_view_applications))
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"^📊 Список количества"),
        handle_course_stats))
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"^📝 Запись заявок$"),
        lambda u, c: u.message.reply_text("Введите данные...")))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_application))
