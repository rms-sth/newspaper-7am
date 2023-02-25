from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register("users", views.UserViewSet)
router.register("groups", views.GroupViewSet)
router.register("tags", views.TagViewSet)
router.register("categories", views.CategoryViewSet)
router.register("posts", views.PostViewSet)
router.register("contact-us", views.ContactViewSet)
router.register("newsletter", views.NewsLetterViewSet)
# router.register("comments/<int:post_id>", views.CommentViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path(
        "draft-list/",
        views.DraftListViewSet.as_view(),
        name="draft-list",
    ),
    path(
        "post-publish/",
        views.PostPublishViewSet.as_view(),
        name="post-publish",
    ),
    path(
        "top-categories/",
        views.TopCategoriesListViewSet.as_view(),
        name="top-categories",
    ),
    path(
        "post-by-category/<int:cat_id>/",
        views.PostByCategoryListViewSet.as_view(),
        name="top-by-category",
    ),
    path(
        "post-by-tag/<int:tag_id>/",
        views.PostByTagListViewSet.as_view(),
        name="post-by-tag",
    ),
    path(
        "post/<int:post_id>/comments/",
        views.PostCommentViewSet.as_view(),
        name="post-comment",
    ),
    path(
        "api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
]
