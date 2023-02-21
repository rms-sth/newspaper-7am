from django.contrib import admin

from newspaper.models import Category, Comment, Contact, NewsLetter, Post, Tag

# admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(NewsLetter)
admin.site.register(Contact)
admin.site.register(Comment)


class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "author"]
    date_hierarchy = "published_at"
    # fields = ("title", "content")


admin.site.register(Post, PostAdmin)
