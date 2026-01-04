# Projet Odoo - Magasin de Vélos (Vente & Location)

## Description du projet

Système de gestion intégré pour un magasin de vélos développé sur Odoo 19.0 Community Edition.
Le système permet de gérer :
- La vente de vélos et d'accessoires
- La location de vélos (courte et longue durée)
- Le suivi des clients et de leur historique
- La génération de rapports statistiques

## Contexte

Ce projet a été réalisé dans le cadre d'un projet académique simulant une mise en place réelle chez un client.
Le client souhaite une solution complète pour gérer son activité de vente et de location de vélos sans payer de licence Odoo Enterprise.

## Fonctionnalités principales

### Module de Location (bike_rental_module)

#### Gestion des contrats de location
- Création et suivi de contrats de location
- Tarification flexible (par heure ou par jour)
- Calcul automatique de la durée et du prix total
- Gestion des états (Brouillon, Confirmé, En cours, Terminé, Annulé)
- Vérification automatique de la disponibilité des vélos
- Détection et calcul des pénalités de retard
- Génération de factures Odoo pour les locations

#### Disponibilité des vélos
- Vue calendrier pour visualiser les périodes de location
- Vérification des chevauchements pour éviter les doubles réservations
- Passage automatique des états via tâche planifiée (cron)

#### Tarification
- Prix de location par heure et par jour configurables
- Calcul automatique des pénalités en cas de retard
- Montant total incluant location et pénalités

#### Reporting
- Rapport de location avec statistiques par vélo, client, période
- Taux d'occupation des vélos sur les 365 derniers jours
- Revenus totaux par vélo
- Nombre de locations par vélo

#### Facturation
- Création de factures clients natives Odoo (account.move)
- Lignes de facture automatiques pour la location
- Ligne de pénalité si retard détecté
- Lien bidirectionnel entre contrat et facture
- Protection contre la double facturation

### Module de Vente
- Gestion du catalogue produits (vélos, pièces, accessoires)
- Commandes clients
- Facturation
- Gestion des stocks

### Module Website
- Interface web pour les clients
- Consultation du catalogue en ligne

## Prérequis

### Logiciels requis
- Python 3.10 ou supérieur
- PostgreSQL 12 ou supérieur
- Git
- wkhtmltopdf (pour la génération de PDF)

### Dépendances Python
Les dépendances Odoo seront installées automatiquement lors de l'installation d'Odoo.

## Installation

### Méthode utilisée : Image Docker fournie par le professeur

Notre installation utilise l'image Docker **mvaodoo/odoo_training:latest** fournie par le professeur.
Cette méthode simplifie grandement l'installation et garantit un environnement Odoo 19.0 cohérent avec PostgreSQL préconfiguré.

#### Prérequis
- Docker Desktop installé et en cours d'exécution
- Git pour cloner le projet
- Accès à l'image Docker : `mvaodoo/odoo_training:latest`

---

### Étapes d'installation

#### 1. Cloner le dépôt du projet

```bash
git clone https://github.com/rayan-ad/odoo_project.git
cd odoo_project
```

#### 2. Récupérer l'image Docker du professeur

```bash
docker pull mvaodoo/odoo_training:latest
```

#### 3. Créer et lancer le conteneur Odoo

```bash
docker run -d \
  --name odoo_velo_container \
  -p 8069:8069 \
  -v "$(pwd)/bike_rental_module":/mnt/extra-addons/bike_rental_module \
  mvaodoo/odoo_training:latest
```

**Explication des paramètres :**
- `-d` : Lance le conteneur en arrière-plan (mode détaché)
- `--name odoo_velo_container` : Nom du conteneur pour faciliter la gestion
- `-p 8069:8069` : Mappe le port 8069 du conteneur vers le port 8069 de la machine hôte
- `-v "$(pwd)/bike_rental_module":/mnt/extra-addons/bike_rental_module` : Monte notre module personnalisé dans le conteneur
- `mvaodoo/odoo_training:latest` : Image Docker du professeur

**Note Windows :** Si vous êtes sur Windows avec PowerShell, remplacez `$(pwd)` par `${PWD}` :
```powershell
docker run -d --name odoo_velo_container -p 8069:8069 -v "${PWD}/bike_rental_module:/mnt/extra-addons/bike_rental_module" mvaodoo/odoo_training:latest
```

