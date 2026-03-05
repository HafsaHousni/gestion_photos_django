from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm  # <-- Import du nouveau formulaire
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Image  , Album
from django.http import HttpResponseForbidden
from .forms import ImageForm, AlbumForm, AddImagesToAlbumForm
from django.utils import timezone

def home(request):
    return render(request, 'galerie/index.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'galerie/register.html', {'form': form})

@login_required
def dashboard(request):
    public_images = Image.objects.filter(is_public=True, is_deleted=False)
    private_images = Image.objects.filter(user=request.user, is_public=False, is_deleted=False)
    context = {
        'public_images': public_images,
        'private_images': private_images,
    }
    return render(request, 'galerie/dashboard.html', context)


@login_required
def profil(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = request.user

        # Modifier le nom d'utilisateur
        if username and username != user.username:
            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà utilisé.")
            else:
                user.username = username
                user.save()
                messages.success(request, "Nom d'utilisateur mis à jour.")

        # Modifier le mot de passe
        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Mot de passe mis à jour.")
        else:
            for error in password_form.errors.values():
                messages.error(request, error)
    else:
        password_form = PasswordChangeForm(request.user)

    return render(request, 'galerie/profil.html', {
        'password_form': PasswordChangeForm(request.user),
    })
from .forms import ImageUploadForm
from .models import Image

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.save()
            form.save_m2m()  # Sauvegarde les relations ManyToMany (albums)
            return redirect('my_gallery')  # Remplace par ta vue de galerie
    else:
        form = ImageUploadForm(user=request.user)
    return render(request, 'galerie/upload.html', {'form': form})


@login_required
def my_gallery(request):
    images = Image.objects.filter(user=request.user, is_deleted=False).order_by('-uploaded_at')
    return render(request, 'galerie/my_gallery.html', {'public_images': images})



@login_required
def edit_image(request, pk):
    image = get_object_or_404(Image, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect('my_gallery')
    else:
        form = ImageForm(instance=image)

    return render(request, 'edit_image.html', {'form': form, 'image': image})

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id, user=request.user)
    if image.deleted_at and timezone.now() >= image.deleted_at + timezone.timedelta(days=7):
        image.image.delete()  # Supprime le fichier du disque
        image.delete()        # Supprime de la base de données
    return redirect('trash_bin')

@login_required
def soft_delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id, user=request.user)
    image.is_deleted = True  # Marquer comme supprimée (soft delete)
    image.deleted_at = timezone.now()  # Sauvegarder la date de suppression
    image.save()
    return redirect('my_gallery')



@login_required
def trash_view(request):
    trashed_images = Image.objects.filter(user=request.user, is_deleted=True)
    return render(request, 'galerie/bin.html', {'trashed_images': trashed_images})


@login_required
def trash_bin(request):
    deleted_images = Image.objects.filter(user=request.user, is_deleted=True).order_by('-deleted_at')
    return render(request, 'galerie/trash_bin.html', {'deleted_images': deleted_images})



def restore_image(request, image_id):
    # Récupérer l'image avec cet id, sans filtre sur is_deleted
    image = get_object_or_404(Image, id=image_id)
    
    if image.is_deleted:
        # Restaurer l'image
        image.is_deleted = False
        image.deleted_at = None
        image.save()
    
    return redirect('dashboard')

@login_required
def create_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.save()
            return redirect('my_gallery')
    else:
        form = AlbumForm()
    return render(request, 'create_album.html', {'form': form})
@login_required
def add_images_to_album(request):
    if request.method == 'POST':
        form = AddImagesToAlbumForm(request.user, request.POST)
        if form.is_valid():
            album = form.cleaned_data['album']
            for image in form.cleaned_data['images']:
                album.image_set.add(image)
            return redirect('my_gallery')
    else:
        form = AddImagesToAlbumForm(request.user)
    return render(request, 'add_images_to_album.html', {'form': form})

@login_required
def albums_view(request):
    albums = Album.objects.filter(user=request.user)
    return render(request, 'albums.html', {'albums': albums})

@login_required
def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    return render(request, 'album_detail.html', {'album': album})


def logout_view(request):
    logout(request)
    return redirect('login')