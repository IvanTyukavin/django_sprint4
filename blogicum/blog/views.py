from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from .forms import PostForm, UserForm, CommentForm
from .models import Post, Category, Location, User, Comment


class Index(ListView):
    """Главная страница - лента записей (index.html)"""
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related(
            'author', 'category', 'location'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


class PostDetailView(DetailView):
    """Детальная страница поста (detail.html)"""
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryView(ListView):
    """Публикации в категории (category.html)"""
    template_name = 'blog/category.html'
    paginate_by = 10
    
    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

        queryset = Post.objects.filter(
            category=self.category,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related(
            'author', 'category', 'location'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(ListView):
    """Страница пользователя (profile.html)"""
    template_name = 'blog/profile.html'
    paginate_by = 10
    
    def get_queryset(self):
        profile = get_object_or_404(User, username=self.kwargs['username'])
        queryset = Post.objects.select_related(
            'author', 'location', 'category'
        ).annotate(
            comment_count=Count('comments')
        ).filter(author=profile).order_by('-pub_date')
        
        if self.request.user != profile:
            queryset = queryset.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание новой публикации (create.html)"""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование публикации (create.html)"""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление публикации (create.html)"""
    model = Post
    template_name = 'blog/create.html'
    context_object_name = 'form'
    success_url = reverse_lazy('blog:index')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.get_object()}
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля (user.html)"""
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk) 

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.pk}
        )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.pk}
        )
