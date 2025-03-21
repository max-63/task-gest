# Generated by Django 5.1 on 2025-03-09 07:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taches', '0003_alter_tache_assignee_a'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatProjet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projet', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chat_projet', to='taches.projet')),
            ],
        ),
        migrations.CreateModel(
            name='Chatregroupement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('regroupement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chat_regroupement', to='taches.tacheregroupement')),
            ],
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texte', models.TextField()),
                ('date_envoi', models.DateTimeField(auto_now_add=True)),
                ('chat_projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='taches.chatprojet')),
                ('chat_regroupement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='taches.chatregroupement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
