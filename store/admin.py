from django.contrib import admin
from .models import Product, Cart, Registerpage, Feedback

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'price', 'category', 'is_new')
#     list_filter = ('category', 'is_new')
#     search_fields = ('name', 'category')

# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('user', 'product', 'quantity', 'total_price', 'added_at')
#     list_filter = ('user', 'product', 'added_at')
#     search_fields = ('user__username', 'product__name')

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Registerpage)
admin.site.register(Feedback)
