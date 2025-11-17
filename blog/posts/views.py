"""
Views for handling blog post operations such as listing, creating, viewing,
editing, deleting, commenting, and liking posts.
"""

from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from django.http import HttpResponseRedirect
from .models import Post, Category, Tag, Like
from .forms import CommentForm
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
User = get_user_model()
users = User.objects.prefetch_related('posts').all()


# List all blog posts
class PostListView(ListView):
    """
    Displays a paginated list of all blog posts with optional search functionality.
    """
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True).order_by('-created_at')
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(author__username__icontains=query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PostDetailView(DetailView):
    """
    Displays a single blog post with comment form and like status.
    """
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """
        Adds the comment form and like status to the context.
        """
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comment_form'] = CommentForm()

        if self.request.user.is_authenticated:
            context['has_liked'] = post.likes.filter(user=self.request.user).exists()
        else:
            context['has_liked'] = False

        return context

    def post(self, request, *args, **kwargs):
        """
        Handles submission of a new comment.
        """
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = self.object
            comment.save()
        return redirect('post_detail', pk=self.object.pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Allows authenticated users to create a new blog post.
    """
    model = Post
    fields = ['title', 'content', 'image', 'category', 'tags', 'is_published']
    template_name = 'post_form.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        """
        Assigns the current user as the author before saving the post.
        """
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, View):
    """
    Custom view to update an existing blog post using a manual HTML form.
    """
    template_name = 'post_custom_update.html'
    success_url = reverse_lazy('post_list')

    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        categories = Category.objects.all()
        tags = Tag.objects.all()
        return render(request, self.template_name, {
            'post': post,
            'categories': categories,
            'tags': tags
        })

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.is_published = 'is_published' in request.POST

        if 'image' in request.FILES:
            post.image = request.FILES['image']

        category_id = request.POST.get('category')
        post.category = Category.objects.get(pk=category_id) if category_id else None

        post.save()

        tag_ids = request.POST.getlist('tags')
        post.tags.set(tag_ids)

        return redirect(self.success_url)


class PostDeleteView(LoginRequiredMixin, View):
    """
    Custom view to delete a blog post with confirmation.
    """
    template_name = 'post_custom_delete.html'

    def get(self, request, pk):
        """
        Renders the delete confirmation page.
        """
        post = get_object_or_404(Post, pk=pk)
        return render(request, self.template_name, {'object': post})

    def post(self, request, pk):
        """
        Deletes the post after user confirms.
        """
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return redirect('post_list')


class ToggleLikeView(View):
    """
    Allows a user to like or unlike a post.
    """
    def post(self, request, pk):
        """
        Toggles the like status for a post by the current user.
        """
        post = Post.objects.get(pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        return HttpResponseRedirect(reverse('post_detail', args=[pk]))


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


class PostByCategoryView(ListView):
    """
    Displays blog posts filtered by a specific category.
    """
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        category_name = self.kwargs.get('category_name')
        return Post.objects.filter(
            is_published=True,
            category__name=category_name
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = self.kwargs.get('category_name')
        return context


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['trending_posts'] = Post.objects.filter(
            tags__name__iexact='trending', is_published=True
        ).order_by('-created_at')[:3]

        context['latest_posts'] = Post.objects.filter(
            is_published=True
        ).order_by('-created_at')[:6]

        # Get top 4 users with most posts, break tie with date_joined
        context['users'] = User.objects.filter(
            is_active=True
        ).annotate(
            post_count=Count('posts')
        ).order_by('-post_count', 'date_joined')[:4]

        return context