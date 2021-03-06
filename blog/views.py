from django.shortcuts import render, redirect
from django.http import HttpResponse
from blog.models import Post,Tag,Category
from accounts.models import UserProfileInfo
from comments.models import Comment,Reply
from blog.forms import UserForm,UserProfileInfoForm
from . import forms
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth.models import User


# Create your views here.

#Index page with latest posts
def index(request):
    post_list = Post.objects.filter(status='published').order_by('published_date')

    paginator = Paginator(post_list, 5) # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    my_dict = {'posts':posts}
    return render(request, 'blog/index.html', context=my_dict)

#Post details page
def post_details(request, pk):
    post = Post.objects.get(id=pk)
    post_tags = post.tag.all()
    post_categories = post.category.all()

    next_posts = Post.objects.filter(published_date__gt=post.published_date)
    if(next_posts):
        next_post = next_posts [0]
    else:
        next_post = None

    previous_posts = Post.objects.filter(published_date__lt=post.published_date)
    if(previous_posts):
        previous_post = previous_posts [previous_posts.count()-1]
    else:
        previous_post = None

    post_id = post.id
    comments = post.comments.filter(is_approved=True)



    my_dict = {'post_tags':post_tags,'post_categories':post_categories, 'post':post, 'comments':comments, 'next_post':next_post, 'previous_post':previous_post}
    return render(request, 'blog/single.html', context=my_dict)

#All posts by published year
def archeive_posts(request, year):
    post_list = Post.objects.filter(published_date__year = year)
    paginator = Paginator(post_list, 5) # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {'year':year,'posts':posts}
    return render(request, 'blog/archeive.html', context)

#All posts by post tag
def archeive_posts_by_tag(request, tag):
    tag = Tag.objects.get(text=tag)
    post_list = tag.tags.all()

    paginator = Paginator(post_list, 5) # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {'posts':posts}
    return render(request, 'blog/archeive.html', context)

#All posts by post category
def archeive_posts_by_category(request, category):
    category = Category.objects.get(text=category)
    post_list = category.categories.all()
    paginator = Paginator(post_list, 5) # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {'posts':posts}
    return render(request, 'blog/archeive.html', context)

#All posts by a specific author
def archeive_posts_by_author(request, username):
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author.id)

    paginator = Paginator(post_list, 5) # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {'posts':posts}
    return render(request, 'blog/archeive.html', context)

#All posts by published_date
def archeive_posts_by_date(request, year, month, day):
    post_list = Post.objects.filter(published_date__year=year, published_date__month=month, published_date__day=day)

    paginator = Paginator(post_list, 5) # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {'posts':posts}
    return render(request, 'blog/archeive.html', context)

#Search Result
def search_view(request):
        if request.method == 'GET' :
            search_query = request.GET.get('search_box')
            tag_list = Tag.objects.filter(text__contains=search_query)
            cat_list = Category.objects.filter(text__contains=search_query)
            post_list = Post.objects.filter(title__contains=search_query ).distinct() | Post.objects.filter(content__contains=search_query ).distinct() | Post.objects.filter(tag__id__in=tag_list).distinct() | Post.objects.filter(category__id__in=cat_list).distinct()

        paginator = Paginator(post_list, 5) # Show 5 posts per page
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        context = {'posts':posts}
        return render(request, 'blog/archeive.html', context)

#Comment submission by logged in user
@login_required
def submit_comment(request):

    if request.method == 'POST' :

        comment_title = request.POST.get('comment_title')
        comment_content = request.POST.get('comment_content')
        post_id = request.POST.get('post_id')
        current_user = request.user
        profile = UserProfileInfo.objects.get(user=current_user)

        c = Comment()
        c.post = Post.objects.get(id=post_id)
        c.content = comment_content
        c.author = UserProfileInfo.objects.get(id=profile.id)
        c.published_date = datetime.now()
        c.save()

    return HttpResponseRedirect(reverse('blog:post_details', args=(post_id, )))

#Reply submission by logged in user
@login_required
def submit_reply(request):

    if request.method == 'POST' :
        post_id = request.POST.get('post_id')
        reply_title = request.POST.get('reply_title')
        reply_content = request.POST.get('reply_content')
        comment_id = request.POST.get('comment_id')
        current_user = request.user
        profile = UserProfileInfo.objects.get(user=current_user)

        r = Reply()
        r.comment = Comment.objects.get(id=comment_id)
        r.content = reply_content
        r.author = UserProfileInfo.objects.get(id=profile.id)
        r.published_date = datetime.now()
        r.save()

    return HttpResponseRedirect(reverse('blog:post_details', args=(post_id, ))) # have to work here




#Log out from blog
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

#Authentication and Login
def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active and ( user.is_superuser or user.is_staff):
                login(request, user)
                return HttpResponseRedirect(reverse('backend:posts'))
            elif user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("User is not active.Please Contact  to Admin")

        else:
            print('Someone tried to login and failed!')
            print('User Name {} and Password {}'.format(username, password))
            return HttpResponse("Invalid login detials provieded")
    else:
        return render(request,'blog/login.html', {})


#New user registration
def registration(request):
    registered = False

    if request.method == 'POST' :
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit = False)
            profile.user = user

            if 'profile_pic' in request.FILES :
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()

            registered = True

        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request,'blog/sign-up.html',
                    {'user_form':user_form,
                    'profile_form':profile_form,
                    'registered':registered})
