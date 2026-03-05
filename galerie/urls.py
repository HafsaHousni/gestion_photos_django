from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='galerie/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profil/', views.profil, name='profil'),
    path('upload/', views.upload_image, name='upload'),
    path('mygallery/', views.my_gallery, name='my_gallery'),

    # Affichage de la corbeille
    path('trash/', views.trash_view, name='trash_bin'),

    # Modifier une image
    path('image/<int:image_id>/edit/', views.edit_image, name='edit_image'),

    # Supprimer (soft delete → vers corbeille)
    path('image/<int:image_id>/soft-delete/', views.soft_delete_image, name='soft_delete_image'),

    # Restaurer une image depuis la corbeille
    path('image/<int:image_id>/restore/', views.restore_image, name='restore_image'),

    # Suppression définitive (hard delete après 7 jours ou manuelle)
    path('image/<int:image_id>/delete/', views.delete_image, name='delete_image'),

    path('album/create/', views.create_album, name='create_album'),
    path('album/add-images/', views.add_images_to_album, name='add_images_to_album'),
    path('albums/', views.albums_view, name='albums'),
    path('albums/<int:album_id>/', views.album_detail, name='album_detail'),

]
