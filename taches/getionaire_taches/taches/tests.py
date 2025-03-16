import django
import os
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.models import User
from taches.models import Tache, TacheRegroupement, Projet

# Initialisation de Django (si lancé hors du shell Django)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'getionaire_taches.settings')
django.setup()

# 🔹 ID du projet dans lequel ajouter les tâches
PROJET_ID = 1

# 🔹 Vérifie si le projet existe
try:
    projet = Projet.objects.get(id=PROJET_ID)
except Projet.DoesNotExist:
    print(f"❌ Le projet avec l'ID {PROJET_ID} n'existe pas !")
    exit()

# 🔹 Création ou récupération d'un regroupement dans ce projet
regroupement, _ = TacheRegroupement.objects.get_or_create(
    projet=projet,
    nom="Regroupement Test",
    defaults={"description": "Regroupement pour test de tâches."}
)

# 🔹 Récupérer ou créer un utilisateur pour assigner les tâches
user, _ = User.objects.get_or_create(username="testuser", defaults={"email": "test@example.com"})

# 🔹 Création des 30 tâches avec date_fini espacée de 1 à 2 jours
for i in range(30):
    date_fini = now() - timedelta(days=30 - i, hours=(i % 2) * 12)  # Décalage de 1 à 2 jours
    tache = Tache.objects.create(
        nom=f"Tâche {i+1}",
        description=f"Description de la tâche {i+1}",
        est_terminee=2,  # ✅ Tâche terminée
        duree=(i % 5) + 1,  # Durée entre 1 et 5 jours
        date_fini=date_fini,
        assignee_a=user
    )
    tache.regroupement.add(regroupement)  # Ajouter au regroupement

print("✅ 30 tâches terminées créées avec des dates progressives !")
