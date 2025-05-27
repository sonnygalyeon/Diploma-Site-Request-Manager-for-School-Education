# async def handle_application(update, context):
#     try:
#         parts = update.message.text.split(',')
#         if len(parts) != 4:
#             raise ValueError
        
#         course, name, email, phone = [part.strip() for part in parts]
        
#         async with AsyncSession(engine) as session:
#             new_app = Application(
#                 course_name=course,
#                 user_name=name,
#                 email=email,
#                 phone=phone,
#                 user_id=update.message.chat_id
#             )
#             session.add(new_app)
#             await session.commit()
            
#         await update.message.reply_text("✅ Заявка успешно сохранена!")
        
#     except Exception as e:
#         await update.message.reply_text("❌ Ошибка формата. Введите:\nКурс, Имя, Email, Телефон")
        
# async def handle_view_applications(update, context):
#     await update.message.reply_text(
#         "Ваши заявки:\n...",
#         reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
#     )        