from .models import RealEstateRating, RealEstateComment, RealEstate, RealEstateImage, PropertyType, DistrictChoices, SaleStatus, ConditionChoices
from django.contrib.auth.forms import AuthenticationForm
from django import forms

class RealEstateForm(forms.ModelForm):
    class Meta:
        model = RealEstate
        exclude = ("user", "latitude", "longitude")
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label


class RealEstateImageForm(forms.ModelForm):
    class Meta:
        model = RealEstateImage
        fields = ('image',)


class RealEstateSearchForm(forms.Form):
    title = forms.CharField(label='Uy nomi', required=False)
    type = forms.ChoiceField(label='Xonadon turi', choices=[('', 'Tanlang')] + list(PropertyType.choices), required=False)
    district = forms.ChoiceField(label='Rayon', choices=[('', 'Tanlang')] + list(DistrictChoices.choices), required=False)
    status = forms.ChoiceField(label='Status', choices=[('', 'Tanlang')] + list(SaleStatus.choices), required=False)
    address = forms.CharField(label='Manzil', required=False)
    rooms = forms.IntegerField(label='Xonalar soni', required=False)
    area = forms.DecimalField(label='Umumiy maydon (m²)', required=False)
    price_usd = forms.DecimalField(label='Narx (USD)', required=False)
    condition = forms.ChoiceField(label='Holati', choices=[('', 'Tanlang')] + list(ConditionChoices.choices), required=False)
    furniture = forms.BooleanField(label='Mebelli', required=False)
    appliances = forms.BooleanField(label='Texnika bilan', required=False)


class RatingForm(forms.ModelForm):
    class Meta:
        model = RealEstateRating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = RealEstateComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Login")
    password = forms.CharField(label="Parol", widget=forms.PasswordInput)



from .models import PropertyType, DistrictChoices, ConditionChoices
from django import forms

# class EvaluationForm(forms.Form):
#     property_type = forms.ChoiceField(
#         choices=PropertyType.choices,
#         label="Тип недвижимости",
#         widget=forms.Select(attrs={"class": "form-select", "id": "id_property_type"})
#     )
#
#
#     district = forms.ChoiceField(
#         choices=DistrictChoices.choices,
#         label="Район",
#         widget=forms.Select(attrs={"class": "form-select", "id": "id_district"})
#     )
#
#     # umumiy maydonlar (ko‘pchiligi turga qarab ko‘rinadi)
#     area = forms.DecimalField(required=False, max_digits=9, decimal_places=2, label="Площадь (м²)",
#                               widget=forms.NumberInput(attrs={"class": "form-control", "id": "id_area"}))
#     land_area = forms.DecimalField(required=False, max_digits=9, decimal_places=2, label="Площадь участка (сотки)",
#                                    widget=forms.NumberInput(attrs={"class": "form-control", "id": "id_land_area"}))
#     rooms = forms.IntegerField(required=False, label="Количество комнат",
#                                widget=forms.NumberInput(attrs={"class": "form-control", "id": "id_rooms"}))
#     floor = forms.IntegerField(required=False, label="Этаж",
#                                widget=forms.NumberInput(attrs={"class": "form-control", "id": "id_floor"}))
#     total_floors = forms.IntegerField(required=False, label="Этажность",
#                                       widget=forms.NumberInput(attrs={"class": "form-control", "id": "id_total_floors"}))
#
#     condition = forms.ChoiceField(choices=ConditionChoices.choices, required=False, label="Состояние",
#                                   widget=forms.Select(attrs={"class": "form-select", "id": "id_condition"}))
#
#     has_furniture = forms.BooleanField(required=False, label="С мебелью", widget=forms.CheckboxInput())
#     has_appliances = forms.BooleanField(required=False, label="С техникой", widget=forms.CheckboxInput())
#     has_parking = forms.BooleanField(required=False, label="Есть парковка", widget=forms.CheckboxInput())
#     has_renters = forms.BooleanField(required=False, label="Есть арендаторы", widget=forms.CheckboxInput())
#
#     facade = forms.CharField(required=False, label="Фасад", widget=forms.TextInput(attrs={"class": "form-control"}))
#     building_name = forms.CharField(required=False, label="Название новостройки", widget=forms.TextInput(attrs={"class": "form-control"}))
#     line = forms.CharField(required=False, label="Линия", widget=forms.TextInput(attrs={"class": "form-control"}))
#
#     rent_price = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label="Арендная плата (USD)",
#                                     widget=forms.NumberInput(attrs={"class": "form-control", "id": "id_rent_price"}))
#
#     # 🔥 Yangi qo‘shilgan maydonlar
#     base_price_m2 = forms.DecimalField(
#         label="Цена за 1 м² (USD)", required=False, initial=800,
#         widget=forms.NumberInput(attrs={"class": "form-control", "id": "id_base_price_m2"})
#     )
#     base_price_sotix = forms.DecimalField(
#         label="Цена за 1 сотку (USD)", required=False, initial=1000,
#         widget=forms.NumberInput(attrs={"class": "form-control", "id": "id_base_price_sotix"})
#     )
#
#     images = forms.FileField(
#         label="Rasmlar yuklash",
#         widget=forms.ClearableFileInput(attrs={
#             "class": "form-control",
#             "id": "id_images",
#             "multiple": True  # HTML5 multiple input
#         }),
#         required=False
#     )

from django import forms
from .models import Property, PropertyImage
from django import forms

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "property_type", "district", "area", "land_area", "rooms",
            "floor", "total_floors", "condition", "has_furniture",
            "has_appliances", "has_parking", "has_renters",
            "facade", "building_name", "line", "rent_price",
            "base_price_m2", "base_price_sotix"
        ]
        widgets = {
            "property_type": forms.Select(attrs={"class": "form-select", "id": "id_property_type"}),
            "district": forms.Select(attrs={"class": "form-select", "id": "id_district"}),
            "area": forms.NumberInput(attrs={"class": "form-control", "id": "id_area"}),
            "land_area": forms.NumberInput(attrs={"class": "form-control", "id": "id_land_area"}),
            "rooms": forms.NumberInput(attrs={"class": "form-control", "id": "id_rooms"}),
            "floor": forms.NumberInput(attrs={"class": "form-control", "id": "id_floor"}),
            "total_floors": forms.NumberInput(attrs={"class": "form-control", "id": "id_total_floors"}),
            "condition": forms.Select(attrs={"class": "form-select", "id": "id_condition"}),
            "facade": forms.TextInput(attrs={"class": "form-control"}),
            "building_name": forms.TextInput(attrs={"class": "form-control"}),
            "line": forms.TextInput(attrs={"class": "form-control"}),
            "rent_price": forms.NumberInput(attrs={"class": "form-control", "id": "id_rent_price"}),
            "base_price_m2": forms.NumberInput(attrs={"class": "form-control", "id": "id_base_price_m2"}),
            "base_price_sotix": forms.NumberInput(attrs={"class": "form-control", "id": "id_base_price_sotix"}),
        }
