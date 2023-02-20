from django.urls import path
from newspaper import views

urlpatterns = [
    path(
        "",
        views.HomeView.as_view(),
        name="home",
    ),
    path(
        "post-detail/<int:pk>/",
        views.PostDetailView.as_view(),
        name="post-detail",
    ),
    path(
        "post-list",
        views.PostListView.as_view(),
        name="post-list",
    ),
    path(
        "post-search/",
        views.PostSearchView.as_view(),
        name="post-search",
    ),
    path(
        "newsletter/",
        views.NewsLetterView.as_view(),
        name="newsletter",
    ),
    path(
        "post-by-category/<int:cat_id>/",
        views.PostByCategory.as_view(),
        name="post-by-category",
    ),
    path(
        "post-by-tag/<int:tag_id>/",
        views.PostByTag.as_view(),
        name="post-by-tag",
    ),
    path(
        "about/",
        views.AboutUsView.as_view(),
        name="about-us",
    ),
    path(
        "contact/",
        views.ContactView.as_view(),
        name="contact",
    ),
    path(
        "comment/",
        views.CommentView.as_view(),
        name="comment",
    ),
    path(
        "draft-list/",
        views.DraftListView.as_view(),
        name="draft-list",
    ),
    path(
        "post-publish/<int:pk>/",
        views.PostPublishView.as_view(),
        name="post-publish",
    ),
    path(
        "post-create/",
        views.PostCreateView.as_view(),
        name="post-create",
    ),
    path(
        "post-delete/<int:pk>/",
        views.PostDeleteView.as_view(),
        name="post-delete",
    ),
    path(
        "post-update/<int:pk>/",
        views.PostUpdateView.as_view(),
        name="post-update",
    ),
    path(
        "category-create/",
        views.CategoryCreateView.as_view(),
        name="category-create",
    ),
]
