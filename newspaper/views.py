from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from newspaper.forms import CommentForm, ContactForm, NewsLetterForm, PostForm, CategoryForm
from newspaper.models import Category, Post


class HomeView(ListView):
    model = Post
    template_name = "aznews/home.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        status="published", published_at__isnull=False
    ).order_by("-published_at")[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_post"] = (
            Post.objects.filter(status="published", published_at__isnull=False)
            .order_by("-views_count")  # descending order
            .first()
        )
        context["most_viewed_posts"] = Post.objects.filter(
            status="published", published_at__isnull=False
        ).order_by("-views_count")[:3]

        one_week_ago = timezone.now() - timedelta(days=7)
        context["weekly_top_posts"] = Post.objects.filter(
            status="published",
            published_at__isnull=False,
            published_at__gte=one_week_ago,
        ).order_by("-views_count")[:7]

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "aznews/detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj = self.get_object()
        obj.views_count += 1
        obj.save()

        # detail => 5
        # 4, 3, 2, 1
        obj = self.get_object()
        context["previous_post"] = (
            Post.objects.filter(
                id__lt=obj.id,
                status="published",
                published_at__isnull=False,
            )
            .order_by("-id")
            .first()
        )
        # detail => 5
        # 6, 7, 8, 9
        context["next_post"] = (
            Post.objects.filter(
                id__gt=obj.id,
                status="published",
                published_at__isnull=False,
            )
            .order_by("id")
            .first()
        )
        context["recent_posts"] = Post.objects.filter(
            status="published", published_at__isnull=False
        ).order_by("-published_at")[:4]
        return context


class PostListView(ListView):
    model = Post
    template_name = "aznews/list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        status="published", published_at__isnull=False
    ).order_by("-published_at")
    paginate_by = 10


class PostSearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET["query"]
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

        page = request.GET.get("page", 1)
        paginator = Paginator(posts, 1)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return render(
            request,
            "aznews/search_list.html",
            {"query": query, "page_obj": page_obj},
        )


class NewsLetterView(View):
    form_class = NewsLetterForm

    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get("x-requested-with")
        if is_ajax == "XMLHttpRequest":
            form = self.form_class(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Successfully submitted your email address. We will contact you soon",
                    },
                    status=200,
                )
            else:
                print(form)
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Something went wrong. Please make sure your form is correct.",
                    },
                    status=400,
                )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Cannot process. Must be an ajax request.",
                },
                status=400,
            )


class PostByCategory(ListView):
    model = Post
    template_name = "aznews/list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        super().get_queryset()
        queryset = Post.objects.filter(
            status="published",
            published_at__isnull=False,
            category=self.kwargs["cat_id"],
        )
        return queryset


class PostByTag(ListView):
    model = Post
    template_name = "aznews/list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        super().get_queryset()
        queryset = Post.objects.filter(
            status="published",
            published_at__isnull=False,
            tag=self.kwargs["tag_id"],
        )
        return queryset


class AboutUsView(TemplateView):
    template_name = "aznews/about.html"


class ContactView(View):
    template_name = "aznews/contact.html"
    form_class = ContactForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Successfully submitted your message. We will contact you soon.",
            )
        else:
            messages.error(
                request,
                "Cannot submit your message. Something went wrong.",
            )
        return render(request, self.template_name, {"form": form})


class CommentView(View):
    form_class = CommentForm
    template_name = "aznews/detail.html"

    def post(self, request, *args, **kwargs):
        post_id = request.POST["post"]

        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("post-detail", post_id)
        else:
            post = Post.objects.get(id=post_id)
            return render(
                request,
                self.template_name,
                {"post": post, "form": form},
            )


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "news_admin/post_list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(published_at__isnull=True)
    paginate_by = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "news_admin/post_create.html"
    success_url = reverse_lazy("draft-list")

    def form_valid(self, form):
        form.instance.author = self.request.user  # logged in user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return redirect("home")


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "news_admin/post_create.html"
    success_url = reverse_lazy("home")


class PostPublishView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        post.status = "published"
        post.published_at = timezone.now()
        post.save()
        return redirect("home")


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "news_admin/category_create.html"
    success_url = reverse_lazy("draft-list")

    def form_valid(self, form):
        form.instance.author = self.request.user  # logged in user
        return super().form_valid(form)
