from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Crée les groupes utilisateurs de base (client, livreur, gestionnaire)'

    def handle(self, *args, **options):
        # Liste des groupes à créer
        groups = ['client', 'livreur', 'gestionnaire']
        
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Groupe créé : {group_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Le groupe {group_name} existe déjà'))
