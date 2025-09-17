import os
from django.contrib.auth import login, logout
from realtor_project import settings
from .forms import RealEstateForm, RatingForm, CommentForm, LoginForm, EvaluationForm

from django.core.paginator import Paginator
from .models import RealEstate, RealEstateRating, RealEstateComment, PropertyType, DistrictChoices, ConditionChoices, SaleStatus,  RealEstateImage, RealEstateVideo
from bot import send_real_estate_to_channel
from .telegram_utils import send_real_estate_to_channel
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg, Min, Max, Count, F, Q
from django.utils.dateparse import parse_date
import os
from django.http import JsonResponse
from django.conf import settings
from .forms import EvaluationForm
from .models import PropertyImage, Property, PropertyType, DistrictChoices
from .utils import calculate_estimate  # sizda hisoblash logikasi shu faylda
# def estimate_view(request):
#     if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
#         form = EvaluationForm(request.POST, request.FILES)
#         if form.is_valid():
#             cd = form.cleaned_data
#             estimated_price, details = calculate_estimate(cd)
#             return JsonResponse({
#                 "success": True,
#                 "estimated_price": estimated_price,
#                 "details": "<br>".join(details)
#             })
#         else:
#
#
#             return JsonResponse({"success": False, "errors": form.errors}, status=400)
#
#     else:
#         form = EvaluationForm()
#     return render(request, "real_estate/estimate.html", {"form": form})

# listings/views.py

# def estimate_view(request):
#     if request.method == "POST":
#         form = EvaluationForm(request.POST, request.FILES)
#         if form.is_valid():
#             cd = form.cleaned_data
#             price, details = calculate_estimate(cd)
#
#             # ruscha label olish
#             property_type_label = dict(PropertyType.choices).get(cd["property_type"], cd["property_type"])
#             district_label = dict(DistrictChoices.choices).get(cd["district"], cd["district"])
#
#             images = []
#             if request.FILES.getlist("images"):
#                 for f in request.FILES.getlist("images"):
#                     tmp_path = os.path.join(settings.MEDIA_ROOT, "tmp", f.name)
#                     with open(tmp_path, "wb+") as dest:
#                         for chunk in f.chunks():
#                             dest.write(chunk)
#                     images.append({
#                         "url": settings.MEDIA_URL + "tmp/" + f.name,
#                         "name": f.name
#                     })
#
#             return JsonResponse({
#                 "success": True,
#                 "price": f"{price:,} USD",
#                 "property_type": property_type_label,   # ✅ ruscha ko‘rinishi
#                 "district": district_label,
#                 "details": details,
#                 "images": images,
#             })
#         else:
#             return JsonResponse({"success": False, "errors": form.errors})


