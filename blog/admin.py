from django.contrib import admin
from blog.models import Post, Tag, Comment


class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ('likes',)


class CommentsAdmin(admin.ModelAdmin):
    raw_id_fields = ('post', 'author')


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Comment, CommentsAdmin)
