from django.urls import path

from . import views

urlpatterns = [
    path("orders/", views.create_order, name="create-order"),
    path("orders/<int:pk>/", views.order_detail, name="order-detail"),
]
