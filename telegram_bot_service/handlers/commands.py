from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select, func
from database import AsyncSessionLocal
from models import Course, Application

async def handle_application(update, context):
    try:
        parts = update.message.text.split(',')
        if len(parts) != 4:
            raise ValueError

        course, name, email, phone = [part.strip() for part in parts]

        async with AsyncSession(engine) as session:
            new_app = Application(
                course_name=course,
                user_name=name,
                email=email,
                phone=phone,
                user_id=update.message.chat_id
            )
            session.add(new_app)
            await session.commit()

        await update.message.reply_text("✅ Заявка успешно сохранена!")

    except Exception as e:
        await update.message.reply_text("❌ Ошибка формата. Введите:\nКурс, Имя, Email, Телефон")


async def handle_view_applications(update, context):
    await update.message.reply_text(
        "Ваши заявки:\n...",
        reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
    )


async def handle_course_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with AsyncSessionLocal() as session:
            # Получаем статистику по количеству заявок на каждый курс
            query = select(
                Course.title,
                func.count(Application.id)
            ).join(
                Application, Course.id == Application.course_id
            ).group_by(
                Course.title
            ).order_by(
                func.count(Application.id).desc()
            )

            result = await session.execute(query)
            stats = result.all()

            if not stats:
                await update.message.reply_text("📊 Пока нет данных о заявках")
                return

            # Форматируем сообщение
            message = "📈 <b>Статистика по курсам</b>:\n\n"
            for course_title, count in stats:
                message += f"▪️ <i>{course_title}</i>: <b>{count}</b> заявок\n"

            # Добавляем общее количество
            total_query = select(func.count(Application.id))
            total = (await session.execute(total_query)).scalar()
            message += f"\nВсего заявок: <b>{total}</b>"

            await update.message.reply_text(
                text=message,
                parse_mode='HTML'
            )

    except Exception as e:
        await update.message.reply_text(
            "❌ Произошла ошибка при получении статистики. Попробуйте позже."
        )
        print(f"Error in handle_course_stats: {e}")
