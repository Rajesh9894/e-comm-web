from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from .models import Product, Registerpage, Cart, Wishlist, Order, Feedback

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

        # Field validation
        if not username:
            errors.append("Username is required.")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long.")
        elif User.objects.filter(username=username).exists():
            errors.append("Username already exists.")

        if not email:
            errors.append("Email is required.")
        elif '@' not in email or '.' not in email:
            errors.append("Please enter a valid email address.")
        elif User.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        if not password:
            errors.append("Password is required.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters long.")

        if not confirm_password:
            errors.append("Please confirm your password.")
        elif password != confirm_password:
            errors.append("Password and Confirm Password do not match.")

        if errors:
            return render(request, 'store/register.html', {
                'errors': errors,
                'username': username,
                'email': email,
            })

        try:
            # Create Django user
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Also create Registerpage record (if needed for other functionality)
            Registerpage.objects.create(
                username=username,
                email=email,
                password=make_password(password),
            )

            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
            
        except Exception as e:
            errors.append("An error occurred during registration. Please try again.")
            return render(request, 'store/register.html', {
                'errors': errors,
                'username': username,
                'email': email,
            })

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
            return redirect('dashboard')
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
    category = request.GET.get('category', '').strip()

    # Start with all products
    products = Product.objects.all()
    
    # Apply category filter if provided
    if category and category != 'all':
        products = products.filter(category__iexact=category)
    
    # Apply search filter if provided
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query)
        )

    # Calculate average rating for each product
    for product in products:
        product.average_rating = Feedback.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0

    return render(request, 'store/product_list.html', {
        'products': products, 
        'query': query,
        'selected_category': category
    })

@login_required(login_url='login')
def product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get existing feedback for this product
    feedback_list = Feedback.objects.filter(product=product)
    
    if request.method == 'POST':
        # Handle feedback submission
        comment = request.POST.get('comment', '').strip()
        rating = request.POST.get('rating', 5)
        
        errors = []
        
        if not comment:
            errors.append("Please enter your feedback comment.")
        elif len(comment) < 10:
            errors.append("Feedback comment must be at least 10 characters long.")
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                errors.append("Please select a valid rating between 1 and 5 stars.")
        except (ValueError, TypeError):
            errors.append("Please select a valid rating.")
        
        # Check if user already submitted feedback for this product
        existing_feedback = Feedback.objects.filter(user=request.user, product=product).first()
        if existing_feedback:
            errors.append("You have already submitted feedback for this product.")
        
        if errors:
            return render(request, 'store/product.html', {
                'product': product,
                'feedback_list': feedback_list,
                'errors': errors,
                'comment': comment,
                'rating': rating
            })
        
        try:
            # Create new feedback
            feedback = Feedback.objects.create(
                user=request.user,
                product=product,
                comment=comment,
                rating=rating
            )
            messages.success(request, "Thank you for your feedback!")
            return redirect('product_detail', product_id=product.id)
            
        except Exception as e:
            errors.append("An error occurred while submitting your feedback. Please try again.")
            return render(request, 'store/product.html', {
                'product': product,
                'feedback_list': feedback_list,
                'errors': errors,
                'comment': comment,
                'rating': rating
            })
    
    return render(request, 'store/product.html', {
        'product': product,
        'feedback_list': feedback_list
    })

# ---------------- CART ----------------
@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    quantity = min(quantity, 10)
    
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity = min(cart_item.quantity + 1, 10)
        cart_item.save()
        messages.success(request, f"Updated {product.name} quantity in your cart!")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f"{product.name} added to your cart!")
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

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
            # Limit quantity to maximum 10
            new_quantity = min(new_quantity, 10)
            cart_item.quantity = new_quantity
            cart_item.save()
    return redirect('view_cart')

@login_required(login_url='login')
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')

#------------------- CATEGORY -------------------
@login_required(login_url='login')
def category_view(request, category_name):
    print(f"Category requested: {category_name}")  # Debug print
    
    # Get all distinct categories for debugging
    all_categories = Product.objects.values_list('category', flat=True).distinct()
    print(f"Available categories in DB: {list(all_categories)}")
    
    # Handle 'all' category to show all products
    if category_name.lower() == 'all':
        products = Product.objects.all()
        category_name = 'All Products'
    else:
        # Filter products by category (case-insensitive)
        products = Product.objects.filter(category__iexact=category_name)
        print(f"Products found: {products.count()}")  # Debug print
    
    return render(request, 'store/category.html', {
        'category_name': category_name, 
        'products': products,
        'all_categories': all_categories  # Pass for debugging
    })


