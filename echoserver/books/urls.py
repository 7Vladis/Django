from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('edit/<int:pk>', views.edit_book, name='edit_book'),
    path('delete/<int:pk>', views.delete_book, name='delete_book'),
    path('add/', views.add_book, name='add_book'),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('create-order/', views.create_order, name='create_order'),
    path('orders/', views.orders_view, name='orders'),
    path('remove-from-cart/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/<int:order_id>/delete/', views.delete_order, name='delete_order'),
]