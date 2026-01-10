from django.contrib import admin

from .models import Category, Post, Location, Comment
# Register your models here.

admin.site.empty_value_display = 'Не задано'
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Location)
admin.site.register(Comment)
