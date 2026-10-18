from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Расширенный профиль пользователя для управления подписками"""
    SUBSCRIPTION_CHOICES = [
        ('free', 'Обычный (Free)'),
        ('premium', 'Премиум (Premium)'),
        ('premium_plus', 'Премиум Плюс (Premium+)'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    subscription = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free', verbose_name="Тип подписки")

    def __str__(self):
        return f"Профиль {self.user.username} ({self.get_subscription_display()})"


class Route(models.Model):
    """Модель маршрута путешествия в GoNext (Разработчик: Максим Фирсов)"""
    TRANSPORT_CHOICES = [
        ('car', '🚗 Автомобиль'),
        ('plane', '✈️ Самолёт'),
        ('train', '🚆 Поезд'),
        ('bus', '🚌 Автобус'),
        ('Active', '🚲 Пешком / Велосипед'),
    ]

    CURRENCY_CHOICES = [
        ('BYN', 'BYN (Бел. рубль)'),
        ('USD', 'USD (Доллар)'),
        ('EUR', 'EUR (Евро)'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор маршрута")
    title = models.CharField(max_length=200, verbose_name="Название маршрута")
    country_and_points = models.CharField(max_length=300, verbose_name="Страна и точки маршрута")
    days = models.PositiveIntegerField(default=1, verbose_name="Длительность (дней)")
    
    budget = models.PositiveIntegerField(default=500, verbose_name="Бюджет")
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='BYN', verbose_name="Валюта")
    
    transport = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, default='car', verbose_name="Вид транспорта")
    description = models.TextField(verbose_name="Описание маршрута")
    
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Ссылка на фото (URL)")
    latitude = models.FloatField(default=53.9006, verbose_name="Широта старта")
    longitude = models.FloatField(default=27.5590, verbose_name="Долгота старта")
    waypoints = models.TextField(default='[]', verbose_name="Все точки маршрута (JSON)")
    distance_km = models.PositiveIntegerField(default=0, verbose_name="Протяженность (км)")
    favorites = models.ManyToManyField(User, related_name='favorite_routes', blank=True, verbose_name="Избранное")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Маршрут GoNext"
        verbose_name_plural = "Маршруты GoNext"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.country_and_points})"


class Review(models.Model):
    """Отзывы и оценки к маршрутам"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='reviews', verbose_name="Маршрут")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор отзыва")
    rating = models.PositiveIntegerField(default=5, verbose_name="Оценка (1-5)")
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    def __str__(self):
        return f"Отзыв от {self.author.username} ({self.rating}★)"