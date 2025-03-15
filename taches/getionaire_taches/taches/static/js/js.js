// const userActuDiv = document.getElementById('user-actu');
// const userAdminConstDiv = document.getElementById('user-admin-const');

// // Vérifier si les éléments existent avant d'essayer de récupérer leurs attributs
// const userActu = userActuDiv ? userActuDiv.getAttribute('data-user-actu') : null;
// const userAdminConst = userAdminConstDiv ? userAdminConstDiv.getAttribute('data-user-admin') : null;

// // Déclaration de la variable en dehors de l'if
// let userActuisAdmin = userActu === userAdminConst;

// console.log("L'utilisateur est admin :", userActuisAdmin);

// const divUrlAddQqun = document.getElementById('data-url-add');
// const urlAddQqun = divUrlAddQqun ? divUrlAddQqun.getAttribute('data-url-add-qqun') : null;
// console.log(urlAddQqun);

// // Récupérer le token CSRF depuis le meta tag
// const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
// console.log(csrfToken);

// document.getElementById('params').addEventListener("click", function() {
//     Swal.fire({
//         title: 'Paramètres',
//         html: `
//             ${userActuisAdmin ? `
//                 <div id="div-inviter">
//                     <form id="invitation-form">
//                         <input type="text" name="user" id="user" placeholder="Nom d'utilisateur">
//                         <button type="submit">Inviter</button>
//                     </form>
//                 </div>` : ''}
//         `,
//         showConfirmButton: false,
//         showCloseButton: true
//     });

//     // Ajouter l'événement submit au formulaire
//     const form = document.getElementById('invitation-form');
//     if (form) {
//         form.addEventListener('submit', function(event) {
//             event.preventDefault();  // Empêcher le formulaire de se soumettre normalement

//             const userName = document.getElementById('user').value;  // Récupérer le nom d'utilisateur
//             const data = new FormData();
//             data.append('user', userName);  // Ajouter les données du formulaire
//             data.append('csrfmiddlewaretoken', csrfToken);  // Ajouter le token CSRF

//             fetch(urlAddQqun, {
//                 method: 'POST',
//                 headers: {
//                     'X-CSRFToken': csrfToken,
//                     'Content-Type': 'application/x-www-form-urlencoded',  // Assure que l'en-tête est correct pour les formulaires
//                 },
//                 body: data
//             })
//             .then(response => {
//                 // Vérifie si la réponse est OK (status 200-299)
//                 if (!response.ok) {
//                     throw new Error('Erreur du serveur');
//                 }
//                 return response.json();  // Parse la réponse en JSON
//             })
//             .then(data => {
//                 console.log(data);  // Affiche les données reçues du serveur
//                 if (data.success) {
//                     Swal.fire('Succès', 'L\'invitation a été envoyée avec succès.', 'success');
//                 } else {
//                     Swal.fire('Erreur', 'Il y a eu un problème avec l\'invitation.', 'error');
//                 }
//             })
//             .catch(error => {
//                 console.error('Erreur lors de l\'envoi:', error);
//                 Swal.fire('Erreur', 'Une erreur est survenue lors de l\'envoi de l\'invitation.', 'error');
//             });
            
//         });
//     }
// });
