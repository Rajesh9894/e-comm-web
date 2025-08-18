from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Product, RegisterUser, Cart

# ---------------- HOME ----------------
@login_required(login_url='login')
def home_view(request):
    featured_products = Product.objects.filter(is_new=True)[:4]
    return render(request, 'store/home.html', {'featured_products': featured_products})

# ---------------- REGISTER ----------------
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        errors = []

        if not username or not email or not password or not confirm_password:
            errors.append("All fields are required.")

        if password != confirm_password:
            errors.append("Password and Confirm Password do not match.")

        if User.objects.filter(username=username).exists():
            errors.append("Username already exists.")

        if User.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        if errors:
            return render(request, 'store/register.html', {
                'errors': errors,
                'username': username,
                'email': email
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        RegisterUser.objects.create(username=username, email=email, password=make_password(password)
        )

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'store/register.html')

# ---------------- LOGIN ----------------
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'store/login.html', {'error': 'Both fields are required'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'store/login.html', {'error': 'Invalid username or password'})

    return render(request, 'store/login.html')

# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

# ---------------- PRODUCTS ----------------
@login_required(login_url='login')
def product_list(request):
    query = request.GET.get('q', '').strip()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        products = Product.objects.all()

    return render(request, 'store/product_list.html', {'products': products, 'query': query})

@login_required(login_url='login')
def product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product.html', {'product': product})

# ---------------- CART ----------------
@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('product_list')

def cart_count(request):
    if request.user.is_authenticated:
        return {'cart_count': Cart.objects.filter(user=request.user).count()}
    return {'cart_count': 0}

@login_required(login_url='login')
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required(login_url='login')
def update_cart_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if request.method == "POST":
        new_quantity = int(request.POST.get("quantity", 1))
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
    return redirect('view_cart')

@login_required(login_url='login')
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')




