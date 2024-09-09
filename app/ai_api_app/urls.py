from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.category_list, name='home'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:category_id>/titles/', views.title_list, name='title_list'),
    path('categories/<int:category_id>/titles/create/', views.title_create, name='title_create'),
    path('titles/<int:pk>/update/', views.title_update, name='title_update'),
    path('titles/<int:pk>/delete/', views.title_delete, name='title_delete'),
    path('titles/<int:title_id>/responses/', views.response_list, name='response_list'),
    path('titles/<int:title_id>/responses/create/', views.response_create, name='response_create'),
    path('responses/<int:pk>/update/', views.response_update, name='response_update'),
    path('responses/<int:pk>/delete/', views.response_delete, name='response_delete'),
    path('responses/<int:pk>/', views.response_detail, name='response_detail'),
]