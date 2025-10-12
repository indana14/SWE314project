from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category, Seller, Product, CartItem


# Custom UserAdmin for your User model
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'phone', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'phone', 'email')

    # use phone instead of username for login
    fieldsets = (
        (None, {'fields': ('phone', 'username', 'email', 'password')}),
        ('Personal info', {'fields': ('address',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )


# Category admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price')
    search_fields = ('name',)


# Seller admin
@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_sold', 'total_earnings')
    search_fields = ('user__username', 'user__phone')


# Product admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'weight', 'price', 'approved')
    list_filter = ('category', 'approved')
    search_fields = ('title', 'description')


# CartItem admin
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'product', 'quantity')
    search_fields = ('buyer__username', 'product__title')
