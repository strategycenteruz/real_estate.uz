from decimal import Decimal, ROUND_HALF_UP
from .models import PropertyType, ConditionChoices, DistrictChoices

# district_coeffs: kodlaringizdagi qiymatlar bilan mos keltiring
DISTRICT_COEFFS = {
    DistrictChoices.CHILANZAR: Decimal("1.10"),
    DistrictChoices.MIRABAD: Decimal("1.20"),
    DistrictChoices.MIRZO_ULUGBEK: Decimal("1.18"),
    DistrictChoices.SERGELI: Decimal("0.95"),
    DistrictChoices.YUNUSABAD: Decimal("1.15"),
    DistrictChoices.YASHNABOD: Decimal("1.15"),
    DistrictChoices.YAKKASAROY: Decimal("1.25"),
    DistrictChoices.ALMAZAR: Decimal("1.08"),
    DistrictChoices.UCHTEPA: Decimal("1.07"),
    DistrictChoices.SHAYXANTOHUR: Decimal("1.12"),
    DistrictChoices.BEKTEMIR: Decimal("0.90"),
}

DISTRICT_COMMENTS = {
    DistrictChoices.CHILANZAR: "район с развитой инфраструктурой, стабильный спрос.",
    DistrictChoices.MIRABAD: "центр города, престижная локация.",
    DistrictChoices.MIRZO_ULUGBEK: "удобное расположение, хорошие школы и транспорт.",
    DistrictChoices.SERGELI: "доступное жильё, немного ниже спрос.",
    DistrictChoices.YUNUSABAD: "близость к центру, популярный район.",
    DistrictChoices.YASHNABOD: "развивающийся район, средний спрос.",
    DistrictChoices.YAKKASAROY: "очень престижный, высокая цена.",
    DistrictChoices.ALMAZAR: "спокойный жилой район.",
    DistrictChoices.UCHTEPA: "доступные цены, спальный район.",
    DistrictChoices.SHAYXANTOHUR: "исторический центр, высокий спрос.",
    DistrictChoices.BEKTEMIR: "промышленная зона, цены ниже.",
}
def _to_decimal(val):
    try:
        if val in (None, ""):
            return Decimal("0")
        # if it's already Decimal, str() keeps representation
        return Decimal(str(val))
    except Exception:
        return Decimal("0")

