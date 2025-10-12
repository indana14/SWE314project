from django.contrib import admin
from django.urls import path
from scrappy import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.landing, name="landing"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("home/", views.home, name="home"),
    path("buyer/", views.buyer_page, name="buyer"),
    path("seller/", views.seller_page, name="seller"),
    path("cart/", views.cart_page, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("about/", views.about, name="about"),
    path("logout/", views.logout_view, name="logout"),
]

# ✅ Add this for media file serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