# views.py
import requests
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def send_to_realtor(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        property_type = request.POST.get("property_type")
        details = request.POST.get("details")

        # Xabar matni
        msg = (
            "📩 Новая заявка риэлтору!\n\n"
            f"👤 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"🏠 Тип недвижимости: {property_type}\n"
            f"📋 Детали: {details if details else '—'}\n\n"
            "⚡️ Свяжитесь с клиентом как можно скорее!"
        )

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        res = requests.post(url, data={
            "chat_id": settings.TELEGRAM_CHANNEL_ID,
            "text": msg
        })

        if res.status_code == 200:
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": res.text})

    return JsonResponse({"success": False, "error": "Неверный метод"})

def estimate_page(request):
    form = EvaluationForm()
    return render(request, "real_estate/estimate.html", {"form": form})

def estimate_view(request):
    if request.method == "POST":
        form = EvaluationForm(request.POST)
        if form.is_valid():
            # Property obyektini yaratamiz
            property_obj = form.save(commit=False)
            price, details = calculate_estimate(form.cleaned_data)
            property_obj.save()

            # Rasmlarni saqlash
            images = []
            for f in request.FILES.getlist("images")[:10]:  # maksimal 10 ta
                if not f.content_type.startswith("image/"):
                    continue
                img = PropertyImage.objects.create(property=property_obj, image=f)
                images.append({
                    "url": img.image.url,
                    "name": f.name
                })

            # Ruscha label’lar
            property_type_label = dict(PropertyType.choices).get(
                form.cleaned_data["property_type"],
                form.cleaned_data["property_type"]
            )
            district_label = dict(DistrictChoices.choices).get(
                form.cleaned_data["district"],
                form.cleaned_data["district"]
            )

            return JsonResponse({
                "success": True,
                "price": f"{price:,} USD",
                "property_type": property_type_label,
                "district": district_label,
                "details": details,
                "images": images,
            })

        else:
            return JsonResponse({
                "success": False,
                "errors": form.errors
            })

    return JsonResponse({"success": False, "error": "Invalid request method"})

@login_required
def profile(request):
    # foydalanuvchining e'lonlari
    my_ads = RealEstate.objects.filter(user=request.user)

    # foydalanuvchi "izbrannoye"
    favorite_ads = request.user.favorite_ads.all()

    # foydalanuvchi qoldirgan izohlar yoki baholar asosida ko‘rsatish
    ads_with_stats = (
        RealEstate.objects.filter(
            Q(comments__user=request.user) | Q(ratings__user=request.user)
        )
        .annotate(
            avg_rating=Avg("ratings__rating"),
            comments_count=Count("comments", distinct=True),
        )
        .distinct()
    )

    return render(request, "users/profile.html", {
        "my_ads": my_ads,
        "favorite_ads": favorite_ads,
        "ads_with_stats": ads_with_stats,
    })

def statistics_view(request):
    queryset = RealEstate.objects.all()

    # --- Фильтры ---
    property_type = request.GET.get("property_type")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    district = request.GET.get("district")
    rooms = request.GET.get("rooms")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if property_type:
        queryset = queryset.filter(type=property_type)

    if min_price:
        queryset = queryset.filter(price_usd__gte=min_price)

    if max_price:
        queryset = queryset.filter(price_usd__lte=max_price)

    if district:
        queryset = queryset.filter(district=district)

    if rooms:
        if rooms == "4":
            queryset = queryset.filter(rooms__gte=4)
        else:
            queryset = queryset.filter(rooms=rooms)

    if date_from:
        queryset = queryset.filter(created_at__date__gte=parse_date(date_from))

    if date_to:
        queryset = queryset.filter(created_at__date__lte=parse_date(date_to))

    # --- Статистика ---
    price_stats = queryset.aggregate(
        min_price=Min("price_usd"),
        avg_price=Avg("price_usd"),
        max_price=Max("price_usd"),
    )

    district_data = queryset.values("district").annotate(total=Count("id"))
    district_labels = [d["district"] for d in district_data]
    district_values = [d["total"] for d in district_data]

    avg_price_m2 = queryset.aggregate(
        avg=Avg(F("price_usd") / F("area"))
    )["avg"]

    district_price_m2 = queryset.values("district").annotate(
        avg_price=Avg(F("price_usd") / F("area"))
    )
    district_m2_labels = [d["district"] for d in district_price_m2]
    district_m2_values = [float(d["avg_price"] or 0) for d in district_price_m2]

    type_data = queryset.values("type").annotate(total=Count("id"))
    type_labels = [t["type"] for t in type_data]
    type_values = [t["total"] for t in type_data]

    prices = list(queryset.values_list("price_usd", flat=True))
    hist_labels, hist_values = [], []
    if prices:
        step = 50000
        max_price_val = max(prices)
        bins = range(0, int(max_price_val) + step, step)
        for i in range(len(bins) - 1):
            low, high = bins[i], bins[i + 1]
            count = queryset.filter(price_usd__gte=low, price_usd__lt=high).count()
            hist_labels.append(f"${low/1000:.0f}k–${high/1000:.0f}k")
            hist_values.append(count)

    district_total = sum(district_values) if district_values else 0
    districts = DistrictChoices.choices  # [(value, label), ...]
    property_types = dict(RealEstate._meta.get_field("type").choices)

    context = {
        "price_stats": price_stats,
        "district_labels": [DistrictChoices(d["district"]).label for d in district_data],
        "district_values": district_values,
        "avg_price_m2": avg_price_m2,
        "district_m2_labels": [DistrictChoices(d["district"]).label for d in district_price_m2],
        "district_m2_values": district_m2_values,
        "type_labels": [PropertyType(t["type"]).label for t in type_data],
        "type_values": type_values,
        "district_total": district_total,
        "hist_labels": hist_labels,
        "hist_values": hist_values,
        "districts": districts,
        "property_types": property_types,
    }
    return render(request, "real_estate/stats.html", context)

def real_estate_map(request):
    return render(request, "real_estate/map.html", {
        "type_choices": RealEstate._meta.get_field("type").choices,
        "district_choices": DistrictChoices.choices,  # modeldan rayonlar
    })

def real_estate_api(request):
    q = request.GET.get("q")
    type_ = request.GET.get("type")
    district = request.GET.get("district")

    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    rooms = request.GET.get("rooms")
    floor = request.GET.get("floor")
    area_min = request.GET.get("area_min")
    area_max = request.GET.get("area_max")

    estates = RealEstate.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).filter(is_approved=True)

    if q:
        estates = estates.filter(title__icontains=q)
    if type_:
        estates = estates.filter(type=type_)
    if district:
        estates = estates.filter(district=district)
    if price_min:
        estates = estates.filter(price_usd__gte=price_min)
    if price_max:
        estates = estates.filter(price_usd__lte=price_max)
    if rooms:
        estates = estates.filter(rooms=rooms)
    if floor:
        estates = estates.filter(floor=floor)
    if area_min:
        estates = estates.filter(area__gte=area_min)
    if area_max:
        estates = estates.filter(area__lte=area_max)

    data = []
    for e in estates:
        data.append({
            "id": e.id,
            "title": e.title,
            "address": e.address,
            "district": e.get_district_display(),
            "latitude": e.latitude,
            "longitude": e.longitude,
            "price_usd": e.price_usd,
            "area": e.area,
            "rooms": e.rooms,
            "image": e.images.first().image.url if e.images.exists() else None,
        })
    return JsonResponse(data, safe=False)

