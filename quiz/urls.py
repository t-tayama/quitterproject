from django.urls import path
from . import views

app_name = 'quiz'


urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),

    path('list/', views.QuizListView.as_view(), name='list'),
    path('category/<int:category_pk>', views.QuizCategoryView.as_view(), name='category'),
    path('tag/<int:tag_pk>', views.QuizTagView.as_view(), name='tag'),
    path('search/', views.QuizSearchView.as_view(), name='search'),

    path('detail/<int:quiz_pk>', views.detail, name='detail'),
    path('answer/<int:quiz_pk>', views.answer, name='answer'),
    path('result/<int:quiz_pk>', views.result, name='result'),

    path('create/', views.create, name='create'),
    path('edit/<int:quiz_pk>', views.edit, name='edit'),
    path('delete/<int:quiz_pk>', views.delete, name='delete'),

    path('mypage/', views.mypage, name='mypage'),

    path('contact/', views.contact, name='contact'),
    path('postok/', views.postok, name='postok'),

    path('report/<int:quiz_pk>', views.report, name='report'),
]



