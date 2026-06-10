from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    techhnex_id = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'techhnex_id', 'password1', 'password2']

    def clean_techhnex_id(self):
        techhnex_id = self.cleaned_data['techhnex_id']
        if Profile.objects.filter(techhnex_id=techhnex_id).exists():
            raise forms.ValidationError("Techhnex ID already exists.")
        return techhnex_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Profile.objects.create(
            #     user=user,
            #     techhnex_id=self.cleaned_data['techhnex_id']
            # )
        return user
