from django import forms

from newspaper.models import Contact, NewsLetter, Comment, Post
from django_summernote.widgets import SummernoteWidget


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content", "featured_image", "status", "category", "tag")
        widgets = {
            "title":forms.TextInput(
                attrs={
                    "class":'form-control',
                    'required':True,
                    'placeholder':"Title of your post..."
                }
            ),
            "content": SummernoteWidget(),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "tag": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),
        }


class NewsLetterForm(forms.ModelForm):
    class Meta:
        model = NewsLetter
        fields = "__all__"


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"
