# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.shortcuts import redirect
from django.db.models import Count
from settle.steam_news import get_news
from settle.models import Post, Comment, Tag, User
from settle.forms import SignupForm
from django import forms
from django.utils import timezone

# Create your views here.


def redirectHome(request):
    response = redirect('/settle')
    return response


def index(request, template="settle/index.html"):
    context_dict = {}
    post_list = Post.objects.all().order_by("-date_submitted")
    page = request.GET.get('page', 1)
    paginator = Paginator(post_list, 3)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'settle/index.html', {'posts': posts})


def feed(request):
    context_dict = {}

    # need to filter this for feed
    post_list = Post.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(post_list, 3)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'settle/feed.html', {'posts': posts})


def upload(request):
    context_dict = {}

    game_tags = Tag.objects.filter(is_game_tag=True).filter(
        is_pending=False).order_by("text")
    info_tags = Tag.objects.filter(is_game_tag=False).filter(
        is_pending=False).order_by("text")
    context_dict["game_tags"] = game_tags
    context_dict["info_tags"] = info_tags

    return render(request, 'settle/upload.html', context=context_dict)


def suggest_tag(request):
    context_dict = {}
    return render(request, 'settle/suggest-tag.html', context=context_dict)


def post(request, post_id):
    context_dict = {}
    result_list = []

    post = Post.objects.filter(id=post_id)[0]

    all_comments = Comment.objects.filter(parent_post=post_id).annotate(
        num_likes=Count('liking_users')).order_by('-num_likes')
    comment_count = len(all_comments)

    comm_pagin = Paginator(all_comments, 3)  # show 3 comments at once

    # get page no. from URL, or 1 if just loading in
    page = request.GET.get('page', 1)

    try:
        comments = comm_pagin.page(page)  # get the given page of comments
    except PageNotAnInteger:
        comments = comm_pagin.page(1)  # default to 1st page if not a number
    except EmptyPage:
        # default to last page if too big
        comments = comm_pagin.page(comm_pagin.num_pages)

    # testing - when we actually make it, we'll parameterise the app id

    app_id = post.game_tag.steamAppId

    if app_id != 0:
        result_list = get_news(app_id, 10)
    # result_list = get_news(440, 5)
    context_dict["result_list"] = result_list
    context_dict["post"] = post
    context_dict["comments"] = comments
    context_dict["comment_count"] = comment_count

    return render(request, 'settle/post.html', context=context_dict)


def signup(request):
    # Used to tell us if signup was successful
    registered = False

    if request.method == 'POST':
        signup_form = SignupForm(data=request.POST)

        if signup_form.is_valid():
            newUser = signup_form.save(commit=False)
            newUser.date_joined = timezone.now()

            newUser.save()

            registered = True

        else:
            print(signup_form.errors)
    else:
        signup_form = SignupForm()

    return render(request, 'settle/register.html', {'form': signup_form, 'registered': registered})
