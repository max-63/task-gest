#!/bin/bash

# Demander le message de commit
echo "📢 Entre le message du commit :"
read commit_message

# Ajouter tous les fichiers
git add .

# Faire le commit avec le message saisi
git commit -m "$commit_message"

# Pousser vers GitHub (branche actuelle)
git push origin $(git branch --show-current)

echo "✅ Commit et push effectués avec succès ! 🚀"
