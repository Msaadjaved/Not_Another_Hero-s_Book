from django.urls import path
from . import views, views_author, views_auth

urlpatterns = [
    # ========== Public Pages ==========
    path('', views.home, name='home'),
    path('story/<int:story_id>/', views.story_detail, name='story_detail'),
    path('story/<int:story_id>/play/', views.play_story, name='play_story'),
    path('story/<int:story_id>/choice/<int:choice_id>/', views.make_choice, name='make_choice'),
    path('story/<int:story_id>/ending/<int:ending_page_id>/', views.story_ending, name='story_ending'),
    path('statistics/', views_auth.statistics, name='statistics'),
    
    # ========== Authentication (Level 16) ==========
    path('register/', views_auth.register, name='register'),
    path('login/', views_auth.user_login, name='login'),
    path('logout/', views_auth.user_logout, name='logout'),
    path('profile/', views_auth.profile, name='profile'),
    
    # ========== Author Tools ==========
    path('author/', views_author.author_dashboard, name='author_dashboard'),
    path('author/story/create/', views_author.create_story, name='create_story'),
    path('author/story/<int:story_id>/edit/', views_author.edit_story, name='edit_story'),
    path('author/story/<int:story_id>/delete/', views_author.delete_story, name='delete_story'),
    path('author/story/<int:story_id>/page/create/', views_author.create_page, name='create_page'),
    path('author/page/<int:page_id>/edit/', views_author.edit_page, name='edit_page'),
    path('author/page/<int:page_id>/delete/', views_author.delete_page, name='delete_page'),
    path('author/page/<int:page_id>/choice/create/', views_author.create_choice, name='create_choice'),
    path('author/choice/<int:choice_id>/delete/', views_author.delete_choice, name='delete_choice'),
    
    # ========== Ratings & Reports (Level 18) ==========
    path('story/<int:story_id>/rate/', views_auth.rate_story, name='rate_story'),
    path('rating/<int:rating_id>/delete/', views_auth.delete_rating, name='delete_rating'),
    path('story/<int:story_id>/report/', views_auth.report_story, name='report_story'),
    
    # ========== Admin (Level 16/18) ==========
    path('admin-dashboard/', views_auth.admin_dashboard, name='admin_dashboard'),
    path('moderate/story/<int:story_id>/suspend/', views_auth.suspend_story, name='suspend_story'),
    path('moderate/story/<int:story_id>/unsuspend/', views_auth.unsuspend_story, name='unsuspend_story'),
    path('moderate/report/<int:report_id>/update/', views_auth.update_report_status, name='update_report_status'),
    
    # ========== Visualizations (Level 18) ==========
    path('story/<int:story_id>/tree/', views_auth.story_tree_view, name='story_tree'),
    path('play/<int:play_id>/path/', views_auth.player_path_view, name='player_path'),
]