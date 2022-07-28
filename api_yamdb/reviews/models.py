from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year, validate_username


class User(AbstractUser):
    """Кастомная модель пользователя"""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    USER_ROLES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор')
    ]

    role = models.CharField(
        max_length=50,
        choices=USER_ROLES,
        verbose_name='права пользователя',
        help_text='укажите уровень прав',
        default=USER
    )
    username = models.SlugField(
        validators=[validate_username],
        verbose_name='Имя пользователя',
        unique=True,
        null=True,
    )
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    """Модель категории"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        help_text='Дайте название категории',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Адрес для страницы категории',
        help_text=(
            'Укажите адрес для страницы категории. '
            'Используйте только латиницу, цифры, '
            'дефисы и знаки подчёркивания'
        ),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Genre(models.Model):
    """Модель жанр"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        help_text='Дайте название жанра',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Адрес для страницы жанра',
        help_text=(
            'Укажите адрес для страницы жанра. '
            'Используйте только латиницу, цифры, '
            'дефисы и знаки подчёркивания'
        ),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']


class Title(models.Model):
    """Модель произведения"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения',
        help_text='Дайте название произведению',
    )
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='Год',
        help_text='Укажите год произведения',
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг',
        null=True,
        default=None
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения',
        help_text='Укажите описание произведения.',
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        related_name='titles',
        on_delete=models.SET_NULL,
        verbose_name='Категория',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']


class GenreTitle(models.Model):
    """Связующая модель жанра и произведения."""
    genre = models.ForeignKey(
        Genre, null=True, on_delete=models.CASCADE, verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение'
    )

    def __str__(self):
        return f'{self.title}, жанр: {self.genre}'


class Review(models.Model):
    """Модель отклика."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведения',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )
    text = models.TextField(
        null=False,
        verbose_name='Текст отзыва',
        help_text='Введите текст отзыва',
    )
    score = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(10, 'Оценка не может быть больше 10'),
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
        ],
        help_text='Поставьте оценку от 1 до 10',
        verbose_name='Оценка',
    )

    def __str__(self):
        return f'Отзыв {self.text} на {self.title}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review'
            )
        ]


class Comment(models.Model):
    """Модель комментария."""
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )

    def __str__(self):
        return f'Комментарий от автора(заменить) к {self.review}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']
