Application web de gestion de stock avec alertes automatiques, rôles utilisateurs, export PDF, et tableau de bord.

## Installation

1. Cloner le projet :

   ```bash
   git clone https://github.com/votre-utilisateur/gestion-stock.git
   cd gestion-stock
   ```

2. Créer un environnement virtuel et installer les dépendances :

   ```bash
   python -m venv env
   source env/bin/activate  # ou env\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configurer la base MySQL (via PHPMyAdmin), adapter `settings.py`

4. Appliquer les migrations et créer un superutilisateur :

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Lancer le serveur :

   ```bash
   python manage.py runserver
   ```

## Fonctionnalités

* Gestion des produits, fournisseurs, catégories
* Suivi des mouvements de stock
* Alertes (stock critique, date de péremption)
* Rôles : admin, gestionnaire, employé
* Exports PDF (inventaire, historique)
* Dashboard interactif

## Accès

* `/login/` : connexion
* `/register/` : inscription (admin)
* `/dashboard/` : tableau de bord

