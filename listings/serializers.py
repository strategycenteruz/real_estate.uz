from rest_framework import serializers
from .models import RealEstate, RealEstateImage

class RealEstateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateImage
        fields = ['id', 'image']

class RealEstateSerializer(serializers.ModelSerializer):
    images = RealEstateImageSerializer(many=True, read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)

    class Meta:
        model = RealEstate
        fields = [
            'id', 'title', 'type', 'type_display', 'is_urgent',
            'location', 'orientir', 'rooms', 'floor', 'total_floors',
            'area', 'condition', 'condition_display', 'balcony_size',
            'has_terrace', 'has_pool', 'has_waterfall', 'bathrooms',
            'cadastral', 'furniture', 'appliances',
            'price_usd', 'mortgage_available', 'description', 'phone',
            'images', 'created_at', 'latitude', 'longitude',
        ]


class RealEstateCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = RealEstate
        fields = '__all__'

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        real_estate = RealEstate.objects.create(**validated_data)
        for image in images:
            RealEstateImage.objects.create(real_estate=real_estate, image=image)
        return real_estate
