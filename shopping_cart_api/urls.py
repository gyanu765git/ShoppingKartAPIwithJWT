from shopping_cart_api import views
from django.urls import path

urlpatterns = [
    path("products/",views.ProductsView.as_view(), name='products'),
    path("categories/",views.CategoryView.as_view(), name='category'),
    path("products/category/<int:category_id>/",views.GetProductByCategoryView.as_view(), name='get-product-by-category-id'),
    path('cart/', views.CartView.as_view(), name='cart-list'),
    path('cart/<int:pk>/', views.CartView.as_view(), name='cart-detail'),
    path("signup/", views.SignUpView.as_view()),
]


