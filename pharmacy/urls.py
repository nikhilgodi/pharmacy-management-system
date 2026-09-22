from django.urls import path
from . import views


urlpatterns = [

    # =========================
    # LOGIN / LOGOUT
    # =========================

    path('login/', views.login_page, name='login'),
    path('login-user/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout'),


    # =========================
    # SHOPKEEPER REGISTRATION
    # =========================

    path(
        'shopkeeper-register/',
        views.shopkeeper_register_page,
        name='shopkeeper_register'
    ),

    path(
        'shopkeeper-register-user/',
        views.shopkeeper_register_user,
        name='shopkeeper_register_user'
    ),


    # =========================
    # ADMIN / SHOPKEEPER
    # =========================

    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'add-medicine/',
        views.add_medicine,
        name='add_medicine'
    ),

    path(
        'add-medicine-page/',
        views.add_medicine_page,
        name='add_medicine_page'
    ),

    path(
        'edit-medicine-page/<int:medicine_id>/',
        views.edit_medicine_page,
        name='edit_medicine_page'
    ),

    path(
        'edit-medicine/<int:medicine_id>/',
        views.edit_medicine,
        name='edit_medicine'
    ),

    path(
        'delete-medicine/<int:medicine_id>/',
        views.delete_medicine,
        name='delete_medicine'
    ),


    # =========================
    # CUSTOMER
    # =========================

    path(
        'user-dashboard/',
        views.user_dashboard,
        name='user_dashboard'
    ),

    path(
        'order-medicine/<int:medicine_id>/',
        views.order_medicine,
        name='order_medicine'
    ),

    path(
        'my-orders/',
        views.my_orders,
        name='my_orders'
    ),


    # =========================
    # ORDER MANAGEMENT
    # =========================

    path(
        'orders-management/',
        views.orders_management,
        name='orders_management'
    ),

    path(
        'update-order-status/<int:order_id>/',
        views.update_order_status,
        name='update_order_status'
    ),
]