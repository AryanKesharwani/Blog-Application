from django.urls import path
from .views import (
    PostListView,
    PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView, ToggleLikeView,
    PostByCategoryView, HomePageView
)

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post_list'),
    path('', HomePageView.as_view(), name='home'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/new/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('posts/<int:pk>/like/', ToggleLikeView.as_view(), name='post_like'),
    path('categories/<str:category_name>/', PostByCategoryView.as_view(), name='posts_by_category'),
]