def reels_view(request):
    """Alohida reels sahifasi"""
    videos = RealEstateVideo.objects.select_related('real_estate').order_by('-id')[:20]
    return render(request, 'real_estate/reels.html', {'reels_videos': videos})

# Faqat biror kategoriya uchun e’lonlar
def category_list(request, category_code):
    category_label = dict(PropertyType.choices).get(category_code)
    if not category_label:
        return render(request, '404.html', status=404)

    queryset = RealEstate.objects.filter(
        is_approved=True,
        type=category_code
    ).order_by('-created_at').prefetch_related('images')

    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'properties': page_obj,
        'category_label': category_label,
        'type_choices': PropertyType.choices,
    }
    return render(request, 'real_estate/category_list.html', context)

def real_estate_list(request):
    filters = {}
    q_filters = Q()

    q = request.GET.get('q')
    if q:
        q_filters &= (
            Q(title__icontains=q) |
            Q(address__icontains=q) |
            Q(orientir__icontains=q)
        )

    if request.GET.get('type'):
        filters['type'] = request.GET['type']
    if request.GET.get('district'):
        filters['district'] = request.GET['district']
    if request.GET.get('status'):
        filters['status'] = request.GET['status']
    if request.GET.get('rooms'):
        filters['rooms'] = request.GET['rooms']
    if request.GET.get('condition'):
        filters['condition'] = request.GET['condition']
    if request.GET.get('mortgage'):
        filters['mortgage_available'] = True
    if request.GET.get('price'):
        filters['price_usd__lte'] = request.GET['price']

    # --- Reels (video e’lonlar)
    reels_videos = (
        RealEstate.objects
        .filter(is_approved=True)
        .exclude(video__isnull=True).exclude(video="")
        .order_by('-created_at')[:10]
    )

    # --- Popular listings
    popular_listings = (
        RealEstate.objects
        .filter(is_approved=True)
        .annotate(
            favorites_count=Count('favorites', distinct=True),
            popularity=F('views') + F('favorites_count') * 10
        )
        .order_by('-popularity')[:6]
    )

    # --- Category stats
    type_counts = dict(
        RealEstate.objects.filter(is_approved=True)
        .values('type').annotate(total=Count('id'))
        .values_list('type', 'total')
    )

    categories = [
        {
            'code': code,
            'label': label,
            'count': type_counts.get(code, 0),
            'icon': f'icons/{code}.png',
            'url': reverse('category_list', kwargs={'category_code': code}),
        }
        for code, label in PropertyType.choices
    ]

    # --- Main queryset
    queryset = (
        RealEstate.objects.filter(is_approved=True)
        .filter(q_filters, **filters)
        .annotate(average_rating=Avg('ratings__rating'))
        .select_related()
        .prefetch_related('images')
        .only('id', 'title', 'type', 'district', 'status', 'price_usd', 'address', 'area', 'created_at')
        .order_by('-created_at')
    )

    paginator = Paginator(queryset, 9)
    properties = paginator.get_page(request.GET.get('page'))

    # --- Last comments
    comments = (
        RealEstateComment.objects
        .select_related("real_estate")
        .order_by("-created_at")[:10]
    )

    # --- Map data (rayon bo‘yicha)
    district = request.GET.get("district")
    estates = (
        RealEstate.objects.filter(is_approved=True)
        .exclude(latitude__isnull=True, longitude__isnull=True)
    )
    if district:
        estates = estates.filter(district=district)

    estates_json = json.dumps(
        list(estates.values("id", "title", "address", "latitude", "longitude", "price_usd")),
        cls=DjangoJSONEncoder
    )
    # --- Baholash formasi qo‘shildi

    form = EvaluationForm()
    context = {
        'properties': properties,
        'type_choices': PropertyType.choices,
        'district_choices': DistrictChoices.choices,
        'condition_choices': ConditionChoices.choices,
        'status_choices': SaleStatus.choices,
        'reels_videos': reels_videos,
        'categories': categories,
        'popular_listings': popular_listings,
        'comments': comments,
        'selected_district': district,
        'estates_json': estates_json,
        'form': form,  # ✅ Baholash formasi
    }
    return render(request, 'real_estate/list.html', context)








