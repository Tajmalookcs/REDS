from django import template
from apps.core.utils import amount_in_words, amount_in_words_urdu

register = template.Library()


@register.filter
def to_words(value):
    return amount_in_words(value)


@register.filter
def to_words_urdu(value):
    return amount_in_words_urdu(value)