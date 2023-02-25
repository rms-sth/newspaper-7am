from django.contrib.auth.models import Group, User
from django.db.models import Case, F, Q, Sum, When
from django.utils import timezone
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
    PostPublishSerializer,
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

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [
                permissions.IsAuthenticated(),
            ]
        return super().get_permissions()


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Group to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Tag to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [
                permissions.AllowAny(),
            ]
        return super().get_permissions()


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Category to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [
                permissions.AllowAny(),
            ]
        return super().get_permissions()


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Post to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.filter(published_and_active).order_by("-published_at")
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [
                permissions.AllowAny(),
            ]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.views_count += 1
        obj.save()
        return super().retrieve(request, *args, **kwargs)


class TopCategoriesListViewSet(ListAPIView):
    """
    List all Top categories that has maximum views_count posts
    """

    permission_classes = [permissions.AllowAny]
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
        # [2,6,5,6]
        category_ids = [top_category["pk"] for top_category in top_categories]
        order_by_max_views = Case(
            *[
                When(id=category["pk"], then=category["max_views"])
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

    permission_classes = [permissions.AllowAny]
    serializer_class = PostSerializer

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

    permission_classes = [permissions.AllowAny]
    serializer_class = PostSerializer

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

    permission_classes = [permissions.IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_permissions(self):
        if self.action == "create":
            return [
                permissions.AllowAny(),
            ]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)  # raise an exception


class NewsLetterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows NewsLetter Us to be viewed or created.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = NewsLetter.objects.all()
    serializer_class = NewsLetterSerializer

    def get_permissions(self):
        if self.action == "create":
            return [
                permissions.AllowAny(),
            ]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)  # raise an exception


class DraftListViewSet(ListAPIView):
    """
    List all Posts by tag id
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.filter(published_at__isnull=True).order_by("-created_at")
    serializer_class = PostSerializer


class PostPublishViewSet(APIView):
    """
    API endpoint that allows Comment to be viewed or created in specified post.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostPublishSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data

            # publish the post
            post = Post.objects.get(id=data["post"])
            post.published_at = timezone.now()
            post.save()

            serialized_post = PostSerializer(post)
            return Response(
                {
                    "success": "Post was successfully published.",
                    "data": serialized_post.data,
                },
                status=status.HTTP_201_CREATED,
            )


class PostCommentViewSet(APIView):
    """
    API endpoint that allows Comment to be viewed or created in specified post.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = CommentSerializer

    def get(self, request, post_id, *args, **kwargs):
        comments = Comment.objects.filter(post=post_id).order_by("-created_at")
        serializer = self.serializer_class(comments, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, post_id, *args, **kwargs):
        request.data.update({"post": post_id})
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