#### 4. Vérifier que le conteneur est en cours d'exécution

```bash
docker ps
```

Vous devriez voir une ligne avec `odoo_velo_container` et le statut `Up`.

#### 5. Accéder à l'interface Odoo

Ouvrir un navigateur et aller à : **http://localhost:8069**

#### 6. Créer la base de données

Lors de la première connexion, Odoo vous demandera de créer une base de données :

1. **Nom de la base de données** : `velo_shop12`
2. **Email** : admin@example.com (ou votre email)
3. **Mot de passe** : choisir un mot de passe administrateur
4. **Langue** : Français
5. **Pays** : France
6. Cliquer sur "Créer la base de données"

#### 7. Installer les modules dépendants

Une fois connecté à Odoo, installer les modules suivants (dans cet ordre) :

1. Aller dans **Apps** (Applications)
2. Cliquer sur **Mettre à jour la liste des applications**
3. Installer les modules :
   - **Sales** (sale) - Gestion des ventes
   - **Accounting** (account) - Comptabilité
   - **Contacts** (contacts) - Gestion des clients
   - **Website** (website) - Interface web
   - **Product** (product) - Gestion des produits

**Note :** Ces modules sont des dépendances pour bike_rental_module.

#### 8. Installer le module Bike Rental Module

1. Dans **Apps**, rechercher "Bike Rental" ou "bike_rental_module"
2. Cliquer sur **Installer**
3. Attendre la fin de l'installation (quelques secondes)

Le menu **Location** devrait maintenant apparaître dans la barre de navigation.

---

### Commandes Docker utiles

```bash
# Voir tous les conteneurs (en cours et arrêtés)
docker ps -a

# Voir les logs du conteneur en temps réel
docker logs -f odoo_velo_container

# Arrêter le conteneur
docker stop odoo_velo_container

# Redémarrer le conteneur
docker start odoo_velo_container

# Redémarrer le conteneur (stop + start)
docker restart odoo_velo_container

# Accéder au shell du conteneur (pour debugging)
docker exec -it odoo_velo_container bash

# Supprimer le conteneur (attention : perte des données si pas de volume persistant)
docker rm -f odoo_velo_container

# Voir les volumes Docker
docker volume ls
```

---

### Méthodes alternatives (pour référence)

<details>
<summary><strong>Option A : Installation manuelle depuis les sources</strong></summary>

Si vous souhaitez installer Odoo manuellement sans Docker (non utilisé dans ce projet) :

**Prérequis :**
- Python 3.10+
- PostgreSQL 12+
- wkhtmltopdf

**Étapes :**

```bash
# 1. Cloner Odoo 19.0
git clone https://github.com/odoo/odoo.git --depth 1 --branch 19.0 odoo-19
cd odoo-19

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Créer une base PostgreSQL
sudo -u postgres psql
CREATE DATABASE velo_shop12;
CREATE USER odoo WITH PASSWORD 'odoo';
GRANT ALL PRIVILEGES ON DATABASE velo_shop12 TO odoo;
\q

# 4. Créer un fichier de configuration odoo.conf
[options]
admin_passwd = admin
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = /chemin/vers/odoo-19/addons,/chemin/vers/odoo_project/bike_rental_module
http_port = 8069

# 5. Lancer Odoo
./odoo-bin -c odoo.conf -d velo_shop12 -i bike_rental_module --dev=all
```

Accès : http://localhost:8069

</details>

<details>
<summary><strong>Option B : Docker Compose personnalisé</strong></summary>

Si vous voulez créer votre propre environnement Docker Compose avec séparation web/db :

Créer un fichier `docker-compose.yml` :

```yaml
version: '3.8'
services:
  web:
    image: odoo:19.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./bike_rental_module:/mnt/extra-addons/bike_rental_module
      - odoo-web-data:/var/lib/odoo
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
      - POSTGRES_DB=velo_shop12

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

volumes:
  odoo-web-data:
  odoo-db-data:
```

Lancer avec :
```bash
docker-compose up -d
```

</details>

## Configuration initiale

### 1. Installer les modules dépendants

Avant d'installer le module bike_rental_module, assurez-vous que les modules suivants sont installés :
- Sales (sale)
- Accounting (account)
- Contacts (contacts)
- Product (product)
- Website (website)