# ---------------- WISHLIST ----------------
@login_required(login_url='login')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is already in wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, 
        product=product
    )
    
    if created:
        messages.success(request, f"{product.name} added to your wishlist!")
    else:
        messages.info(request, f"{product.name} is already in your wishlist!")
    
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required(login_url='login')
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product=product)
    wishlist_item.delete()
    messages.success(request, f"{product.name} removed from your wishlist!")
    return redirect(request.META.get('HTTP_REFERER', 'view_wishlist'))

@login_required(login_url='login')
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

def wishlist_count(request):
    if request.user.is_authenticated:
        return {'wishlist_count': Wishlist.objects.filter(user=request.user).count()}
    return {'wishlist_count': 0}

# ---------------- BUY NOW ----------------
@login_required(login_url='login')
def buy_now_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is in cart and get the quantity
    cart_quantity = 1  # Default quantity
    try:
        cart_item = Cart.objects.get(user=request.user, product=product)
        cart_quantity = cart_item.quantity
    except Cart.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        quantity = int(request.POST.get('quantity', 1))
        
        # Basic validation
        errors = []
        if not name:
            errors.append("Name is required.")
        if not mobile:
            errors.append("Mobile number is required.")
        elif not mobile.isdigit():
            errors.append("Mobile number must contain only numbers.")
        elif len(mobile) < 10 or len(mobile) > 15:
            errors.append("Mobile number must be between 10 and 15 digits.")
        if not email or '@' not in email:
            errors.append("Valid email is required.")
        if quantity < 1 or quantity > 10:
            errors.append("Quantity must be between 1 and 10.")
        
        if errors:
            return render(request, 'store/buy_now.html', {
                'product': product,
                'errors': errors,
                'name': name,
                'mobile': mobile,
                'email': email,
                'address': address,
                'quantity': quantity
            })
        
        # Create order
        try:
            order = Order.objects.create(
                user=request.user,
                product=product,
                customer_name=name,
                email=email,
                mobile=mobile,
                address=address if address else None,
                quantity=quantity,
                total_amount=product.final_price * quantity,
                order_status='Pending'
            )
            # Redirect to order confirmation page
            return redirect('order_confirmation', order_id=order.id)
            
        except Exception as e:
            errors.append("An error occurred while placing your order. Please try again.")
            return render(request, 'store/buy_now.html', {
                'product': product,
                'errors': errors,
                'name': name,
                'mobile': mobile,
                'email': email,
                'address': address,
                'quantity': quantity
            })
    
    return render(request, 'store/buy_now.html', {
        'product': product,
        'quantity': cart_quantity
    })


# ---------------- ACCOUNT ----------------
@login_required(login_url='login')
def account_view(request):
    """Display user account information"""
    user = request.user
    return render(request, 'store/account.html', {'user': user})

# ---------------- ORDERS ----------------
@login_required(login_url='login')
def view_orders(request):
    """Display all orders for the current user"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})

# ---------------- ORDER CONFIRMATION ----------------
@login_required(login_url='login')
def order_confirmation_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST' and 'feedback' in request.POST:
        # Handle feedback submission
        feedback_text = request.POST.get('feedback_text', '').strip()
        errors = []
        
        if not feedback_text:
            errors.append("Please enter your feedback comment.")
        elif len(feedback_text) < 10:
            errors.append("Feedback comment must be at least 10 characters long.")
        
        # Check if user already submitted feedback for this product
        existing_feedback = Feedback.objects.filter(user=request.user, product=order.product).first()
        if existing_feedback:
            errors.append("You have already submitted feedback for this product.")
        
        if errors:
            return render(request, 'store/order_confirmation.html', {
                'order': order,
                'errors': errors,
                'feedback_text': feedback_text
            })
        
        try:
            # Create new feedback
            feedback = Feedback.objects.create(
                user=request.user,
                product=order.product,
                comment=feedback_text,
                rating=5  # Default 5-star rating for order confirmation feedback
            )
            messages.success(request, "Thank you for your feedback!")
            return redirect('order_confirmation', order_id=order.id)
            
        except Exception as e:
            errors.append("An error occurred while submitting your feedback. Please try again.")
            return render(request, 'store/order_confirmation.html', {
                'order': order,
                'errors': errors,
                'feedback_text': feedback_text
            })
    
    return render(request, 'store/order_confirmation.html', {'order': order})
