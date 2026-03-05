from django.core.management.base import BaseCommand
from django.utils import timezone
from galerie.models import Image  

class Command(BaseCommand):
    help = 'Supprime définitivement les images dans la corbeille depuis plus de 7 jours.'

    def handle(self, *args, **kwargs):
        expiration = timezone.now() - timezone.timedelta(days=7)
        images = Image.objects.filter(is_deleted=True, deleted_at__lte=expiration)

        count = images.count()
        for img in images:
            img.image.delete()  # supprime le fichier image du serveur
            img.delete()        # supprime la ligne dans la base de données

        self.stdout.write(self.style.SUCCESS(f'{count} images supprimées définitivement.'))
