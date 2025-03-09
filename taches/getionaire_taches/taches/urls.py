from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout/', views.logout_view, name="logout"),
    path('dashboard/', views.pannel, name="dash"),
    path('crer_big_projet/', views.crer_big_projet, name="crer_big_projet"),
    path('big_projet/<str:projet_name>/<str:admin_hash>/', views.projet, name="projet"),
    path('big_projet/<str:projet_name>/<str:admin_hash>/create_regroupement/', views.create_regroupement, name='creer_regroupement'),
    path('big_projet/<str:projet_name>/<str:admin_hash>/see_tasks/<int:regroupement_id>/', views.see_taches_regroupement, name="see_tasks"),
    path('tasks_for_regroupement/<int:regroupement_id>/', views.tasks_for_regroupement, name="tasks_for_regroupement"),
    path('projet/<str:projet_name>/gantt/', views.gantt_sans_date, name='gantt_sans_date'),
    path('projet/<str:projet_name>/tache/<int:tache_id>/<str:admin_hash>/modifier/', views.projet, name='modifier_tache'),
    path('update_task_position/<str:projet_name>/<str:admin_hash>/', views.update_task_position, name='update_task_position'),
    path('add_qqun_to_projet/<int:projet_id>/', views.add_user_to_project, name='add_qqun_to_projet'),
]