### 2. Installer le module bike_rental_module

Aller dans : Apps > Mettre à jour la liste des applications > Rechercher "Bike Rental" > Installer

### 3. Configuration de base

#### Créer la catégorie "Velos"
1. Aller dans Inventaire > Configuration > Catégories de produits
2. Créer une catégorie "Velos"

#### Créer des vélos
1. Aller dans Location > Vélos à louer
2. Créer des produits de type vélo
3. Cocher "Disponible en location"
4. Définir les prix de location (heure et jour)

#### Créer des clients
1. Aller dans Contacts
2. Créer des fiches clients

## Utilisation

### Créer un contrat de location

1. Aller dans Location > Contrats de location
2. Cliquer sur "Créer"
3. Sélectionner un vélo disponible
4. Sélectionner un client
5. Définir la période de location (date début et fin)
6. Choisir le mode de facturation (heure ou jour)
7. Enregistrer et confirmer le contrat
8. Le système calcule automatiquement la durée et le prix

### Créer une facture pour un contrat

1. Ouvrir un contrat de location en état "En cours" ou "Terminé"
2. Cliquer sur "Créer facture Odoo"
3. La facture est créée automatiquement avec :
   - Une ligne pour la location (quantité x prix unitaire)
   - Une ligne pour les pénalités si retard détecté
4. La facture s'ouvre automatiquement
5. Le bouton disparaît pour éviter la duplication

### Suivre la disponibilité des vélos

1. Aller dans Location > Disponibilité
2. La vue calendrier affiche toutes les périodes de location
3. Les vélos sont différenciés par couleur

### Consulter les rapports

#### Rapport de location
1. Aller dans Location > Rapports > Rapport de location
2. Grouper par vélo, client, mois ou année
3. Visualiser les durées, prix, pénalités

#### Taux d'occupation
1. Aller dans Location > Rapports > Taux d'occupation
2. Visualiser le taux d'occupation de chaque vélo sur 365 jours
3. Voir le nombre de locations et le revenu total

## Structure du projet

```
odoo_project/
├── bike_rental_module/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── rental_contract.py      # Modèle principal des contrats
│   │   ├── rental_report.py        # Rapports SQL
│   │   └── product_template.py     # Extension du modèle produit
│   ├── views/
│   │   ├── rental_contract_views.xml
│   │   ├── rental_report_views.xml
│   │   ├── bike_occupation_views.xml
│   │   └── product_views.xml
│   ├── reports/
│   │   └── rental_contract_report.xml
│   ├── data/
│   │   └── rental_cron.xml         # Tâche planifiée
│   └── security/
│       └── ir.model.access.csv
└── README.md
```

## Hébergement et déploiement

### Solution actuelle : Docker local

Le projet utilise un conteneur Docker basé sur l'image **mvaodoo/odoo_training:latest** fournie par le professeur.

