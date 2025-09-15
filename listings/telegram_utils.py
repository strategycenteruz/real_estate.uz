import requests, json
from django.conf import settings

def send_real_estate_to_channel(real_estate):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMediaGroup"

    media_group = []
    files = {}

    # Rasmlar
    for i, img in enumerate(real_estate.images.all()):
        media_group.append({
            "type": "photo",
            "media": f"attach://photo{i}"
        })
        files[f"photo{i}"] = open(img.image.path, "rb")

    # Video
    if real_estate.video:
        media_group.append({
            "type": "video",
            "media": "attach://video"
        })
        files["video"] = open(real_estate.video.path, "rb")

    # Yandex Maps link
    yandex_link = f"https://yandex.uz/maps/?text={real_estate.address}"

    # Shablon matni
    caption_text = f"""
<b>{real_estate.get_type_display().upper()} {real_estate.rooms or '-'} / {real_estate.floor or '-'} / {real_estate.total_floors or '-'}</b>
{real_estate.title or ''}

<b>Ор-р:</b> {real_estate.get_district_display()} {real_estate.orientir or ''}

<b>Комнат:</b> {real_estate.rooms or '-'}
<b>Этаж:</b> {real_estate.floor or '-'}
<b>Этажность:</b> {real_estate.total_floors or '-'}
<b>Площадь:</b> {real_estate.area} кв.м 

{real_estate.description or ''}

<b>Состояние:</b> {real_estate.get_condition_display() if real_estate.condition else '-'}
<b>Мебель:</b> {"Есть" if real_estate.furniture else "Нет"}
<b>Техника:</b> {"Есть" if real_estate.appliances else "Нет"}

<b>Цена:</b> {real_estate.price_usd} у.е

📍 <a href="{yandex_link}">Открыть в Яндекс.Картах</a>

📱 <a href="https://t.me/Abdurashid_estate">Канал</a>                     
📱 <a href="https://www.instagram.com/abdurashid_muhtarovich/">Instagram</a>                              
📨 <a href="https://t.me/Abdurashid_etagi">Напиши мне</a>
    """.strip()

    # Caption oxirgi media elementga qo‘shiladi
    if media_group:
        media_group[-1]["caption"] = caption_text
        media_group[-1]["parse_mode"] = "HTML"

    payload = {
        "chat_id": settings.CHANNEL_ID,
        "media": json.dumps(media_group, ensure_ascii=False)
    }

    response = requests.post(url, data=payload, files=files)
    print("TELEGRAM RESPONSE:", response.json())
