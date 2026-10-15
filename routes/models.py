from django.db import models
from django.contrib.auth.models import User


class Route(models.Model):
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
    
    latitude = models.FloatField(default=53.9006, verbose_name="Широта")
    longitude = models.FloatField(default=27.5590, verbose_name="Долгота")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Маршрут GoNext"
        verbose_name_plural = "Маршруты GoNext"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.country_and_points})"