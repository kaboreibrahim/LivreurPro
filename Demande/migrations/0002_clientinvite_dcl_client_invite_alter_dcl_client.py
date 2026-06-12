from django.conf import settings
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Demande', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientInvite',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100, verbose_name='Nom')),
                ('prenom', models.CharField(max_length=100, verbose_name='Prénom')),
                ('telephone', models.CharField(max_length=20, verbose_name='Téléphone')),
                ('email', models.EmailField(blank=True, null=True, verbose_name='Email')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
            options={
                'verbose_name': 'Client invité',
                'verbose_name_plural': 'Clients invités',
            },
        ),
        migrations.AddField(
            model_name='dcl',
            name='client_invite',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='demandes',
                to='Demande.clientinvite',
                verbose_name='Client invité',
            ),
        ),
        migrations.AlterField(
            model_name='dcl',
            name='client',
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={'role': 'client'},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='demandes',
                to=settings.AUTH_USER_MODEL,
                verbose_name='client',
            ),
        ),
    ]
