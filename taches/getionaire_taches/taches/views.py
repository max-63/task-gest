from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import paypalrestsdk
from paypalrestsdk import Payment
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
import requests
from django.contrib import messages
from .models import UserProfile, Projet, TacheRegroupement, Tache, Chatregroupement, ChatProjet, Messages
import hashlib
import json
import logging 
import plotly.graph_objects as go
from django.http import JsonResponse
from datetime import timedelta
from django.db.models import Sum
from collections import defaultdict, deque
from django.core.serializers.json import DjangoJSONEncoder
from collections import Counter
from django.utils.timezone import is_aware, make_aware
import pandas as pd
import datetime
from django.utils import timezone

def is_normal_or_staff(user):
    return user.is_authenticated and (not user.is_superuser or user.is_staff)

def index(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Connexion réussie
            auth_login(request, user)
            user_profile = UserProfile.objects.get(user=user)
            user_profile.is_logged_in = True
            user_profile.save()
            return redirect('dash')  # Redirection après la connexion
        else:
            # Si les identifiants sont incorrects
            messages.error(request, "Mauvais mot de passe ou identifiant. Veuillez réessayer. Si vous n'avez pas encore de compte, créez-en un.")
            return redirect('login')  # Redirection vers la page de connexion
    return render(request, 'login.html')


@user_passes_test(is_normal_or_staff)
@login_required
def logout_view(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.is_logged_in = False
        user_profile.save()
        auth_logout(request)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            auth_logout(request)
            user_profile.is_logged_in = False
            return JsonResponse({'message': 'Successfully logged out.'})
        else:
            auth_logout(request)
            return redirect('home')  # Change to your actual redirect URL
    return redirect('home')

def register_view(request):
    if request.method == "POST":
        username_a = request.POST.get('username')
        password_a = request.POST.get('password')
        email = request.POST.get('email')

        # Vérifie si l'utilisateur existe déjà
        if User.objects.filter(username=username_a).exists():
            return JsonResponse({'success': False, 'message': 'Username already exists. Please choose another one.'})
        
        try:
            # Crée l'utilisateur
            user = User.objects.create_user(username=username_a, password=password_a, email=email)
            # Crée le profil utilisateur
            UserProfile.objects.create(user=user)
            
            # Renvoie une réponse de succès
            return JsonResponse({'success': True, 'message': 'Registration successful! You can now log in.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})
    
    # Si la méthode est GET ou autre
    return render(request, 'register.html')



@login_required
def pannel(request):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
    
    # On cherche tous les projets où l'utilisateur est soit administrateur, soit collaborateur
    projets = Projet.objects.filter(collaborateurs__contains=user_profile.user.username) | Projet.objects.filter(user_admin=user_profile.user) 
    url = "{% url 'projet' projet_name admin_hash %}"
    # Convertir les projets en format JSON (au lieu de simplement passer l'objet projet brut)
    projets_json = json.dumps([
        {
            **projet,
            "date_creation": projet["date_creation"].isoformat() if "date_creation" in projet else None,
            "nombre_taches_total": Projet.objects.get(id=projet["id"]).get_toutes_taches().count(),
            "tache_a_faire_nb": Projet.objects.get(id=projet["id"]).get_toutes_taches().filter(est_terminee=0).count(),
            "tache_en_cour_nb": Projet.objects.get(id=projet["id"]).get_toutes_taches().filter(est_terminee=1).count(),
            "tache_fini_nb": Projet.objects.get(id=projet["id"]).get_toutes_taches().filter(est_terminee=2).count(),
            "nom": projet["nom"],
            "user_admin": hash_admin_name(projet["user_admin"]),
            "collaborateurs": projet["collaborateurs"],

        }
        for projet in projets.values()
    ])



    context = {
        "projets_json": projets_json,  # On passe les projets sous forme de chaîne JSON
        "user": user_profile.user,
    }

    return render(request, 'pannel.html', context)




@login_required
def crer_big_projet(request):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        
    if request.method == "POST":
        nom = request.POST.get("proj_princip")
        admin = user_profile.user.username
        # Vérifier si un projet existe déjà avec ce nom et cet administrateur
        if not Projet.objects.filter(user_admin=admin, nom=nom).exists():
            # Création du projet avec le nom d'utilisateur comme String
            projet = Projet.objects.create(
                nom=nom,
                user_admin=admin  # On stocke maintenant le nom d'utilisateur
            )
            projet.save()
            print("Projet créé avec succès!")
            messages.success(request, f"Le projet {projet.nom} a été créé avec succès.")
            return redirect('dash')
        else:
            print("Un projet avec ce nom et cet administrateur existe déjà.")
            messages.error(request, "Un projet avec ce nom et cet administrateur existe déjà.")
            
    return render(request, 'pannel.html')


def hash_admin_name(admin_name):
    """ Retourne un hash unique pour l'admin """
    return hashlib.sha256(admin_name.encode()).hexdigest()[:15]  # Prend seulement 10 caractères pour éviter un hash trop long


def projet(request, projet_name, admin_hash, tache_id=None):
    projets = Projet.objects.filter(nom=projet_name)
    projet = None
    for p in projets:
        if hash_admin_name(p.user_admin) == admin_hash:
            projet = p
            break
    
    if not projet:
        return render(request, '404.html')

    taches_regroupement = projet.get_regroupements()
    regroupement_taches = {}
    tasks_data = []
    total_tasks = 0

    for regroupement in taches_regroupement:
        taches = Tache.objects.filter(regroupement=regroupement)
        nb_taches = taches.count()
        regroupement_taches[regroupement.nom] = {
            'taches': list(taches.values('id', 'nom')),
            'nb_taches': nb_taches,
        }
        total_tasks += nb_taches
        tasks_data.append({
            'label': regroupement.nom,
            'value': nb_taches,
            
        })

    tasks_data_json = json.dumps(tasks_data)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"tasks": tasks_data})

    tache = None
    if tache_id:
        tache = get_object_or_404(Tache, id=tache_id)
        if request.method == "POST":
            tache.nom = request.POST.get("nom")
            tache.description = request.POST.get("description")
            tache.est_terminee = request.POST.get("statu") #== "terminé"
            if tache.est_terminee == 0:
                tache.est_terminee = 0
                tache.date_fini = None
            if tache.est_terminee == 1:
                tache.est_terminee = 1
                tache.date_fini = None
            if tache.est_terminee == 2:
                tache.est_terminee = 2
                tache.date_fini = timezone.now
            print(tache.est_terminee)
            tache.save()


    if request.method == "POST":
        chat_projet_instance, created = ChatProjet.objects.get_or_create(projet=projet)
        message = request.POST.get("message_projet")

        if message:  # Vérification si le message n'est pas vide
            message = Messages.objects.create(
                user=request.user,
                texte=message,
                chat_projet=chat_projet_instance,
            )

    try:
        chat_projet = ChatProjet.objects.get(projet=projet)
        messages = Messages.objects.filter(chat_projet=chat_projet)
        message_projet = [
            {
                'user': message.user.username,
                'texte': message.texte,
                'date_envoi': message.date_envoi.strftime('%Y-%m-%d %H:%M:%S')
            }
            for message in messages
        ]
    except:
        message_projet = [{}]

    message_projet = json.dumps(message_projet)
    context = {
        "user": request.user,
        "user_admin": projet.user_admin,
        "projet": projet,
        "projet_id":projet.id,
        "admin_hash": admin_hash,
        "projet_name": projet.nom,
        "taches_regroupement": taches_regroupement,
        "tasks_data": tasks_data_json,
        "total_tasks": total_tasks,
        "tache": tache,
        "message_projet":message_projet,
        "projet_id": projet.id,
    }
    
    return render(request, 'interieur_projet.html', context)




@login_required
def create_regroupement(request, projet_name, admin_hash):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        description = request.POST.get('description')

        # Vérification que les champs sont présents
        if not nom or not description:
            return JsonResponse({'success': False, 'message': 'Nom et description sont requis.'}, status=400)

        # Trouver le projet par son nom
        try:
            projet = Projet.objects.get(nom=projet_name)
        except Projet.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Projet introuvable.'}, status=404)

        # Créer le regroupement
        regroupement = TacheRegroupement.objects.create(
            projet=projet,
            nom=nom,
            description=description,
            
        )
        regroupement.save()

        return redirect('projet', projet_name=projet.nom, admin_hash=admin_hash)  # Rediriger vers le projet après la création

    return redirect('dash')  # Rediriger vers la page d'accueil si la méthode n'est pas POST



@login_required
def see_taches_regroupement(request, projet_name, regroupement_id, admin_hash):
    projet = get_object_or_404(Projet, nom=projet_name)
    regroupement_actuel = get_object_or_404(TacheRegroupement, id=regroupement_id, projet=projet)
    taches = Tache.objects.filter(regroupement=regroupement_actuel)

    # Récupérer toutes les tâches du projet pour affichage dans le select
    all_taches = Tache.objects.filter(regroupement__projet=projet)
    regroupements = TacheRegroupement.objects.filter(projet=projet)

    # Pour chaque tâche, récupérer la liste de ses dépendances
    for tache in taches:
        tache.dependantes_list = tache.dependantes.all()  # Liste des tâches dépendantes

    context = {
        'projet': projet,
        'regroupement_actuel': regroupement_actuel,
        'taches': taches,
        'admin_hash': admin_hash,
        'projet_name': projet_name,
        'regroupement_id': regroupement_id,
        'all_taches': all_taches,  # Liste complète des tâches du projet
        'regroupements': regroupements,
        'users': json.dumps(projet.get_collaborateurs()),  # Convertir en JSON

    }

    if request.method == "POST":

        nom = request.POST.get("nom")
        description = request.POST.get("description")
        dependances_ids = request.POST.getlist("depend")  # Liste de plusieurs dépendances
        a_qui = request.POST.get("assignee_a")
        if a_qui is not None:
            user_assigne = User.objects.filter(username=a_qui).first()
        if a_qui == "null": 
            user_assigne = User.objects.filter(username=projet.user_admin).first()
            print(user_assigne)

        if nom and description:
            nouvelle_tache = Tache.objects.create(
                nom=nom,
                description=description,
                assignee_a=user_assigne,
            )
            nouvelle_tache.regroupement.set([regroupement_actuel])  # Associer au regroupement

            # Vérifier que les dépendances sont bien des entiers valides
            dependances_ids = [int(id) for id in dependances_ids if id and id.isdigit()]

            if dependances_ids:  # Vérifier si la liste n'est pas vide après nettoyage
                dependances_taches = Tache.objects.filter(id__in=dependances_ids)
                nouvelle_tache.dependantes.set(dependances_taches)  # Assigner les dépendances

            nouvelle_tache.save()

    return render(request, 'tasks_regroupement.html', context)



def tasks_for_regroupement(request, regroupement_id):
    regroupement = get_object_or_404(TacheRegroupement, id=regroupement_id)
    taches = Tache.objects.filter(regroupement=regroupement)
    tasks_data = [{'id': tache.id, 'nom': tache.nom} for tache in taches]
    return JsonResponse({'taches': tasks_data})


def gantt_sans_date(request, projet_name):
    try:
        # Récupérer le projet par son nom
        projet = Projet.objects.get(nom=projet_name)

        # Récupérer toutes les tâches associées à ce projet
        taches = projet.get_toutes_taches()

        # Fonction pour calculer le chemin critique
        def find_critical_path(tasks):
            # Créer un graphe des dépendances
            graph = defaultdict(list)  # {to_tache_id: [from_tache_id1, from_tache_id2, ...]}
            in_degree = {}  # {tache_id: nombre de dépendances entrantes}
            longest_path = {}  # {tache_id: longueur du chemin le plus long jusqu'à cette tâche}

            # Initialiser les tâches
            for task in tasks:
                to_tache_id = task['id']  # Utiliser l'ID de la tâche actuelle
                from_tache_ids = task['dependantes']  # Liste des dépendances

                if to_tache_id is None or from_tache_ids is None:
                    continue

                # Ajouter les dépendances dans le graphe
                for from_tache_id in from_tache_ids:
                    graph[from_tache_id].append(to_tache_id)
                    in_degree[to_tache_id] = in_degree.get(to_tache_id, 0) + 1
                    in_degree.setdefault(from_tache_id, 0)  # Assurer que toutes les tâches sont comptabilisées
                    longest_path[from_tache_id] = 0
                    longest_path[to_tache_id] = 0

            # Trouver les tâches sans dépendances entrantes (points de départ)
            queue = deque([task_id for task_id in in_degree if in_degree[task_id] == 0])

            # Calculer le chemin critique avec un tri topologique
            while queue:
                task_id = queue.popleft()
                for next_task in graph[task_id]:
                    longest_path[next_task] = max(longest_path[next_task], longest_path[task_id] + 1)
                    in_degree[next_task] -= 1
                    if in_degree[next_task] == 0:
                        queue.append(next_task)

            return longest_path

        # Récupérer les données des tâches
        tasks_data = []
        for tache in taches:
            tasks_data.append({
                'id': tache.id,
                'nom': tache.nom,
                'dependantes': [dependance.id for dependance in tache.dependantes.all()]  # Liste d'IDs des dépendances
            })
        

        # Calculer le chemin critique
        task_positions = find_critical_path(tasks_data)
        
        # Définir l'espacement entre les tâches
        dependency_spacing = 165

        # Convertir en positions pour affichage
        task_positions_px = {task_id: position * dependency_spacing for task_id, position in task_positions.items()}

        # Construire les données des tâches pour la réponse JSON
        tasks_info = []
        for tache in taches:
            task_info = {
                'name': tache.nom,
                'duree': tache.duree,
                'dependances': [dependance.id for dependance in tache.dependantes.all()],  # On récupère les IDs des dépendances
                'regroupement': [regroupement.nom for regroupement in tache.regroupement.all()],
                'description': tache.description,
                'est_terminee': int(tache.est_terminee),
                'tache_id': tache.id,
                
            }
            tasks_info.append(task_info)

        users = projet.get_collaborateurs()
        json.dumps(users)
            

        # Renvoyer les données des tâches
        return JsonResponse({'tasks': tasks_info, 'positions': task_positions_px, 'users':users})

    except Projet.DoesNotExist:
        return JsonResponse({'error': 'Projet non trouvé'}, status=404)
    except Exception as e:
        # Pour mieux débuguer, vous pouvez renvoyer l'erreur exacte
        return JsonResponse({'error': str(e)}, status=500)




# def update_task_position(request, projet_name, admin_hash):
#     if request.method == "POST":
#         try:
#             # Lire le corps de la requête JSON
#             print(request.body)  # Ajouter ceci pour déboguer le contenu de la requête
#             data = json.loads(request.body)
#             moved_task_id = data.get('movedTaskId')
#             target_task_id = data.get('targetTaskId')

#             if not moved_task_id or not target_task_id:
#                 return JsonResponse({'success': False, 'error': 'IDs des tâches manquants'}, status=400)

#             moved_task = Tache.objects.get(id=moved_task_id)
#             print(moved_task)
#             target_task = Tache.objects.get(id=target_task_id)
#             print(target_task)
#             moved_task.dependantes.add(target_task)
#             moved_task.save()

#             return JsonResponse({'success': True})

#         except json.JSONDecodeError:
#             return JsonResponse({'success': False, 'error': 'Erreur de décodage JSON'}, status=400)
#         except Tache.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Tâche introuvable'}, status=404)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)

#     return JsonResponse({'success': False, 'error': 'Méthode HTTP invalide'}, status=405)


@csrf_exempt
@login_required
def update_task_position(request, projet_name, admin_hash):
    if request.method == 'POST':
        data = json.loads(request.body)
        moved_task_id = data.get('movedTaskId')
        target_task_id = data.get('targetTaskId')

        if not moved_task_id or not target_task_id:
            return JsonResponse({'success': False, 'error': 'IDs des tâches manquants'}, status=400)
        
        if not moved_task_id == target_task_id:
            moved_task = Tache.objects.get(id=moved_task_id)
            target_task = Tache.objects.get(id=target_task_id)
            moved_task.dependantes.add(target_task)
            moved_task.save()

        

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Bad request'})


def add_user_to_project(request, projet_id):
    if request.method == 'POST':
        username = request.POST.get('pseudo')
        try:
            projet = Projet.objects.get(id=projet_id)
            user = User.objects.get(username=username)
            projet.set_collaborateurs(projet.get_collaborateurs() + [user.username])
            projet.save()
            return JsonResponse({'success': True, 'message': f'{username} a été ajouté au projet {projet.nom}.'})
        except Projet.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Projet introuvable.'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Utilisateur introuvable.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return render(request, 'pannel.html')



def graph_taches_par_jour(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)

    # Récupérer toutes les tâches terminées avec une date de fin
    taches_terminees = Tache.objects.filter(
        regroupement__projet=projet, est_terminee=2, date_fini__isnull=False
    ).values_list("date_fini", flat=True)

    dates_completion = [make_aware(date).date() if not is_aware(date) else date.date() for date in taches_terminees]


    # Compter le nombre de tâches terminées par jour
    count_per_day = Counter(dates_completion)

    # Transformer en DataFrame Pandas pour trier les dates
    df = pd.DataFrame(list(count_per_day.items()), columns=['date', 'tasks_completed'])
    df = df.sort_values('date')

    # Convertir les dates en string pour JSON
    df['date'] = df['date'].astype(str)


    return JsonResponse(df.to_dict(orient='list'))