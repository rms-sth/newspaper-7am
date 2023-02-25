from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from newspaper.models import Category, Comment, Contact, NewsLetter, Post, Tag

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(NewsLetter)
admin.site.register(Contact)
admin.site.register(Comment)


class PostAdmin(SummernoteModelAdmin):
    list_display = ["title", "category", "author"]
    date_hierarchy = "published_at"
    # fields = ("title", "content")


admin.site.register(Post, PostAdmin)