def real_estate_detail(request, pk):
    real_estate = get_object_or_404(RealEstate, pk=pk)

    # Ko‘rish sonini oshirish
    RealEstate.objects.filter(pk=pk).update(views=F('views') + 1)

    # Videolar
    videos = RealEstateVideo.objects.filter(real_estate=real_estate)

    # O‘rtacha baho olish
    avg_rating = real_estate.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)

    # O‘xshash e’lonlar
    similar_listings = RealEstate.objects.filter(district=real_estate.district).exclude(id=real_estate.id)[:4]

    # Formlar
    rating_form = RatingForm()
    comment_form = CommentForm()

    if request.method == "POST":
        # ⭐ Baholash yuborilsa
        if "rating_submit" in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid() and request.user.is_authenticated:
                RealEstateRating.objects.update_or_create(
                    user=request.user,
                    real_estate=real_estate,
                    defaults={'rating': rating_form.cleaned_data['rating']}
                )
                return redirect("real_estate_detail", pk=pk)

        # 💬 Izoh yuborilsa
        elif "comment_submit" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid() and request.user.is_authenticated:
                RealEstateComment.objects.create(
                    user=request.user,
                    real_estate=real_estate,
                    text=comment_form.cleaned_data['text']
                )
                return redirect("real_estate_detail", pk=pk)

    return render(request, "real_estate/detail.html", {
        "real_estate": real_estate,
        "videos": videos,
        "similar_listings": similar_listings,
        "rating_form": rating_form,
        "comment_form": comment_form,
        "avg_rating": avg_rating,
    })

