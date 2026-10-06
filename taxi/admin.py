from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Order, Profile, Tariff

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price", "per_km", "seats", "position")
    list_editable = ("base_price", "per_km", "position")

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("first_name",)}),)
    list_display = ("username", "first_name", "is_staff")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "car_model", "car_plate", "is_available")
    list_filter = ("role", "is_available")
    search_fields = ("user__username", "user__first_name", "phone", "car_plate")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "pickup", "dropoff", "passenger", "driver", "tariff", "price", "status", "created_at")
    list_filter = ("status", "tariff")
    list_editable = ("driver", "status")
    search_fields = ("phone", "pickup", "dropoff")