from django.urls import path
from . import views
from .views import create_post
from .views import delete_post
from .views import Settings, change_password ,category_posts, about, contact, EditPostView

urlpatterns = [
    path('', views.Index, name='index'),
    path('dashboard/', views.DashboardView, name='dashboard'),
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('settings/', views.Settings, name='settings'),
    path('account-settings/', views.AccountSettings, name='account-settings'),
    path('change-password/', change_password, name='change_password'),
    path('blog-detail/<str:slug>/', views.ArticleDetail, name='detail'),
    path('category/<slug:category_slug>/', category_posts, name='category_posts'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('create-post/', create_post, name='create_post'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit-post/<slug:slug>/', EditPostView, name='edit-post'),
]
