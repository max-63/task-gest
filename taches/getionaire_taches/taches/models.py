from django.db import models
from datetime import *
from django.contrib.auth.models import User
import json


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discord_username = models.CharField(max_length=150, blank=True, null=True)
    last_login = models.DateField(default=datetime.today)
    is_logged_in = models.BooleanField(default=False)
    coins =  models.IntegerField(default=0)
    pp = models.ImageField(upload_to="images/pp/", default="images/pp/steve_default.jpg")
    
class Projet(models.Model):
    nom = models.CharField(max_length=200)
    date_creation = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    est_terminee = models.BooleanField(default=False)
    user_admin = models.CharField(max_length=200)
    collaborateurs = models.TextField(blank=True, null=True)

    def set_collaborateurs(self, collaborateurs_list):
        """Stocke les collaborateurs sous forme de liste JSON."""
        self.collaborateurs = json.dumps(collaborateurs_list)
        self.save()

    def get_collaborateurs(self):
        """Récupère les collaborateurs sous forme de liste."""
        if self.collaborateurs:
            return json.loads(self.collaborateurs)
        return []

    def get_regroupements(self):
        """Retourne tous les regroupements de tâches du projet."""
        return self.regroupements.all()

    def get_toutes_taches(self):
        #Retourne toutes les tâches associées aux regroupements du projet (ManyToMany).
        return Tache.objects.filter(regroupement__in=self.get_regroupements()).distinct()
    


    def __str__(self):
        return self.nom
    

class TacheRegroupement(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="regroupements")
    nom = models.CharField(max_length=200)
    description = models.TextField()
    est_terminee = models.BooleanField(default=False)

    def __str__(self):
        return f"Regroupement {self.nom} - {self.projet.nom}"
    
    def get_taches(self):
        """Retourne toutes les tâches du regroupement."""
        return self.taches.all()



class Tache(models.Model):
    regroupement = models.ManyToManyField(TacheRegroupement, related_name="taches")
    nom = models.CharField(max_length=200)
    description = models.TextField()
    est_terminee = models.IntegerField(default=0) #de 0 a 2, 0, a faire , 1 en cour , 2 fait
    dependantes = models.ManyToManyField('self', symmetrical=False, blank=True)  # Plusieurs dépendances possibles
    duree = models.IntegerField(default=2) 
    date_fini = models.DateTimeField(null=True, blank=True)
    assignee_a = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def get_regroup(self):
        return self.regroupement.all()

    def __str__(self):
        return f"Tâche {self.nom}" 
    

class Chatregroupement(models.Model):
    regroupement = models.OneToOneField(TacheRegroupement, on_delete=models.CASCADE, related_name="chat_regroupement")
    def __str__(self):
        return self.regroupement
    
class ChatProjet(models.Model):
    projet = models.OneToOneField(Projet, on_delete=models.CASCADE, related_name="chat_projet")

class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    texte = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    chat_projet = models.ForeignKey(ChatProjet, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    chat_regroupement = models.ForeignKey(Chatregroupement, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)

    def __str__(self):
        chat_type = "Projet" if self.chat_projet else "Regroupement"
        return f"Message de {self.user.username} ({chat_type})"