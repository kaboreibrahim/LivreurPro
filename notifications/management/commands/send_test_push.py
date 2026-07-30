from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from notifications.models import PushSubscription
from notifications.push import send_push_to_subscription

User = get_user_model()


class Command(BaseCommand):
    help = "Envoie une notification push de test à tous les abonnements actifs d'un utilisateur."

    def add_arguments(self, parser):
        parser.add_argument('username', help="username ou email de l'utilisateur cible")
        parser.add_argument('--title', default='Mon Livreur Pro')
        parser.add_argument('--body', default='Ceci est une notification de test.')
        parser.add_argument('--url', default='/')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                raise CommandError(f"Aucun utilisateur trouvé pour '{username}'")

        subscriptions = PushSubscription.objects.filter(utilisateur=user, actif=True)
        if not subscriptions.exists():
            self.stdout.write(self.style.WARNING(
                f"Aucun abonnement push actif pour {user}. "
                "Activez d'abord les notifications depuis le site (cloche de notifications)."
            ))
            return

        payload = {
            'title': options['title'],
            'body': options['body'],
            'url': options['url'],
            'tag': 'test-push',
        }

        sent, failed = 0, 0
        for subscription in subscriptions:
            if send_push_to_subscription(subscription, payload):
                sent += 1
            else:
                failed += 1

        self.stdout.write(self.style.SUCCESS(f"{sent} notification(s) envoyée(s), {failed} échec(s)."))
