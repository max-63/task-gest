.then(data => {
    const tasksData = data.tasks_data; // Assurez-vous que cette clé existe dans la réponse
    const ganttContainer = document.getElementById("gantt-container");

    // Stockage des positions et largeurs des tâches
    const taskPositions = {}; // Position horizontale
    const taskWidths = {};    // Largeur des tâches

    // Variable pour la ligne de chaque tâche
    let currentLine = 0;

    // Fonction pour obtenir la position horizontale de la tâche
    function getTaskPosition(taskName) {
        const task = tasksData.find(t => t.name === taskName);
        let position = 0;

        // Si la tâche a des dépendances, on les prend en compte
        if (task && task.dependances && task.dependances.length > 0) {
            const lastDependency = task.dependances[task.dependances.length - 1];
            const lastDependencyPosition = taskPositions[lastDependency] || 0;
            position = lastDependencyPosition + 120; // 120px est l'espacement entre les tâches
        }

        // Si la position est déjà occupée, on la déplace à droite
        let adjustedPosition = position;
        while (Object.values(taskPositions).includes(adjustedPosition)) {
            adjustedPosition += 120; // Décalage de 120px
        }

        return adjustedPosition;
    }

    // Fonction pour obtenir la largeur de la tâche en fonction de sa durée
    function getTaskWidth(taskDuree) {
        const width = taskDuree * 50; // 50px par unité de durée (ajustez selon vos besoins)
        return width;
    }

    // Affichage des tâches dans le Gantt
    tasksData.forEach((task) => {
        const taskRow = document.createElement("div");
        taskRow.classList.add("task-row");

        // Calcul de la position et de la largeur de la tâche
        const taskPosition = getTaskPosition(task.name);
        const taskWidth = getTaskWidth(task.duree);

        // Enregistrer la position et la largeur de la tâche
        taskPositions[task.name] = taskPosition;
        taskWidths[task.name] = taskWidth;

        // Position verticale : chaque tâche sur une ligne distincte avec un espacement de 240px
        const verticalPosition = currentLine * 240; // 240px pour doubler l'espace vertical
        taskRow.style.top = `${verticalPosition}px`;

        // Récupérer la couleur du regroupement (si la tâche en a un)
        let couleur = "#ccc"; // Couleur par défaut
        if (task.regroupement && task.regroupement.length > 0) {
            const regroupementName = task.regroupement[0]; // Prendre le premier regroupement
            if (regroupementCouleurs[regroupementName]) {
                couleur = regroupementCouleurs[regroupementName];
            }
        }

        // Créer la barre de la tâche
        const taskBar = document.createElement("div");
        taskBar.classList.add("gantt-bar");

        // Appliquer la largeur et la position à la barre de tâche
        taskBar.style.width = `${taskWidth}px`;
        taskBar.style.left = `${taskPosition}px`;
        taskBar.style.backgroundColor = couleur;
        taskBar.textContent = task.name;

        // Ajouter un événement au clic sur la tâche pour modifier les informations
        const editUrl = `{% url 'modifier_tache' projet_name 0 admin_hash %}`.replace("0", task.name);
        taskBar.addEventListener("click", () => {
            Swal.fire({
                title: `Modifier la tâche: ${task.name}`,
                html: `
                    <form method="POST" action="${editUrl}">     
                        {% csrf_token %}
                        <label for="nom">Nom</label>
                        <input type="text" id="nom" name="nom" value="{{ task.name }}" required>
                        
                        <label for="description">Description</label>
                        <textarea id="description" name="description" required>{{ task.description }}</textarea>
                        
                        <label for="status">Statut:</label>
                        <select id="status" name="status" required>
                            <option value="">--Please choose an option--</option>
                            <option value="terminé" {% if task.status == "terminé" %}selected{% endif %}>Terminé</option>
                            <option value="en_cours" {% if task.status == "en_cours" %}selected{% endif %}>En cours</option>
                        </select>
                        
                        <button type="submit">Enregistrer</button>
                    </form>
                `,
                showConfirmButton: false,
                showCancelButton: true,
                cancelButtonText: 'Annuler',
                width: '600px',
                padding: '20px',
            });
        });

        // Ajouter la barre de tâche à la ligne et à l'interface
        taskRow.appendChild(taskBar);
        ganttContainer.appendChild(taskRow);

        // Incrémenter le compteur de ligne pour la prochaine tâche
        currentLine++;
    });
})

/* Conteneur pour le diagramme de Gantt */
.gantt-container {
    width: 60%;  /* Ajuste la largeur du diagramme de Gantt */
    overflow-x: auto;
    overflow-y: hidden;
    height: 400px; /* Définit une hauteur pour le diagramme de Gantt */
    position: relative; /* Ajouté pour permettre aux tâches positionnées absolument de se placer correctement */
    margin-top: 3rem;
    border: 2px solid #f1c40f;  /* Bordure jaune (plus foncée pour une meilleure visibilité) */
    border-radius: 8px;  /* Coins arrondis */
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);  /* Ajoute une ombre légère pour plus de profondeur */
}


/* Tâches du diagramme de Gantt */
.gantt-tasks {
    position: relative; /* Ajouté pour s'assurer que les tâches se positionnent correctement */
    display: flex;
    flex-direction: column;
    gap: 10px;  /* Espacement entre les lignes de tâches */
}

/* Tâches individuelles */
.gantt-bar {
    background-color: var(--gantt-bar-color);
    padding: 0.5rem;
    border-radius: 5px;
    color: white;
    text-align: center;
    cursor: pointer;
    position: absolute; /* Cela permet aux barres de se placer selon leur position définie */
}







<p><strong>Description:</strong> ${task.description}</p>
                            <p><strong>Durée:</strong> ${task.duree} jours</p>
                            <p><strong>Regroupement:</strong> ${task.regroupement.join(", ")}</p>