from django.urls import path
from django.contrib.auth import views as auth_views
from .views import custom_logout, profile
from . import views


urlpatterns = [
    path('', views.real_estate_list, name='real_estate_list'),
    path('create/', views.real_estate_create, name='real_estate_create'),
    path('update/<int:pk>/', views.real_estate_update, name='real_estate_update'),
    path('delete/<int:pk>/', views.real_estate_delete, name='real_estate_delete'),
    path('realestate/all/', views.all_ads_view, name='all_ads'),
    path('realestate/<int:pk>/', views.real_estate_detail, name='real_estate_detail'),
    path('realestate/reels/', views.reels_view, name='reels_view'),
    path("realestate/<int:pk>/rate/", views.rate_real_estate, name="rate_real_estate"),
    path("realestate/<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("category/<str:category_code>/", views.category_list, name="category_list"),

    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("profile/", profile, name="profile"),
    path("logout/", custom_logout, name="logout"),

    path("favorites/add/<int:pk>/", views.add_to_favorites, name="add_to_favorites"),
    path("favorites/remove/<int:pk>/", views.remove_from_favorites, name="remove_from_favorites"),

    path("realestate/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("map/", views.real_estate_map, name="real_estate_map"),

    path("statistics/", views.statistics_view, name="statistics"),
    path("estimate/", views.estimate_view, name="estimate"),

    path("estimate/", views.estimate_page, name="estimate_page"),
    path("send_to_realtor/", views.send_to_realtor, name="send_to_realtor"),

    path("api/real-estates/", views.real_estate_api, name="real_estate_api"),
]
