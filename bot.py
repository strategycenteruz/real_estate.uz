from django.conf import settings
import requests

BOT_TOKEN = "7778665104:AAEEf4GljOHqIcQJ99yvjRVk-88NK8TLs6s"  # BotFather orqali olasiz
CHANNEL_ID = "@realestetetg"  # Kanal username yoki ID

def send_real_estate_to_channel(real_estate):
    """RealEstate obyektini kanalga yuboradi"""

    # 1. Asosiy ma’lumotlarni formatlash
    text = (
        f"🏠 <b>{real_estate.title or real_estate.get_type_display()}</b>\n"
        f"📍 Район: {real_estate.get_district_display() if real_estate.district else '-'}\n"
        f"📌 Адрес: {real_estate.address}\n"
        f"📏 Площадь: {real_estate.area} м²\n"
        f"🛏 Комнат: {real_estate.rooms or '-'}\n"
        f"💰 Цена: {real_estate.price_usd} USD\n"
        f"☎️ Телефон: {real_estate.phone}\n"
        f"ℹ️ Статус: {real_estate.get_status_display()}\n\n"
        f"{real_estate.description}\n\n"
        f"🗺 <a href='https://yandex.uz/maps/?text={real_estate.address}'>Открыть на карте</a>"
    )

    # 2. Rasmlar (eng ko‘pi bilan 8 ta)
    images = real_estate.images.all()[:8]
    media_group = []

    for idx, img in enumerate(images):
        media_group.append({
            "type": "photo",
            "media": f"{settings.SITE_URL}{img.image.url}",  # to‘liq URL
            "caption": text if idx == 0 else None,
            "parse_mode": "HTML"
        })

    if media_group:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
            json={"chat_id": CHANNEL_ID, "media": media_group}
        )
    else:
        # Agar rasm bo‘lmasa, faqat text yuborish
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}
        )

    # 3. Video bo‘lsa yuborish
    if real_estate.video:
        video_url = f"{settings.SITE_URL}{real_estate.video.url}"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
            data={"chat_id": CHANNEL_ID, "video": video_url, "caption": "🎥 Видео-обзор"}
        )
