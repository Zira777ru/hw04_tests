from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Post, Group, User
from .constants import POST_PER_PAGE


def paginator(posts, request):
    paginator = Paginator(posts, POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = paginator(posts, request)
    context = {
        'page_obj': page_obj,
    }
    template = 'posts/index.html'
    return render(request, template, context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    page_obj = paginator(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related('group').all()
    page_obj = paginator(posts, request)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    page_obj = get_object_or_404(Post, pk=post_id)
    context = {
        'page_obj': page_obj,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    template = 'posts/create_post.html'
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post.pk)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.pk)
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    template = 'posts/create_post.html'
    return render(request, template, context)
