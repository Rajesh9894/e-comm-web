from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # Home
    path('', views.home_view, name='home'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_view, name='product_detail'),

    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),

    #dashboard
    path('dashboard/', TemplateView.as_view(template_name='store/dashboard.html'), name='dashboard'),
    
    # Account
    path('account/', views.account_view, name='account'),
    
    #category
    path('category/<str:category_name>/', views.category_view, name='category'),
    
    # Wishlist
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Buy Now
    path('buy/<int:product_id>/', views.buy_now_view, name='buy_now'),
    
    # Orders
    path('orders/', views.view_orders, name='view_orders'),
    
    # Order Confirmation
    path('order/confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),

    # Product management (frontend)
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/image/', views.product_update_image, name='product_update_image'),
]

