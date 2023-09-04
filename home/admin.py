from django.contrib import admin
from .models import Post, Comment, Vote


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'slug', 'updated')
    search_fields = ('slug',)
    list_filter = ('updated',)
    prepopulated_fields = {'slug': ('body',)}
    # inja migam k slug ro bar asase yr fielde dge por bokon
    raw_id_fields = ('user',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created', 'is_reply')
    raw_id_fields = ('user', 'post', 'reply')

# or admin.site.register(Post, PostAdmin)


admin.site.register(Vote)
