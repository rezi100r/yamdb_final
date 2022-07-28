from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Функция проверки корректности указанного года"""
    if value > timezone.now().year:
        raise ValidationError(f'Год {value} больше текущего.')


def validate_username(value):
    """Проверка username"""
    if value == 'me':
        raise ValidationError('me нельзя использовать как имя пользователя')
