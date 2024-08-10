from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signUp, name='signup'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('<int:movie_id>/', views.detail, name='detail'),
    path('watch/', views.watch, name='watch'),
    path('recommend/', views.recommend, name='recommend'),
    path('movie-list/', views.movie_list, name='movie_list'),
    path('index/', views.index, name='index'),
    path('main/', views.primary, name='primary'),
    path('get-movie-genre-counts/', views.get_movie_genre_counts, name='get_movie_genre_counts'),
    path('save_user_data/', views.save_user_data, name='save_user_data'),
    path('api/users/<int:user_id>/', views.delete_user_view, name='delete_user'),

    path('main_movie/', views.main_movie, name='main_movie'),
    path('getmovie/', views.getmovie, name='getmovie'),
    path('deletemovie/<int:movie_id>/', views.deletemovie, name='deletemovie'),
    path('updatemovie/', views.updatemovie, name='updatemovie'),
]