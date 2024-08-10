from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.http import Http404
from .models import Movie, Myrating, MyList
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Case, When
import pandas as pd
import json
from django.shortcuts import render, get_object_or_404
from .models import Movie
from .models import Comment
from django.shortcuts import render
from recommend.models import Movie
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.models import User
import datetime
from django.views.decorators.csrf import csrf_exempt
import hashlib
from datetime import datetime
from django.contrib.auth.hashers import make_password
import pandas as pd
from django.shortcuts import render, redirect
from django.http import Http404
from django.db.models import Case, When
from .models import Myrating, Movie
import pandas as pd
from django.db.models import Case, When
from django.shortcuts import render, redirect
from django.http import Http404
from .models import Myrating, Movie
from django.db.models import Case, When
from django.shortcuts import redirect, render
from .models import Myrating, Movie, MyList
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


import json
import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect
from movie_recommender import settings
from .forms import *
from django.http import Http404, JsonResponse
from .models import Movie, Myrating, MyList, Comment
from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Case, When
import pandas as pd
import os
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse



# 应用程序中的views.py文件

from django.http import JsonResponse

from django.http import JsonResponse
from .models import User

import json
from django.core.paginator import Paginator


def delete_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return JsonResponse({'message': '用户已成功删除'})

@csrf_exempt
def save_user_data(request):
    if request.method == 'POST':
        # 获取从客户端传递的用户数据
        user_data = json.loads(request.body)
        # 查询对应的用户对象
        user_id = user_data.get('id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # 创建新用户
            user = User.objects.create(id=user_id)
            user.save()
        # 更新用户字段
        user.id = user_data.get('id')
        user.username = user_data.get('username')
        user.first_name = user_data.get('first_name')
        user.last_name = user_data.get('last_name')
        user.is_superuser = user_data.get('is_superuser')
        user.email = user_data.get('email')
        user.is_active = user_data.get('is_active')
        user.is_staff = user_data.get('is_staff')
        user.date_joined = datetime.now()
        user.last_login =datetime.now()

        password = user_data.get('password')
        hashed_password = make_password(password)
        user.password = hashed_password

        user.save()

        # 返回一个 JSON 响应，表示保存成功
        return JsonResponse({'status': 'success', 'message': '用户数据保存成功！'})
    else:
        # 返回一个 JSON 响应，表示请求方法不支持
        return JsonResponse({'status': 'error', 'message': '请求方法不支持！'}, status=405)


def get_movie_genre_counts():
    # 从 Movie 对象中获取所有电影类型的数据
    genre_counts = Movie.objects.values_list('genre', flat=True)

    # 创建一个空字典来存储电影类型及其对应的数量
    genre_dict = {}
    for genre_list in genre_counts:
        # 假设电影类型以逗号分隔，将其拆分成一个列表
        genres = genre_list.split(',')
        for genre in genres:
            # 去除首尾空格并判断是否为空类型
            genre = genre.strip()
            if genre:
                # 统计每个类型的数量，存储到字典中
                genre_dict[genre] = genre_dict.get(genre, 0) + 1

    # 获取电影类型和对应的数量列表
    genres = list(genre_dict.keys())
    counts = list(genre_dict.values())
    return genres, counts



def movie_list(request):
    genre = request.GET.get('genre')  # 获取传递的电影类型参数
    if genre:  # 如果选择了电影类型
        movies = Movie.objects.filter(genre__contains=genre)  # 使用contains()方法进行模糊匹配
    else:
        movies = Movie.objects.all()  # 如果未选择电影类型，显示所有电影

    paginator = Paginator(movies, 42)  # 每页显示10个电影
    page_number = request.GET.get('page')  # 获取页码参数
    page_obj = paginator.get_page(page_number)  # 获取当前页的对象

    context = {
        'movies': page_obj,  # 将当前页的对象传递给模板
    }
    return render(request, 'recommend/list.html', context)





def primary(request):

    users = User.objects.all()  # 获取所有用户对象
    users_data = []

    # 用于存储每个用户对象的数据
    for user in users:
        user_data = {
            'id': user.id,
            'password': user.password,
            'is_superuser': 'True' if user.is_superuser else 'False',
            'username': user.username,
            'last_login': user.last_login.isoformat(),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_active': 'True' if user.is_active else 'False',
            'date_joined': user.date_joined.isoformat(),
        }


        users_data.append(user_data)


    contextusers = {'users_data': users_data}
        # 将用户数据列表传递给模板作为上下文数据


    movies = Movie.objects.values('douban_rate', 'id')

    douban_rates = [movie['douban_rate'] for movie in movies]
    movie_ids = [movie['id'] for movie in movies]
    genres, counts = get_movie_genre_counts()

    click_counts = []
    movie_names = []
    movie_id=[]
    top_movies = Movie.objects.order_by('-click_count')[:10]
    for movie in top_movies:
        click_counts.append(movie.click_count)
        movie_names.append(movie.title)
        movie_id.append(movie.id)



    return render(request, 'recommend/main.html',
                  {'genres': genres, 'counts': counts, 'movie_names': movie_names,
                   'click_counts': click_counts, 'movie_id': movie_id,'douban_rates': douban_rates, 'movie_ids': movie_ids,
                   'contextusers':contextusers})


def main_movie(request):
    # 获取电影数据
    allMovies = Movie.objects.values('id', 'title', 'genre', 'douban_rate', 'director', 'date', 'description')
    allMovies_list = []
    for allMovie in allMovies:
        allMovies_list.append({
            'id': allMovie['id'],
            'title': allMovie['title'],
            'genre': allMovie['genre'],
            'douban_rate': allMovie['douban_rate'],
            'director': allMovie['director'],
            'date': allMovie['date'],
            'description': allMovie['description'],
        })
    context = {
        'movies': allMovies_list,
    }
    return render(request, 'recommend/main_movie.html', {'context': context})




def getmovie(request):
    # 添加电影
    if request.method == 'POST':
        Mid = request.POST.get('id')  # 获取post请求返回的电影id
        title = request.POST.get('title')  # 获取post请求返回的电影标题
        genre = request.POST.get('genre')  # 获取post请求返回的电影类型
        file = request.FILES.get('movie_logo')  # 获取post请求返回的电影海报
        description = request.POST.get('description')  # 获取post请求返回的电影描述
        # file = request.FILES['movie_logo']

        if file is not None:
            logoName = file.name
            where = os.path.join(settings.MEDIA_ROOT, '', logoName)

        if title:  # 如果返回有标题数据
            # print("id: ", Mid)  # 添加打印语句
            # print("标题: ", title)  # 添加打印语句，打印标题值
            # print("类型: ", genre)  # 添加打印语句，打印类型值
         # 添加打印语句，打印描述值
            movie = Movie.objects.create(id=Mid, title=title, genre=genre, movie_logo=logoName,
                                         description=description)  # 创建新的电影
            movie.save()  # 保存电影信息到数据库
            # 分块保存image
            content = file.chunks()
            with open(where, 'wb') as f:
                for i in content:
                    f.write(i)

    return redirect(reverse('main_movie'))


def deletemovie(request, movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return redirect(reverse('primary'))

    recommend_comments = Comment.objects.filter(movie_id=movie)
    if recommend_comments:
        # 删除包含外键的数据
        recommend_comments.delete()

    movie.delete()
    return redirect(reverse('main_movie'))


@csrf_exempt
def updatemovie(request):
    if request.method == 'POST':
        # 获取表单提交的数据
        Mid = request.POST.get('movie_id')
        title = request.POST.get('title')
        genre = request.POST.get('genre')
        douban_rate = request.POST.get('doubanRate')
        director = request.POST.get('director')
        date = request.POST.get('date')
        description = request.POST.get('description')

        try:
            # 根据movieId获取对应的电影对象
            movie = Movie.objects.get(id=Mid)

            # 更新电影对象的属性值
            movie.title = title
            movie.genre = genre
            movie.douban_rate = douban_rate
            movie.director = director
            movie.date = date
            movie.description = description

            # 保存更新后的电影对象
            movie.save()

            return render(request, 'recommend/main_movie.html')
        except Movie.DoesNotExist:
            # 处理电影对象不存在的情况
            return HttpResponse('电影不存在')




def index(request):
    movie_list = Movie.objects.all()
    paginator = Paginator(movie_list, 42)  # 每页放置42个电影
    page_number = request.GET.get('page')  # 获取页码参数
    page_obj = paginator.get_page(page_number)  # 获取当前页的对象

    query = request.GET.get('q')
    sidebar_movies = Movie.objects.order_by('-click_count')[:10]
    if query:
            movies = Movie.objects.filter(Q(title__icontains=query)).distinct()

            return render(request, 'recommend/list.html', {'page_obj':movies})

    context = {

            'sidebar_movies': sidebar_movies,
            'page_obj': page_obj,
        }

    return render(request, 'recommend/list.html', context)


# Show details of the movie
def detail(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404
    movies = get_object_or_404(Movie, id=movie_id)
    movie = Movie.objects.get(id=movie_id)
    movies.click_count += 1
    movies.save()
    temp = list(MyList.objects.all().values().filter(movie_id=movie_id, user=request.user))
    if temp:
        update = temp[0]['watch']
    else:
        update = False

    if request.method == "POST":
        if 'watch' in request.POST:
            watch_flag = request.POST['watch']
            if watch_flag == 'on':
                update = True
            else:
                update = False
            if MyList.objects.all().values().filter(movie_id=movie_id, user=request.user):
                MyList.objects.all().values().filter(movie_id=movie_id, user=request.user).update(watch=update)
            else:
                q = MyList(user=request.user, movie=movie, watch=update)
                q.save()
            if update:
                messages.success(request, "Movie added to your list!")
            else:
                messages.success(request, "Movie removed from your list!")

        elif 'rating' in request.POST:
            rate = request.POST['rating']
            if Myrating.objects.all().values().filter(movie_id=movie_id, user=request.user):
                Myrating.objects.all().values().filter(movie_id=movie_id, user=request.user).update(rating=rate)
            else:
                q = Myrating(user=request.user, movie=movie, rating=rate)
                q.save()

            messages.success(request, "Rating has been submitted!")

        elif 'comment' in request.POST:
            text=request.POST['comment']
            q = Comment(user=request.user, movie=movie, comment=text)
            q.save()
            messages.success(request, "Comment has been submitted!")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    out1 = list(Myrating.objects.filter(user=request.user.id).values())
    movie_rating = 0
    rate_flag = False
    for each in out1:
        if each['movie_id'] == movie_id:
            movie_rating = each['rating']
            rate_flag = True
            break

#    comments = Comment.objects.filter(movie=movie).values_list('comment', flat=True)
    comments = Comment.objects.filter(movie=movie).values('comment', 'user__username')

    context = {
        'movies': movies,
        'movie': movie,
        'movie_rating': movie_rating,
        'rate_flag': rate_flag,
        'update': update,
        'comments': comments
    }
    return render(request, 'recommend/detail.html', context)



# MyList functionality
def watch(request):

    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404

    movies = Movie.objects.filter(mylist__watch=True,mylist__user=request.user)
    query = request.GET.get('q')

    if query:
        movies = Movie.objects.filter(Q(title__icontains=query)).distinct()
        return render(request, 'recommend/watch.html', {'movies': movies})

    return render(request, 'recommend/watch.html', {'movies': movies})


# To get similar movies based on user rating

# 计算电影相似度



def get_similar(movie_id, rating, corrMatrix_expanded, genre_weight):
    # 根据 movie_id 获取电影类型
    movie_genres = Movie.objects.get(id=movie_id).genre
    genres = [genre.strip() for genre in movie_genres.split(',')]
    # 获取电影的相似评分

    similar_ratings = (corrMatrix_expanded[movie_id])*(rating-1)+1
    similar_ratings = similar_ratings.to_dict()
    similar_ratings = pd.DataFrame.from_dict(similar_ratings, orient='index', columns=['similar_rating'])
    similar_ratings['movie_id'] = similar_ratings.index

    similar_ratings = similar_ratings[['movie_id', 'similar_rating']]

    result_df = pd.merge(similar_ratings, genre_weight, on='movie_id')
    # 执行列相乘操作
    result_df['similar_ratings'] = result_df['similar_rating'] * result_df['weight']

    result_df = result_df[['movie_id', 'similar_ratings']].sort_values(by='similar_ratings', ascending=False).head(100)

    # 返回相似评分结果
    return result_df


def recommend(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404

    # 获取用户的电影评分数据
    movie_rating = pd.DataFrame(list(Myrating.objects.all().values()))

    new_user = movie_rating.user_id.unique().shape[0]
    current_user_id = request.user.id

    if current_user_id > new_user:
        movie = Movie.objects.get(id=19)
        q = Myrating(user=request.user, movie=movie, rating=0)
        q.save()

    userRatings = movie_rating.pivot_table(index=['user_id'], columns=['movie_id'], values='rating')
    userRatings = userRatings.fillna(0, axis=1)

    corrMatrix = userRatings.corr(method='pearson')


    # 创建一个4007x4007的零矩阵
    corrMatrix_expanded = pd.DataFrame(0, index=range(1, 4008), columns=range(1, 4008))

    # 获取原始矩阵的维度
    orig_rows, orig_cols = corrMatrix.shape

    # 获取原始矩阵的行列索引
    orig_index = corrMatrix.index
    orig_columns = corrMatrix.columns

    # 将原始矩阵的值复制到扩展矩阵的对应位置
    corrMatrix_expanded.loc[orig_index, orig_columns] = corrMatrix.values



    user = pd.DataFrame(list(Myrating.objects.filter(user=request.user).values())).drop(['user_id', 'id'], axis=1)
    user_filtered = [tuple(x) for x in user.values]

    movie_id_watched = [each[0] for each in user_filtered]

    similar_movies = pd.DataFrame()

    # 可选的电影类型列表
    genres_list = ['剧情', '喜剧', '爱情', '动作', '动画', '科幻', '惊悚', '情色', '恐怖', '武侠', '歌舞', '历史', '战争', '古装', '音乐', '同性', '灾难',
                   '传记', '家庭', '冒险', '奇幻', '犯罪', '悬疑', '儿童', '运动', '西部', '真人秀', '黑色电影', '舞台艺术', '戏曲']

    # 获取当前用户评分较高和较低的电影类型
    high_rated_genres = [genre.strip() for genres in
                         Movie.objects.filter(myrating__user=request.user, myrating__rating__gte=4).values_list('genre',
                                                                                                                flat=True)
                         for genre in genres.split(',')]

    low_rated_genres = [genre.strip() for genres in
                        Movie.objects.filter(myrating__user=request.user, myrating__rating__lt=2).values_list('genre',
                                                                                                              flat=True)
                        for genre in genres.split(',')]

    # 建立字典存放电影类型和对应的出现次数
    high_genre_counts = {genre: 0 for genre in genres_list}
    low_genre_counts = {genre: 0 for genre in genres_list}
    # 计算每个类型的出现次数
    for movie_genres in high_rated_genres:
            high_genre_counts[movie_genres] += 1


    for movie_genres in low_rated_genres:
            low_genre_counts[movie_genres] += 1
    # 计算电影类型对评分的修正权值
    high_genre_weights = {genre: count / sum(high_genre_counts.values()) for genre, count in high_genre_counts.items()}
    low_genre_weights = {genre: count / sum(low_genre_counts.values()) for genre, count in low_genre_counts.items()}

    # 筛选出前八名
    top_high_rated_genres = sorted(high_genre_counts, key=high_genre_counts.get, reverse=True)[:8]
    top_low_rated_genres = sorted(low_genre_counts, key=low_genre_counts.get, reverse=True)[:8]

    # 权值赋值范围
    weight_range = 1.7 - 1.2


    for genre in top_high_rated_genres:
        count = high_genre_counts[genre]
        if count!=0:
            weight = 1.2 + (count / sum(high_genre_counts.values())) * weight_range
            high_genre_weights[genre] = weight

    for genre in top_low_rated_genres:
        count = low_genre_counts[genre]
        if count != 0:
            weight = 1.2 + (count / sum(low_genre_counts.values())) * weight_range
            low_genre_weights[genre] = weight

    top_high = dict(sorted(high_genre_weights.items(), key=lambda x: x[1], reverse=True)[:8])
    top_low = dict(sorted(low_genre_weights.items(), key=lambda x: x[1], reverse=True)[:8])

    movies = Movie.objects.all()
    data = []
    print(top_high)
    print(top_low)
    for movie in movies:
        genres = [genre.strip() for genre in movie.genre.split(',')]
        weight = 1
        for genre in genres:
            if genre in top_high_rated_genres:
                if top_high[genre] != 0:
                    weight *= top_high[genre]
            if genre in top_low_rated_genres:
                if top_low[genre]!=0:
                    weight /= top_low[genre]

        data.append({
            'movie_id': movie.id,
            'weight': weight
        })

    genre_weight = pd.DataFrame(data)

    for movie_id, rating in user_filtered:
        similar_movies = similar_movies.append(get_similar(movie_id, rating, corrMatrix_expanded,
                                                           genre_weight),ignore_index=True)

    # 按照相似评分的和排序，获取推荐电影列表

    movies_id = similar_movies.groupby('movie_id').sum().reset_index()
    movies_id = movies_id.sort_values(by='similar_ratings', ascending=False).head(100)

    movies_id_recommend = movies_id[~movies_id['movie_id'].isin(movie_id_watched)]

    movie_ids = list(movies_id_recommend['movie_id'])  # 提取 movies_id_recommend DataFrame 中的电影ID
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(movie_ids)])
    movie_list = list(Movie.objects.filter(id__in=movie_ids).order_by(preserved)[:10])
    context = {'movie_list': movie_list}

    # 返回推荐电影列表
    return render(request, 'recommend/recommend.html', context)

# Register user
def signUp(request):
    form = UserForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")

    context = {'form': form}

    return render(request, 'recommend/signUp.html', context)


# Login User
def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                if user.is_superuser:
                    return redirect("primary")
                else:
                    return redirect("index")
            else:
                return render(request, 'recommend/login.html', {'error_message': 'Your account is disabled'})
        else:
            return render(request, 'recommend/login.html', {'error_message': 'Invalid Login'})

    return render(request, 'recommend/login.html')


# Logout user
def Logout(request):
    logout(request)
    return redirect("login")


