from django.contrib import admin
from django.urls import path
from mystore import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    path('',views.index ),
    # path('profile',views.profile),
    path('login',views.login,name='login'),
    path('signin',views.signin),
    path('inser_details',views.inser_details),
    path('check_email/', views.check_email, name='check_email'),
    path('login_user',views.login_user,name='login_user'),
    path('check_password/',views.password_check),
    path('logout', views.logout, name='logout'),

    #dashboard's
    path('client_profile/',views.client_profile,name="client_profile"),
    path('admin_dashboard',views.admin_dashboard ,name="admin_dashboard"),
    path('support_dashboard',views.support_dashboard,name='support_dashboard'),

    path('product_management/',views.product_management,name='product_management'),
    path('add_product/', views.add_product, name='add_product'),
    # mystore/urls.py

    path('products/', views.product_view, name='product_view'),
    
    path('get_product/<int:product_id>/', views.get_product, name='get_product'),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),

    path('buy_product/<int:product_id>/', views.buy_product, name='buy_product'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    path('verify_warranty/', views.verify_warranty, name='verify_warranty'),

    path('create_ticket/', views.create_ticket, name='create_ticket'),
    path('user_management',views.user_management,name='user_management'),
    path('admin_orders',views.admin_orders,name='admin_orders'),
    path('ticket',views.ticket,name='ticket',),
    path('assign_staff/', views.assign_staff, name='assign_staff'),
    path('ticket_details/', views.ticket_details, name='ticket_details'),
    path("update_ticket_status/", views.update_ticket_status, name="update_ticket_status"),
    path("update_order_status/", views.update_order_status, name="update_order_status"),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
