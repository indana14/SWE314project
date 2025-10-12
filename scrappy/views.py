from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, CartItem, User, Seller, Category


# Landing page
def landing(request):
    return render(request, "landing.html")


# Login page
def login_view(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid phone number or password.")

    return render(request, "login.html")


# Signup page
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")

        if User.objects.filter(phone=phone).exists():
            messages.error(request, "A user with this phone number already exists.")
            return render(request, "signup.html")

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                phone=phone,
                password=password
            )
            user.address = address
            user.save()

            # Create a Seller profile automatically
            Seller.objects.get_or_create(user=user)

            login(request, user)
            return redirect("home")

        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")

    return render(request, "signup.html")


def home(request):
    return render(request, "home.html")


# Buyer page
def buyer_page(request):
    products = Product.objects.filter(approved=True)
    categories = Category.objects.all()

    category_filter = request.GET.get("category")
    if category_filter:
        products = products.filter(category__id=category_filter)

    return render(request, "buyer.html", {"products": products, "categories": categories})


# Seller Dashboard / Product Upload
@login_required
def seller_page(request):
    # Ensure seller profile exists
    seller, created = Seller.objects.get_or_create(user=request.user)

    if request.method == "POST":
        title = request.POST["title"]
        category_id = request.POST["category"]
        description = request.POST["description"]
        weight = float(request.POST["weight"])
        available_date = request.POST["available_date"]
        image = request.FILES.get("image")

        # Get category & price
        category = get_object_or_404(Category, id=category_id)
        estimated_price = weight * category.base_price

        Product.objects.create(
            seller=seller,
            title=title,
            category=category,
            description=description,
            weight=weight,
            available_date=available_date,
            image=image,
            price=estimated_price,
            approved=False  # Admin must approve
        )

        seller.update_stats()  # update totals
        messages.success(request, f"Product submitted! Estimated price: ${estimated_price:.2f}")
        return redirect("seller")

    products = seller.products.all()
    categories = Category.objects.all()
    return render(request, "seller.html", {"categories": categories, "products": products, "seller": seller})


def logout_view(request):
    logout(request)
    return redirect("landing")


# Add to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.create(buyer=request.user, product=product, quantity=1)
    return redirect("cart")


# Cart page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem, Product


@login_required
def cart_page(request):
    cart_items = CartItem.objects.filter(buyer=request.user)

    # Calculate totals
    subtotal = sum(item.subtotal() for item in cart_items)
    shipping = 10.00 if subtotal > 0 else 0.00
    tax = round(subtotal * 0.08, 2)
    total = subtotal + shipping + tax

    # Update quantity (if + or – clicked)
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        action = request.POST.get("action")

        item = get_object_or_404(CartItem, id=item_id, buyer=request.user)

        if action == "increase":
            item.quantity += 1
            item.save()
        elif action == "decrease" and item.quantity > 1:
            item.quantity -= 1
            item.save()
        elif action == "remove":
            item.delete()
            messages.info(request, "Item removed from cart.")
        return redirect("cart")

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "total": total,
        "remaining_for_free_shipping": max(0, 100 - subtotal),
    }

    return render(request, "cart.html", context)

# Checkout page
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(buyer=request.user)
    subtotal = sum(item.subtotal() for item in cart_items)
    shipping = 10.00 if subtotal > 0 else 0.00
    tax = round(subtotal * 0.08, 2)
    total = subtotal + shipping + tax

    if request.method == "POST":
        # Example: After confirming payment, clear the cart
        cart_items.delete()
        messages.success(request, "Your order has been placed successfully!")
        return redirect("home")

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "total": total,
    }
    return render(request, "checkout.html", context)



# About page
def about(request):
    return render(request, "AboutUs.html")
