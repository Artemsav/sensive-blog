from tkinter.messagebox import YES

from django.db.models import Count, Prefetch
from django.shortcuts import render

from blog.models import Comment, Post, Tag


def get_related_posts_count(tag):
    return tag.posts.count()


def get_likes_count(post):
    return post.count()


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': len(Comment.objects.filter(post=post)),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_post_optimized(post, comments_amount):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': comments_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_optimized(tag, tag.post_amount) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': len(tag.posts.all()),
    }


def serialize_tag_optimized(tag, post_amount):
    return {
        'title': tag.title,
        'posts_with_tag': post_amount,
    }


def index(request):
    most_popular_posts = Post.objects.popular()
    count_for_id = Post.objects.fetch_with_comments_count()
    fresh_posts = most_popular_posts.order_by('-published_at')
    most_fresh_posts = fresh_posts[:5]
    most_popular_tags = Tag.objects.popular().annotate(post_amount=Count('posts'))[:5] 
    context = {
        'most_popular_posts': [
            serialize_post_optimized(post, count_for_id[post.id]) for post in most_popular_posts.prefetch_related(Prefetch('author'),
                                                                                                                  Prefetch('tags', 
                                                                                                                           queryset=(Tag.objects.annotate(post_amount=Count('posts')))))[:5]
        ],
        'page_posts': [
            serialize_post_optimized(post, count_for_id[post.id]) for post in most_fresh_posts.prefetch_related(Prefetch('author'),
                                                                                                                           Prefetch('tags', 
                                                                                                                           queryset=(Tag.objects.annotate(post_amount=Count('posts')))))
        ],
        'popular_tags': [serialize_tag_optimized(tag, tag.post_amount) for tag in most_popular_tags.prefetch_related('posts')],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    most_popular_posts = Post.objects.popular()
    post = most_popular_posts.annotate(likes_amount=Count('likes')).select_related('author').get(slug=slug)
    comments = Comment.objects.filter(post=post).prefetch_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags.all().annotate(post_amount=Count('posts'))

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_optimized(tag, tag.post_amount) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular().annotate(post_amount=Count('posts'))[:5]

    count_for_id = Post.objects.fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag_optimized(tag, tag.post_amount) for tag in most_popular_tags.prefetch_related('posts')],
        'most_popular_posts': [
            serialize_post_optimized(post, count_for_id[post.id]) for post in most_popular_posts.prefetch_related(Prefetch('author'),
                                                                                                                  Prefetch('tags',
                                                                                                                  queryset=(Tag.objects.annotate(post_amount=Count('posts')))))[:5]
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular().annotate(post_amount=Count('posts'))[:5]

    most_popular_posts = Post.objects.popular()

    related_posts = tag.posts.all()[:20]

    count_for_id = Post.objects.fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag_optimized(tag, tag.post_amount) for tag in most_popular_tags.prefetch_related('posts')],
        'posts': [
            serialize_post_optimized(post, count_for_id[post.id]) for post in related_posts.prefetch_related(Prefetch('author'),
                                                                                                                  Prefetch('tags', 
                                                                                                                            queryset=(Tag.objects.annotate(post_amount=Count('posts')))))
        ],
        'most_popular_posts': [
            serialize_post_optimized(post, count_for_id[post.id]) for post in most_popular_posts.prefetch_related(Prefetch('author'),
                                                                                                                  Prefetch('tags', 
                                                                                                                            queryset=(Tag.objects.annotate(post_amount=Count('posts')))))[:5]
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
