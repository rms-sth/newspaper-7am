from django.contrib.auth.models import Group, User
from django.db.models import Case, F, Q, Sum, When
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, permissions, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    ContactSerializer,
    GroupSerializer,
    NewsLetterSerializer,
    PostSerializer,
    TagSerializer,
    TopCategorySerializer,
    UserSerializer,
)
from newspaper.models import Category, Comment, Contact, NewsLetter, Post, Tag

published_and_active = Q(status="published", published_at__isnull=False)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().order_by("-date_joined")  # latest user
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [
                permissions.IsAuthenticated(),
            ]
        return super().get_permissions()

    # def get_queryset(self):
    #     return User.objects.all().exclude(id=self.request.user.id).order_by("username")


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Group to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Tag to be viewed or edited.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Category to be viewed or edited.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Post to be viewed or edited.
    """

    queryset = Post.objects.filter(published_and_active)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


class TopCategoriesListViewSet(ListAPIView):
    """
    List all Top categories that has maximum views_count posts
    """

    serializer_class = TopCategorySerializer

    def get_queryset(self):
        top_categories = (
            Post.objects.filter(published_and_active)
            .values("category__pk", "category__name")
            .annotate(
                pk=F("category__pk"),
                name=F("category__name"),
                max_views=Sum("views_count"),
            )
            .order_by("-views_count")
            .values("pk", "name", "max_views")
        )
        category_ids = [
            top_category["pk"] for top_category in top_categories
        ]  # [2,6,5,6]
        order_by_max_views = Case(
            *[
                When(
                    id=category["pk"], then=category["max_views"]
                )  # When(id=2, then=11), When(id=6,then=2)
                for category in top_categories
            ]
        )
        top_categories = Category.objects.filter(pk__in=category_ids).order_by(
            -order_by_max_views
        )
        return top_categories


class PostByCategoryListViewSet(ListAPIView):
    """
    List all Posts by category id
    """

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Post.objects.filter(
            published_and_active,
            category=self.kwargs["cat_id"],
        )
        return queryset


class PostByTagListViewSet(ListAPIView):
    """
    List all Posts by tag id
    """

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Post.objects.filter(
            published_and_active,
            tag=self.kwargs["tag_id"],
        )
        return queryset


class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Contact Us to be viewed or created.
    """

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)  # raise an exception


class NewsLetterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows NewsLetter Us to be viewed or created.
    """

    queryset = NewsLetter.objects.all()
    serializer_class = NewsLetterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)  # raise an exception


class PostCommentListViewSet(APIView):
    """
    API endpoint that allows Comment to be viewed or created in specified post.
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def validate_post(self, post_id):
        if not post_id:
            return Response(
                {"success": "Must specify the post query params. Example: ?post=1"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            post = get_object_or_404(Post, pk=post_id)
            return post

    def get(self, request, post_id, *args, **kwargs):
        post = self.validate_post(post_id)
        comments = Comment.objects.filter(post=post).order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, post_id, *args, **kwargs):
        post = self.validate_post(post_id)
        data = request.data
        data.update({"post": post.id})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            data.update({"post": post})
            comment = Comment.objects.create(**data)
            serializer = CommentSerializer(comment)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