#### Type d'hébergement
- **Environnement** : Local (machine de développement)
- **Technologie** : Docker conteneur
- **Image utilisée** : mvaodoo/odoo_training:latest
- **Base de données** : PostgreSQL intégrée dans l'image Docker
- **Nom de la base** : velo_shop12
- **Port exposé** : 8069 (accessible via http://localhost:8069)

#### Processus d'installation (voir section Installation complète ci-dessus)
1. Installation de Docker Desktop
2. Récupération de l'image mvaodoo/odoo_training:latest
3. Création du conteneur avec volume monté pour le module
4. Création de la base de données velo_shop12 via l'interface web
5. Installation des modules dépendants (sale, account, contacts, website)
6. Installation du module bike_rental_module
7. Accès via http://localhost:8069

### Options alternatives d'hébergement

#### Option 1 : Docker Compose (recommandé pour production)

Créer un fichier `docker-compose.yml` :

```yaml
version: '3.8'
services:
  web:
    image: odoo:19.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./bike_rental_module:/mnt/extra-addons/bike_rental_module
      - odoo-web-data:/var/lib/odoo
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

volumes:
  odoo-web-data:
  odoo-db-data:
```

Lancer avec : `docker-compose up -d`

#### Option 2 : Serveur Ubuntu (VPS/Cloud)

1. Louer un VPS (OVH, DigitalOcean, AWS, etc.)
2. Installer Ubuntu Server 22.04
3. Suivre la procédure d'installation standard
4. Configurer un reverse proxy (Nginx)
5. Activer HTTPS avec Let's Encrypt
6. Configurer les sauvegardes automatiques

#### Option 3 : Odoo.sh (payant)

Solution officielle Odoo avec hébergement cloud managé.
- Déploiement automatique depuis Git
- Sauvegardes automatiques
- Environnements de staging

### Limites et risques de l'hébergement Docker local

#### Avantages de notre solution Docker
- **Isolation** : Le conteneur isole Odoo du système hôte
- **Portabilité** : Fonctionne de la même manière sur Windows, Mac et Linux
- **Reproductibilité** : Même environnement pour tous les membres du groupe
- **Facilité de gestion** : Démarrage/arrêt simple avec Docker
- **Pas de pollution du système** : Pas besoin d'installer Python, PostgreSQL, etc. directement

#### Limites actuelles
- **Accessible uniquement en local** : Depuis la machine qui héberge le conteneur
- **Pas de haute disponibilité** : Un seul conteneur, pas de redondance
- **Performances** : Limitées par les ressources de la machine locale
- **Persistance des données** : Les données sont dans le conteneur (risque de perte si suppression)

#### Risques
- **Sécurité** :
  - Pas de HTTPS (connexion HTTP non chiffrée)
  - Pas de firewall configuré
  - Port 8069 exposé sur localhost uniquement
- **Sauvegardes** :
  - Aucune sauvegarde automatique configurée
  - Les données sont dans le conteneur (volatiles si pas de volume persistant)
- **Perte de données** :
  - Si le conteneur est supprimé sans backup
  - En cas de panne matérielle
- **Accessibilité** :
  - Impossible d'accéder depuis une autre machine
  - Pas d'accès distant

#### Recommandations pour la production

Si ce projet devait être déployé en production pour un vrai client :

1. **Utiliser Docker Compose avec volumes persistants**
   - Séparer le conteneur web et le conteneur PostgreSQL
   - Utiliser des volumes Docker pour persister les données
   - Exemple fourni dans la section "Méthodes alternatives"

2. **Mettre en place des sauvegardes automatiques**
   ```bash
   # Sauvegarde de la base de données
   docker exec odoo_velo_container pg_dump -U odoo velo_shop12 > backup_$(date +%Y%m%d).sql

   # Automatiser avec cron (Linux/Mac) ou Task Scheduler (Windows)
   ```

3. **Configurer un reverse proxy avec HTTPS**
   - Nginx ou Traefik devant le conteneur Odoo
   - Certificat SSL avec Let's Encrypt
   - Redirection HTTP vers HTTPS

4. **Restreindre l'accès**
   - Configurer un VPN pour l'accès distant sécurisé
   - Ou utiliser un pare-feu pour limiter les IPs autorisées
   - Changer les mots de passe par défaut

5. **Monitoring et logs**
   - Configurer la rotation des logs Docker
   - Monitorer les ressources (CPU, mémoire, disque)
   - Alertes en cas de problème

6. **Tester les restaurations**
   - Tester régulièrement la procédure de restauration
   - Vérifier l'intégrité des backups

7. **Utiliser un hébergement cloud**
   - AWS, Google Cloud, OVH, DigitalOcean
   - Permet scalabilité et haute disponibilité
   - Sauvegardes automatiques et snapshots

## Sauvegardes

### Sauvegarder la base de données depuis le conteneur Docker

```bash
# Sauvegarder la base de données velo_shop12
docker exec odoo_velo_container pg_dump -U odoo velo_shop12 > backup_velo_shop12_$(date +%Y%m%d).sql

# Vérifier que le fichier de sauvegarde a été créé
ls -lh backup_velo_shop12_*.sql
```

### Restaurer la base de données dans le conteneur

```bash
# Restaurer depuis un fichier de sauvegarde
docker exec -i odoo_velo_container psql -U odoo velo_shop12 < backup_velo_shop12_20250104.sql
```

### Sauvegarder les données du conteneur (filestore)

```bash
# Sauvegarder tous les fichiers uploadés (images, attachments, etc.)
docker exec odoo_velo_container tar -czf /tmp/filestore_backup.tar.gz /var/lib/odoo/filestore/velo_shop12

# Copier la sauvegarde hors du conteneur
docker cp odoo_velo_container:/tmp/filestore_backup.tar.gz ./filestore_backup_$(date +%Y%m%d).tar.gz
```

### Sauvegarder le conteneur complet

```bash
# Créer une image du conteneur actuel (avec toutes les données)
docker commit odoo_velo_container odoo_velo_backup:$(date +%Y%m%d)

# Exporter l'image vers un fichier tar
docker save odoo_velo_backup:$(date +%Y%m%d) -o odoo_velo_backup_$(date +%Y%m%d).tar

# Compresser pour économiser de l'espace
gzip odoo_velo_backup_$(date +%Y%m%d).tar
```

### Restaurer depuis une sauvegarde d'image

```bash
# Charger l'image depuis le fichier tar
gunzip odoo_velo_backup_20250104.tar.gz
docker load -i odoo_velo_backup_20250104.tar

# Créer un nouveau conteneur depuis l'image sauvegardée
docker run -d --name odoo_velo_restored -p 8069:8069 odoo_velo_backup:20250104
```

## Tests

### Tester la création d'un contrat

1. Créer un vélo test
2. Créer un client test
3. Créer un contrat avec date de début dans 1 heure
4. Attendre que le cron passe le contrat à "En cours"
5. Terminer le contrat
6. Vérifier les calculs de prix et pénalités

### Tester la disponibilité

1. Créer deux contrats pour le même vélo
2. S'assurer que les périodes ne se chevauchent pas
3. Essayer de créer un chevauchement (doit être bloqué)

### Tester la facturation

1. Créer un contrat terminé
2. Cliquer sur "Créer facture Odoo"
3. Vérifier que la facture contient les bonnes lignes
4. Vérifier que le bouton disparaît
5. Essayer de recréer une facture (doit être bloqué)

## Technologies utilisées

- **Backend** : Odoo 19.0 Community (Python)
- **Base de données** : PostgreSQL 15
- **Frontend** : QWeb (templating Odoo), JavaScript, XML
- **ORM** : Odoo ORM
- **Reporting** : Vues SQL matérialisées, QWeb Reports

## Architecture technique

### Modèles de données

#### rental.contract
Modèle principal gérant les contrats de location avec calculs automatiques de durée, prix, et pénalités.

#### rental.report
Vue SQL matérialisée pour les rapports de location avec agrégations par vélo, client, période.

#### bike.occupation.report
Vue SQL calculant le taux d'occupation des vélos sur 365 jours avec statistiques de revenus.

#### product.template (étendu)
Extension du modèle produit standard avec champs spécifiques à la location.

### Workflow des contrats

1. **Brouillon** : Création initiale
2. **Confirmé** : Validation et réservation du vélo
3. **En cours** : Location active (passage automatique via cron)
4. **Terminé** : Vélo rendu, calcul des pénalités
5. **Annulé** : Contrat annulé

### Automatisations

- Passage automatique des contrats confirmés à "En cours" (cron toutes les heures)
- Passage automatique des contrats en cours à "Terminé" quand la période est expirée
- Calcul automatique des pénalités de retard
- Détection automatique des retards

## Contribuer

Ce projet est un projet académique. Pour toute question ou suggestion :
1. Ouvrir une issue sur GitHub
2. Créer une pull request avec vos modifications

## Auteurs

- Projet réalisé dans le cadre du cours Odoo 2025
- Groupe : Abdillahi Darar Rayan , Barbu Eric-Dan , AL bakali Roudaina

## Licence

Ce projet est réalisé à des fins éducatives.

## Support et contact

Pour toute question technique :
- Consulter la documentation Odoo : https://www.odoo.com/documentation/19.0/
- Consulter les forums Odoo : https://www.odoo.com/forum

## Améliorations futures possibles

- Ajout d'un module de gestion de maintenance des vélos
- Intégration d'un système de réservation en ligne
- Notifications par email pour les retards
- Application mobile pour les clients
- Gestion des contrats d'assurance
- Système de fidélité pour les clients réguliers
- Intégration avec des systèmes de paiement en ligne
- Géolocalisation des vélos avec GPS
