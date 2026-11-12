# Préparer la première séance

Ce guide suit les consignes du cours : exécuter l'application sur Windows avec PostgreSQL, vérifier les deux rôles, envoyer le code sur GitHub, puis préparer le déploiement Vercel. Les comptes demandés par le professeur sont uniquement des comptes de démonstration. Ne place aucun mot de passe dans ce dépôt ou dans une capture d'écran.

## 1. Installer PostgreSQL

Télécharger l'installateur Windows depuis la [page officielle PostgreSQL](https://www.postgresql.org/download/windows/). Le serveur et pgAdmin sont inclus. Choisir une version stable et garder le port `5432`. Définir un mot de passe privé pour le compte technique `postgres`; ce mot de passe est différent des comptes de démonstration de l'application. StackBuilder est facultatif.

Si Windows bloque le lancement après le téléchargement, vérifier que le fichier provient bien du lien officiel PostgreSQL/EDB et que sa signature indique EnterpriseDB Corporation. Si Windows demande l'autorisation administrateur, la saisir sur l'ordinateur. Ne désactive pas SmartScreen ou l'antivirus.

## 2. Créer la base pour l'application

Dans pgAdmin, connecter le serveur PostgreSQL avec le mot de passe technique choisi à l'installation. Créer d'abord un rôle dans **Login/Group Roles** :

- nom : `incidentdesk_app`
- autoriser la connexion
- définir un mot de passe local distinct
- ne pas accorder les attributs de superutilisateur, création de rôles ou réplication

Puis créer une base nommée `incidentdesk` et sélectionner `incidentdesk_app` comme propriétaire. L'application et les migrations utiliseront ce compte limité, pas le compte technique `postgres`.

## 3. Relier le projet à PostgreSQL et migrer

Ouvrir PowerShell dans le dossier du projet qui contient `manage.py` (dans l'Explorateur : clic droit sur le dossier puis « Ouvrir dans le Terminal ») :

```powershell
Copy-Item .env.example .env
notepad .env
```

Dans `.env`, garder `DJANGO_SETTINGS_MODULE=config.settings.local` et remplacer `DATABASE_URL` par l'URL de la base, par exemple :

```text
DATABASE_URL=postgresql://incidentdesk_app:TON_MOT_DE_PASSE_BD@127.0.0.1:5432/incidentdesk
```

Choisir un mot de passe de base alphanumérique pour éviter d'encoder les caractères spéciaux d'une URL. Le fichier `.env` est ignoré par Git : ne jamais le pousser.

Exécuter ensuite :

```powershell
.\.venv\Scripts\python.exe manage.py check --settings=config.settings.local
.\.venv\Scripts\python.exe manage.py migrate --settings=config.settings.local
.\.venv\Scripts\python.exe manage.py createsuperuser --settings=config.settings.local
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --settings=config.settings.local
```

Ouvrir `http://127.0.0.1:8000/admin/` pour l'administration Django et `http://127.0.0.1:8000/accounts/login/` pour l'application.

## 4. Préparer les deux comptes de cours

Dans l'admin Django, créer deux utilisateurs ordinaires avec les noms demandés par le professeur. Définir les mots de passe dans les formulaires de l'admin, sans les enregistrer dans le dépôt. Pour le compte simple, laisser tous les groupes décochés. Pour le compte administrateur de l'application, cocher uniquement le groupe **Incident Administrators**. Ne pas activer `Superuser status` ni `Staff status` pour ce rôle applicatif : il doit gérer les incidents dans l'application sans obtenir l'administration Django.

Tester les deux connexions à `/accounts/login/`. Avec le compte simple, créer puis consulter un incident. Avec le compte administrateur, vérifier la visibilité globale et les actions d'administration prévues par l'application.

## 5. Versionner

Créer un dépôt personnel GitHub, de préférence vide, puis depuis le dossier du projet :

```powershell
git init -b main
git add .
git status
```

Avant le commit, vérifier que `.env`, `.venv`, `*.sqlite3` et `staticfiles` ne sont pas dans la liste. Ensuite :

```powershell
git commit -m "Prepare Incident Desk for the first course step"
git remote add origin https://github.com/TON_COMPTE/incident-desk.git
git push -u origin main
```

Dans GitHub → Actions, regarder les workflows de tests et sécurité, puis noter les résultats réels. Ne présente pas un workflow préparé comme une exécution déjà réussie.

## 6. Déployer sur Vercel

Après le push, créer le projet Vercel depuis ce dépôt GitHub, puis créer une base PostgreSQL hébergée et isolée pour cet environnement. Configurer les variables de production indiquées dans [DEPLOYMENT.md](DEPLOYMENT.md), avec une clé Django et des secrets distincts de ceux du poste local. Appliquer les migrations à cette base seulement après avoir vérifié son URL et le projet visé. Ne réutilise pas les comptes/mots de passe de démonstration comme accès de production.

Le compte Vercel, le dépôt GitHub et la base hébergée doivent être créés dans tes comptes personnels. La validation de ces écrans et du véritable déploiement ne peut se faire qu'après leur création.

## Hors du périmètre de lundi

La page CV, les protections CI/CD de mise en production et le scan DAST authentifié sont des étapes ultérieures du cours. Les rôles applicatifs et le workflow de contrôles sont déjà préparés dans cette copie, mais les exécutions GitHub, le déploiement, le scan ZAP et le rollback doivent encore être observés et documentés.
