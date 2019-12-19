from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Comment
from .forms import Email, CommentForm
from django.core.mail import send_mail


# Create your views here.

def post_list(request):
    posts = Post.objects.filter(status="published")
    paginator = Paginator(posts, 2)
    page = request.GET.get('page')
    try:
        listed_posts = paginator.page(page)
    except PageNotAnInteger:
        listed_posts = paginator.page(1)
    except EmptyPage:
        listed_posts = paginator.page(paginator.num_pages)

    context = {
        'posts': listed_posts,
    }
    return render(request, 'post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             )
    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    context = {
        'post': post,
        'year': year,
        'month': month,
        'day': day,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'post/detail.html', context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = Email(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} send ({}) from: {} '.format(cd['name'], cd['email'], post.title)
            message = 'Read post "{}" on the site{}\n\nComment add by {}:{}'.format(post.title, post_url,
                                                                                    cd['name'], cd['comments'])
            send_mail(subject, message, 'mik4llpl@gmail.com', [cd['to']])
            sent = True
    else:
        form = Email()

    context = {
        'post': post,
        'form': form,
        'sent': sent,
    }
    return render(request, 'post/share.html', context)
