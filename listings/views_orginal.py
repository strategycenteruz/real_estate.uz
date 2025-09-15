from django.contrib.auth import login, logout

from .forms import RealEstateForm, RatingForm, CommentForm, LoginForm
from django.db.models import Avg, F, Q,Count
from django.core.paginator import Paginator
from .models import RealEstate, RealEstateRating, RealEstateComment, PropertyType, DistrictChoices, ConditionChoices, SaleStatus,  RealEstateImage, RealEstateVideo
from django.urls import reverse
from bot import send_real_estate_to_channel
from .telegram_utils import send_real_estate_to_channel
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.functions import TruncMonth
from django.db.models import Avg, Count
from listings.models import RealEstate, RealEstateRating, RealEstateComment

@login_required
def dashboard(request):
    estates = RealEstate.objects.all()
    return render(request, "listings/dashboard.html", {"estates": estates})

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

    # GET parametrlari
    q = request.GET.get('q')
    prop_type = request.GET.get('type')
    district = request.GET.get('district')
    status = request.GET.get('status')
    rooms = request.GET.get('rooms')
    condition = request.GET.get('condition')
    mortgage = request.GET.get('mortgage')
    price = request.GET.get('price')

    # Qidiruv (matnli)
    if q:
        q_filters &= (
            Q(title__icontains=q) |
            Q(address__icontains=q) |
            Q(orientir__icontains=q)
        )

    # Oddiy filtrlar (indeksdan foydalanadi)
    if prop_type:
        filters['type'] = prop_type
    if district:
        filters['district'] = district
    if status:
        filters['status'] = status
    if rooms:
        filters['rooms'] = rooms
    if condition:
        filters['condition'] = condition
    if mortgage:
        filters['mortgage_available'] = True
    if price:
        filters['price_usd__lte'] = price

        # 🎥 Faqat video e’lonlar
    reels_videos = RealEstate.objects.filter(is_approved=True, video__isnull=False).exclude(video="").order_by('-created_at')[:10]


    # Popular listings (likes + views bo'yicha)
    popular_listings = RealEstate.objects.filter(
        is_approved=True
    ).annotate(
        favorites_count=Count('favorites', distinct=True),
        popularity=F('views') + F('favorites_count') * 10
    ).order_by('-popularity')[:6]

    # Kategoriya bo‘yicha sonlar
    type_counts_qs = (
        RealEstate.objects
        .filter(is_approved=True)
        .values('type')
        .annotate(total=Count('id'))
    )
    type_counts = {row['type']: row['total'] for row in type_counts_qs}

    # Kategoriya kartalari uchun tayyor ro‘yxat
    categories = []
    for code, label in PropertyType.choices:
        categories.append({
            'code': code,
            'label': label,
            'count': type_counts.get(code, 0),
            'icon': f'icons/{code}.png',  # static/icons/<code>.png
            'url': reverse('category_list', kwargs={'category_code': code}),
        })

    # Asosiy queryset (prefetch bilan optimallashtirilgan)
    queryset = (
        RealEstate.objects
        .filter(is_approved=True)
        .filter(q_filters, **filters)
        .annotate(average_rating=Avg('ratings__rating'))  # pre-calculate average
        .select_related()
        .prefetch_related('images')
        .only('id', 'title', 'type', 'district', 'status', 'price_usd', 'address', 'area', 'created_at')
        .order_by('-created_at')
    )

    # Paginator
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)  # ✅ Bu Page object
    # Oxirgi 10 ta izoh (approved bo‘lsa filtrla)
    comments = RealEstateComment.objects.select_related("real_estate").order_by("-created_at")[:10]

    context = {
        'properties': properties,
        'type_choices': PropertyType.choices,
        'district_choices': DistrictChoices.choices,
        'condition_choices': ConditionChoices.choices,
        'status_choices': SaleStatus.choices,
        'reels_videos': reels_videos,
        'categories': categories,
        'popular_listings': popular_listings,
        'comments': comments,  # 🔥 qo‘shildi
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
        print("POST kelgan")
        print("Form xatolari:", form.errors)
        if form.is_valid():
            real_estate = form.save(commit=False)   # 👈 commit=False qilib oldik
            real_estate.user = request.user         # 👈 foydalanuvchini avtomatik qo‘shdik
            real_estate.save()

            # Rasmlar
            images = request.FILES.getlist("images")
            for image in images:
                RealEstateImage.objects.create(real_estate=real_estate, image=image)

            # ✅ Telegram kanalga yuborish
            send_real_estate_to_channel(real_estate)

            return redirect("real_estate_list")
    else:
        form = RealEstateForm()

    return render(request, "real_estate/form.html", {"form": form})


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


@login_required
def add_to_favorites(request, pk):
    real_estate = get_object_or_404(RealEstate, pk=pk)
    if request.user in real_estate.likes.all():
        # Agar foydalanuvchi allaqachon qo‘shgan bo‘lsa → olib tashlaymiz
        real_estate.likes.remove(request.user)
    else:
        # Yangi qo‘shish
        real_estate.likes.add(request.user)

    return redirect("real_estate_detail", pk=pk)

@login_required
def toggle_favorite(request, pk):
    real_estate = get_object_or_404(RealEstate, pk=pk)

    if real_estate in request.user.favorite_ads.all():
        request.user.favorite_ads.remove(real_estate)
    else:
        request.user.favorite_ads.add(real_estate)

    return redirect("real_estate_detail", pk=pk)


@login_required
def favorites_list(request):
    """Foydalanuvchi tanlagan sevimli e'lonlari"""
    favorites = request.user.favorite_ads.all()
    return render(request, "listings/favorites_list.html", {"favorites": favorites})

@login_required
def remove_from_favorites(request, pk):
    """Sevimlilardan olib tashlash"""
    real_estate = get_object_or_404(RealEstate, pk=pk)
    request.user.favorite_ads.remove(real_estate)
    return redirect("favorites_list")

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


