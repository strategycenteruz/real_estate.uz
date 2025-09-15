from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
import requests
from django.conf import settings

User = get_user_model()
YANDEX_API_KEY = "3e0c91bd-d2cb-4581-9294-6ce44e90b5f3"  # sizning apikey

class PropertyType(models.TextChoices):
    UCHASTOK = "uchastok", "Участок"
    NOVOSTROYKA = "novostroyka", "Новостройка"
    VTORICHKA = "vtorichka", "Вторичка"
    KOMMERCHESKOE = "kommersiya", "Коммерческое помещение"
    ARENDA = "arenda", "Аренда"

class ConditionChoices(models.TextChoices):
    EVROREMONT = "evroremont", "Евроремонт"
    CHISTYY = "chistyy", "Чистый ремонт"
    BEZ_REMONT = "bez_remonta", "Без ремонта"
    TREBUET_REMONT = "trebuet", "Требует ремонт"

class DistrictChoices(models.TextChoices):
    BEKTEMIR = "bekt", "Бектемирский район"
    CHILANZAR = "chil", "Чиланзарский район"
    YASHNABOD = "yash", "Яшнободский район"
    MIRABAD = "mirab", "Мирабадский район"
    MIRZO_ULUGBEK = "mu", "Мирзо-Улугбекский район"
    SERGELI = "serg", "Сергелийский район"
    SHAYXANTOHUR = "shayx", "Шайхантахурский район"
    ALMAZAR = "almaz", "Алмазарский район"
    UCHTEPA = "uch", "Учтепинский район"
    YAKKASAROY = "yakka", "Яккасарайский район"
    YUNUSABAD = "yunus", "Юнусабадский район"

class SaleStatus(models.TextChoices):
    ACTIVE = "active", "Срочно"
    SOLD = "sold", "Продано"
class RealEstate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # bu "users.User" ni anglatadi
        on_delete=models.CASCADE,
        related_name="real_estates"
    )
    title = models.CharField(max_length=255, blank=True, verbose_name="Название")  # Название (необязательно)
    type = models.CharField(max_length=20, choices=PropertyType.choices, verbose_name="Тип недвижимости")
    district = models.CharField(max_length=30, choices=DistrictChoices.choices, blank=True, null=True,
                                verbose_name="Район")
    status = models.CharField(max_length=20, choices=SaleStatus.choices, default=SaleStatus.ACTIVE, verbose_name="Статус")
    address = models.CharField(max_length=255, verbose_name="Адрес")  # Например: Чиланзар-10
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    orientir = models.CharField(max_length=255, blank=True, verbose_name="Ориентир")  # Например: Базар, метро
    rooms = models.PositiveIntegerField(null=True, blank=True, verbose_name="Количество комнат")
    floor = models.PositiveIntegerField(null=True, blank=True, verbose_name="Этаж")
    total_floors = models.PositiveIntegerField(null=True, blank=True, verbose_name="Этажность")
    area = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name="Общая площадь (м²)")
    condition = models.CharField(max_length=20, choices=ConditionChoices.choices, blank=True, verbose_name="Состояние")
    has_balcony = models.BooleanField(default=False, verbose_name="Есть балкон")
    balcony_size = models.CharField(max_length=50, blank=True, verbose_name="Размер балкона")
    has_terrace = models.BooleanField(default=False, verbose_name="Есть терраса")
    cadastral = models.BooleanField(default=False, verbose_name="Есть кадастр")
    furniture = models.BooleanField(default=False, verbose_name="С мебелью")
    appliances = models.BooleanField(default=False, verbose_name="С техникой")
    price_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена в USD")
    mortgage_available = models.BooleanField(default=True, verbose_name="Ипотека доступна")
    description = models.TextField(blank=True, verbose_name="Дополнительная информация")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрено администратором")
    is_favorite = models.BooleanField(default=False, verbose_name="В избранном")
    # likes = models.PositiveIntegerField(default=0, verbose_name="Количество лайков")
    telegram = models.CharField(max_length=100,blank=True,null=True,verbose_name="Telegram username")

    views = models.PositiveIntegerField(default=0, blank=True)
    favorites = models.ManyToManyField(
        User,
        related_name="favorite_ads",
        blank=True
    )

    video = models.FileField(
        upload_to='videos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi'])]
    )

    def save(self, *args, **kwargs):
        # faqat manzil kiritilgan, lekin koordinata yo‘q bo‘lsa avtomatik olish
        if self.address and (not self.latitude or not self.longitude):
            url = f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&geocode={self.address}&format=json"
            try:
                response = requests.get(url)
                data = response.json()
                pos = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
                lon, lat = pos.split(" ")
                self.longitude = float(lon)
                self.latitude = float(lat)
            except Exception as e:
                print("Geocoding error:", e)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_display()} - {self.address} ({self.area} м²)"

class RealEstateImage(models.Model):
    real_estate = models.ForeignKey(
        RealEstate, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='realestate/images/')

class RealEstateVideo(models.Model):
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE)
    video = models.FileField(upload_to='realestate/videos/')

class RealEstateRating(models.Model):
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # optional
    rating = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True)  # anonim foydalanuvchi ismi

    def __str__(self):
        return f"{self.real_estate} - {self.rating}⭐"

    @property
    def average_rating(self):
        return self.ratings.aggregate(avg=Avg("rating"))["avg"] or 0


class RealEstateComment(models.Model):
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # optional
    name = models.CharField(max_length=100, blank=True)  # anonim foydalanuvchi ismi
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.real_estate} - {self.text[:20]}"


class ChatRoom(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer_chats")
    realtor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="realtor_chats")
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


from django.db import models
class Property(models.Model):
    property_type = models.CharField(max_length=50, choices=PropertyType.choices, verbose_name="Тип недвижимости")
    district = models.CharField(max_length=50, choices=DistrictChoices.choices, verbose_name="Район")

    area = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, verbose_name="Площадь (м²)")
    land_area = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True,
                                    verbose_name="Площадь участка (сотки)")
    rooms = models.IntegerField(null=True, blank=True, verbose_name="Количество комнат")
    floor = models.IntegerField(null=True, blank=True, verbose_name="Этаж")
    total_floors = models.IntegerField(null=True, blank=True, verbose_name="Этажность")

    condition = models.CharField(max_length=50, choices=ConditionChoices.choices, null=True, blank=True,
                                 verbose_name="Состояние")

    has_furniture = models.BooleanField(default=False, verbose_name="С мебелью")
    has_appliances = models.BooleanField(default=False, verbose_name="С техникой")
    has_parking = models.BooleanField(default=False, verbose_name="Есть парковка")
    has_renters = models.BooleanField(default=False, verbose_name="Есть арендаторы")

    facade = models.CharField(max_length=255, null=True, blank=True, verbose_name="Фасад")
    building_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название новостройки")
    line = models.CharField(max_length=100, null=True, blank=True, verbose_name="Линия")

    rent_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                     verbose_name="Арендная плата (USD)")

    base_price_m2 = models.DecimalField(max_digits=12, decimal_places=2, default=800, verbose_name="Цена за 1 м² (USD)")
    base_price_sotix = models.DecimalField(max_digits=12, decimal_places=2, default=1000,
                                           verbose_name="Цена за 1 сотку (USD)")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_property_type_display()} - {self.district}"


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="properties/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property}"



