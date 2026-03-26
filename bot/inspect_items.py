import asyncio
from services.lms_client import LMSClient

async def main():
    client = LMSClient()
    items = await client.get_items()
    if items:
        print("Первый элемент:")
        for key, value in items[0].items():
            print(f"  {key}: {value}")
        print("\nВсе элементы (только title и id, если есть):")
        for item in items:
            # выводим поля, которые могут быть идентификаторами
            print(f"  title: {item.get('title')}, id: {item.get('id')}, external_id: {item.get('external_id')}")
    else:
        print("Не удалось получить items")

asyncio.run(main())
