BOT_TOKEN = "7726856222:AAEnn5XEVxWDuMR3MvLt2gsGT4wdgjdYD44"

import httpx
import asyncio

async def main():
    
    async with httpx.AsyncClient() as client:
        # Проверка токена
        response = await client.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        )
        print("Проверка бота:", response.json())
        
        # Получение обновлений
        updates = await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            json={"offset": -1, "limit": 1}  # Последнее сообщение
        )
        print("Последнее обновление:", updates.json())

if __name__ == "__main__":
    asyncio.run(main())