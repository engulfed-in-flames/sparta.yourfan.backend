from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib import admin
from .models import CustomUser


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "nickname",
            "password1",
            "password2",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", None)
        password2 = self.cleaned_data.get("password2", None)

        if (password1 is None) | (password2 is None):
            raise ValidationError("Passwords should not be empty")

        if password1 != password2:
            raise ValidationError("Passwords do not match")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "password",
            "is_active",
            "is_superuser",
        )


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "email",
        "nickname",
    )
    fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "email",
                    "nickname",
                ),
                "classes": "wide",
            },
        ),
        (
            "Detail",
            {
                "fields": ("date_joined",),
                "classes": ["collapse", "wide"],
            },
        ),
    )
    add_fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "email",
                    "nickname",
                    "password1",
                    "password2",
                )
            },
        ),
    )
    ordering = ("email",)
    search_fields = ("email",)
    filter_horizontal = []


admin.site.unregister(Group)
