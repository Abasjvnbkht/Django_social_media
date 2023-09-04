from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile


class UserRegistrationForm(forms.Form):
    username = forms.CharField(min_length=2, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    password1 = forms.CharField(label='password', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Your Password'}))
    password2 = forms.CharField(label='conirm password', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Your Password'}))

    # nahveye validate kardane form ha
    def clean_email(self):
        # baraye jelogigri az email tekrari
        # in bad az is_valid dar view ejra mishe
        email = self.cleaned_data['email']
        # in email karbar haseshh
        # in clean data hamun cleandata dar dakhele (regietrview.post) hasesh
        user = User.objects.filter(email=email).exists()
        # email avali fieldihas vase User, va 2vomi motegayere balaei hasesh
        # exists true ya false miare va bara behine kardane code b dard mikhore in nabashe,
        # bayad dar model kolle email ro bekhune k baes mishe barname sangin she ama ba in na
        if user:
            raise ValidationError('this email alreaddy exist')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).exists()
        if user:
            raise ValidationError('this name is already')
        return username

    def clean(self):
        cd = super().clean()
        p1 = cd.get('password1')
        p2 = cd.get('password2')

        if p1 and p2 and p1 != p2:
            # age p1 v p2 bud va shabihe ham nabud :
            raise ValidationError('password must match')


class UserLoginForm(forms.Form):
    username = forms.CharField(min_length=2, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Your Password'}))


class EditUserForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ('age', 'bio')