def calculate_estimate(cleaned_data):
    """Return (final_price: Decimal, details: list[str]).
    cleaned_data comes from EvaluationForm.cleaned_data.
    """
    details = []

    # Bazaviy narxlar (adjust these to your market)
    # base per m2 for apartments/new: (you can tune)

    # BASE_M2 = Decimal("800")        # suggested base for urban apartments
    # BASE_SOTIX = Decimal("1000")    # per sotix for land (example)

    # foydalanuvchi kiritgan qiymatlarni olish
    BASE_M2 = _to_decimal(cleaned_data.get("base_price_m2")) or Decimal("800")
    BASE_SOTIX = _to_decimal(cleaned_data.get("base_price_sotix")) or Decimal("10000")

    ptype = cleaned_data.get("property_type")
    district = cleaned_data.get("district")
    condition = cleaned_data.get("condition")

    # read numeric fields safely
    area = _to_decimal(cleaned_data.get("area")) # m²
    land_area = _to_decimal(cleaned_data.get("land_area"))# sotix
    rooms = int(cleaned_data.get("rooms") or 0)
    floor = int(cleaned_data.get("floor") or 0)
    total_floors = int(cleaned_data.get("total_floors") or 0)
    rent_price = _to_decimal(cleaned_data.get("rent_price"))

    has_furniture = bool(cleaned_data.get("has_furniture"))
    has_appliances = bool(cleaned_data.get("has_appliances"))
    has_parking = bool(cleaned_data.get("has_parking"))
    has_renters = bool(cleaned_data.get("has_renters"))

    # 1) base price depending on type
    if ptype == PropertyType.UCHASTOK:
        # land price by sotix
        price = land_area * BASE_SOTIX
        details.append(f"Площадь участка: {land_area} соток × {BASE_SOTIX}$ = {price:.2f}$")
    elif ptype == PropertyType.NOVOSTROYKA:
        price = BASE_M2 * area
        details.append(f"Площадь: {area} м² × {BASE_M2}$ = {price:.2f}$ (новостройка базовый)")
    elif ptype == PropertyType.VTORICHKA:
        price = BASE_M2 * area
        details.append(f"Площадь: {area} м² × {BASE_M2}$ = {price:.2f}$ (вторичка базовый)")
    elif ptype == PropertyType.KOMMERCHESKOE:
        # commercial often pricier per m2
        price = (BASE_M2 * Decimal("1.3")) * area
        details.append(f"Площадь (коммерч.): {area} м² × {BASE_M2 * Decimal('1.3')}$ = {price:.2f}$")
    elif ptype == PropertyType.ARENDA:
        # For rent we prefer rent_price if provided, else estimate as small %

        if rent_price and rent_price > 0:
            # treat rent_price as monthly USD -> annualize for comparable valuation
            price = rent_price * Decimal("12")
            details.append(f"Арендная плата: {rent_price}$/мес → год: {price:.2f}$")
        else:
            # fallback: small % of sale value (we estimate sale then take 5%)
            assumed_sale = BASE_M2 * area
            price = (assumed_sale * Decimal("0.05"))
            details.append(f"Аренда (оценка): 5% от {assumed_sale:.2f}$ = {price:.2f}$")
    else:
        price = Decimal("0")
        details.append("Тип недвижимости не определен")

    # 2) type-specific fine tuning
    # e.g., new buildings get small premium, secondary slightly different
    if ptype == PropertyType.NOVOSTROYKA:
        # premium for new building, possible discounts for high line vs low etc.
        price *= Decimal("1.12")  # +12%
        details.append("Новостройка: +12% (премия)")
    if ptype == PropertyType.VTORICHKA:
        # second-hand slight - or vary by condition (handled later)
        price *= Decimal("1.00")
        details.append("Вторичка: базовая корректировка")

    # 3) condition (repair)
    if condition == ConditionChoices.EVROREMONT:
        price *= Decimal("1.25")
        details.append("Евроремонт: +25%")
    elif condition == ConditionChoices.CHISTYY:
        price *= Decimal("1.15")
        details.append("Чистый ремонт: +15%")
    elif condition == ConditionChoices.TREBUET_REMONT:
        price *= Decimal("0.80")
        details.append("Требует ремонт: -20%")
    elif condition == ConditionChoices.BEZ_REMONT:
        details.append("Без ремонта: без надбавки")

    # 4) rooms / layout adjustments (example logic)
    # more rooms on same area -> premium; simple rule: if rooms>2 add small bonus
    if rooms >= 3 and ptype in (PropertyType.NOVOSTROYKA, PropertyType.VTORICHKA):
        price *= Decimal("1.05")
        details.append(f"Больше комнат ({rooms}): +5%")

    # 5) floor adjustments (1st floor or top floor discount)
    if ptype in (PropertyType.NOVOSTROYKA, PropertyType.VTORICHKA):
        if floor == 1:
            price *= Decimal("0.95")
            details.append("1 этаж: -5%")
        elif total_floors and floor == total_floors:
            price *= Decimal("0.95")
            details.append("Последний этаж: -5%")

    # 6) district coefficient (use provided mapping)
    coeff = DISTRICT_COEFFS.get(district)
    if coeff:
        district_name = dict(DistrictChoices.choices).get(district)
        comment = DISTRICT_COMMENTS.get(district, "")
        price *= coeff
        details.append(f"Коэффициент района ({district_name}): x{coeff} → {comment}")

    # 7) extras (furniture, appliances, parking, renters)
    if has_furniture:
        price += Decimal("5000")
        details.append("Мебель: +5000$")
    if has_appliances:
        price += Decimal("4000")
        details.append("Техника: +4000$")
    if has_parking and ptype == PropertyType.KOMMERCHESKOE:
        price += Decimal("2000")
        details.append("Парковка (коммерч.): +2000$")
    if has_renters and ptype == PropertyType.KOMMERCHESKOE:
        # if premises already rented, it's more valuable
        price *= Decimal("1.08")
        details.append("Арендаторы (коммерч.): +8%")

    # round result to 2 decimals
    final = price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return final, details



def format_currency(value: Decimal) -> str:
    """Format: 220 000.00 $"""
    return f"{value:,.2f}".replace(",", " ") + " $"