@login_required
def real_estate_create(request):
    if request.method == "POST":
        form = RealEstateForm(request.POST, request.FILES)
        if form.is_valid():
            real_estate = form.save(commit=False)
            real_estate.user = request.user

            for r in RealEstate.objects.all():
                print(r.id, r.address, r.latitude, r.longitude)
            # ✅ Lat/Lng saqlash
            real_estate.latitude = request.POST.get("latitude")
            real_estate.longitude = request.POST.get("longitude")

            real_estate.save()

            # Rasmlar
            images = request.FILES.getlist("images")
            for image in images:
                RealEstateImage.objects.create(real_estate=real_estate, image=image)

            # Telegram kanalga yuborish
            send_real_estate_to_channel(real_estate)

            return redirect("real_estate_list")
    else:
        form = RealEstateForm()

    return render(request, "real_estate/form.html", {"form": form})

@login_required
def real_estate_update(request, pk):
    real_estate = get_object_or_404(RealEstate, pk=pk)
    if request.method == 'POST':
        form = RealEstateForm(request.POST, request.FILES, instance=real_estate)
        if form.is_valid():
            form.save()
            return redirect('real_estate_list')
    else:
        form = RealEstateForm(instance=real_estate)
    return render(request, 'real_estate/form.html', {'form': form})
@login_required
def real_estate_delete(request, pk):
    real_estate = get_object_or_404(RealEstate, pk=pk)
    if request.method == 'POST':
        real_estate.delete()
        return redirect('real_estate_list')
    return render(request, 'real_estate/confirm_delete.html', {'real_estate': real_estate})

@login_required
def all_ads_view(request):
    realestates = RealEstate.objects.order_by('-created_at')
    return render(request, 'all_ads.html', {'realestates': realestates})

def rate_real_estate(request, pk):
    if request.method == "POST":
        real_estate = get_object_or_404(RealEstate, pk=pk)
        rating_val = int(request.POST.get("rating", 0))
        name = request.POST.get("name", "Anonim")

        if 1 <= rating_val <= 5:
            RealEstateRating.objects.create(
                user=request.user if request.user.is_authenticated else None,
                real_estate=real_estate,
                rating=rating_val,
                name=name
            )
    return redirect("real_estate_detail", pk=pk)

def add_comment(request, pk):
    estate = get_object_or_404(RealEstate, pk=pk)

    if request.method == "POST":
        text = request.POST.get("text")
        name = request.POST.get("name", "Анонимный пользователь")

        if text.strip():
            RealEstateComment.objects.create(
                real_estate=estate,
                user=request.user if request.user.is_authenticated else None,
                name=name if not request.user.is_authenticated else request.user.username,
                text=text
            )
            messages.success(request, "Комментарий успешно добавлен ✅")
        else:
            messages.error(request, "Комментарий не может быть пустым ❌")

    return redirect("real_estate_detail", pk=estate.pk)

def add_to_favorites(request, pk):
    real_estate = get_object_or_404(RealEstate, pk=pk)
    if request.user in real_estate.likes.all():
        # Agar foydalanuvchi allaqachon qo‘shgan bo‘lsa → olib tashlaymiz
        real_estate.likes.remove(request.user)
    else:
        # Yangi qo‘shish
        real_estate.likes.add(request.user)

    return redirect("real_estate_detail", pk=pk)


def toggle_favorite(request, pk):
    real_estate = get_object_or_404(RealEstate, pk=pk)

    if real_estate in request.user.favorite_ads.all():
        request.user.favorite_ads.remove(real_estate)
    else:
        request.user.favorite_ads.add(real_estate)

    return redirect("real_estate_detail", pk=pk)


def remove_from_favorites(request, pk):
    """Sevimlilardan olib tashlash"""
    real_estate = get_object_or_404(RealEstate, pk=pk)
    request.user.favorite_ads.remove(real_estate)
    return redirect("favorites_list")
@login_required
def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")  # kirgandan keyin asosiy sahifa
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})

def custom_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return render(request, "users/logout_confirm.html")

@login_required
def dashboard(request):
    return render(request, "users/dashboard.html")

