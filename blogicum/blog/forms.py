from django import forms
from django.core.exceptions import ValidationError
from .models import Post, User, Comment
from django.core.mail import send_mail

# Множество с именами участников Ливерпульской четвёрки.
BEATLES = {"Джон Леннон", "Пол Маккартни", "Джордж Харрисон", "Ринго Старр"}


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]
        return first_name.split()[0]

    def clean(self):
        super().clean()
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        if f"{first_name} {last_name}" in BEATLES:
            message = f"{first_name} {last_name} пытался зарегестрироваться!"
            send_mail(
                subject="Another Beatles member",
                message=message,
                from_email="birthday_form@acme.not",
                recipient_list=["admin@acme.not"],
                fail_silently=True,
            )
            raise ValidationError(
                "Мы тоже любим Битлз, но введите, пожалуйста, настоящее имя!"
            )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)


class PostForm(forms.ModelForm):
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Post
        exclude = ("created_ad", "author")
        widgets = {"pub_date": forms.DateInput(attrs={"type": "date"})}
