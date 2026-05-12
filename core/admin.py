from django.contrib import admin
from .models import Category, Entry, Emotion, Milestone

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'is_acknowledged', 'category', 'emotion', 'is_icebreaker')
    list_filter = ('is_acknowledged', 'author', 'category', 'emotion', 'is_icebreaker')
    search_fields = ('content',)

@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'note')
    list_filter = ('date',)
