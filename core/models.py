from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"

    def __str__(self):
        return self.name

class Emotion(models.Model):
    name = models.CharField(max_length=50, verbose_name="Duygu Adı")

    class Meta:
        verbose_name = "Duygu"
        verbose_name_plural = "Duygular"

    def __str__(self):
        return self.name

class Milestone(models.Model):
    title = models.CharField(max_length=150, verbose_name="Dönüm Noktası (Örn: İlk Tanışma)")
    note = models.TextField(blank=True, null=True, verbose_name="Özel Not")
    date = models.DateField(verbose_name="Tarih")

    class Meta:
        verbose_name = "Dönüm Noktası"
        verbose_name_plural = "Dönüm Noktaları"
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%d %B')})"

class Entry(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries', verbose_name="Yazar")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries', verbose_name="Kategori")
    emotion = models.ForeignKey(Emotion, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries', verbose_name="Duygu")
    content = models.TextField(verbose_name="İçerik")
    image = models.ImageField(upload_to='entries/', blank=True, null=True, verbose_name="Görsel")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    is_acknowledged = models.BooleanField(default=False, verbose_name="Okundu/Onaylandı")
    is_icebreaker = models.BooleanField(default=False, verbose_name="Buzkıran (Önemli)")
    
    class Meta:
        ordering = ['-created_at'] # En yeniler en üstte
        verbose_name = "Gönderi"
        verbose_name_plural = "Gönderiler"

    def __str__(self):
        return f"{self.author.username} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
