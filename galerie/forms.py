from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Image, Album
class ImageUploadForm(forms.ModelForm):
    albums = forms.ModelMultipleChoiceField(
        queryset=Album.objects.none(),  # On remplira dans __init__
        required=False,
        widget=forms.CheckboxSelectMultiple  # Tu peux changer par SelectMultiple si tu préfères
    )

    class Meta:
        model = Image
        fields = ['image', 'description', 'is_public', 'albums']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # On récupère l’utilisateur passé dans la vue
        super().__init__(*args, **kwargs)
        if user:
            self.fields['albums'].queryset = Album.objects.filter(user=user)

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requis.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'description', 'is_public']


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['name']

class AddImagesToAlbumForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.none())
    images = forms.ModelMultipleChoiceField(
        queryset=Image.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['album'].queryset = Album.objects.filter(user=user)
        self.fields['images'].queryset = Image.objects.filter(user=user, is_deleted=False)