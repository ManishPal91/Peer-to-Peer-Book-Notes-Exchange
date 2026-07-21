from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('', views.dashboard, name='dashboard'),
    
    path('listings/', views.listing_list, name='listing_list'),
    path('listings/create/', views.listing_create, name='listing_create'),
    path('listings/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listings/<int:pk>/edit/', views.listing_update, name='listing_update'),
    path('listings/<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    
    path('listings/<int:pk>/wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('listings/<int:pk>/wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    path('matches/', views.match_center, name='match_center'),
    path('matches/<int:match_id>/schedule/', views.schedule_pickup, name='schedule_pickup'),
    path('matches/<int:match_id>/verify/', views.verify_pickup, name='verify_pickup'),
]
