from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Dictionarydan key bo‘yicha qiymat olish"""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return None
