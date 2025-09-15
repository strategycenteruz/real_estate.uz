from django.contrib import admin
from .models import RealEstate, RealEstateImage
from .models import RealEstateVideo

class RealEstateImageInline(admin.TabularInline):
    model = RealEstateImage
    extra = 1

class RealEstateVideoInline(admin.TabularInline):  # <--- Yangi qo‘shildi
    model = RealEstateVideo
    extra = 1


@admin.register(RealEstate)
class RealEstateAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'type', 'address', 'rooms', 'price_usd', 'status', 'is_approved')
    list_filter = ('type', 'status', 'is_approved', 'condition', 'address')
    search_fields = ('title', 'address', 'orientir', 'description')
    list_editable = ('is_approved', 'status')
    readonly_fields = ('created_at',)

    inlines = [RealEstateImageInline, RealEstateVideoInline]  # <--- Ikkalasi birga


    fieldsets = (
        ('Asosiy ma’lumotlar', {
            'fields': ('title', 'type', 'district', 'status', 'is_approved', 'address', 'orientir')
        }),
        ('Tavsif va tafsilotlar', {
            'fields': (
                'rooms', 'floor', 'total_floors', 'area', 'condition',
                'has_balcony', 'balcony_size', 'has_terrace',
                'cadastral', 'furniture', 'appliances',
                'price_usd', 'mortgage_available', 'description', 'phone', 'video',
            )
        }),
        ('Yaratilgan sana', {
            'fields': ('created_at',)
        })
    )


@admin.register(RealEstateVideo)
class RealEstateVideoAdmin(admin.ModelAdmin):
    list_display = ('real_estate', 'video')



