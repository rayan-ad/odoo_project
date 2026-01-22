{
    'name': 'Bike Rental Module',
    'version': '1.0',
    'summary': 'Module pour la gestion de location des vélos',
    'description': """
        Module complet de gestion de location de vélos pour Odoo 19.0

        Fonctionnalités :
        - Gestion des contrats de location avec workflow complet
        - Tarification flexible (horaire ou journalière)
        - Calcul automatique des pénalités de retard
        - Vérification de disponibilité des vélos
        - Génération de factures Odoo
        - Rapports statistiques (taux d'occupation, revenus)
        - Vue calendrier pour visualiser la disponibilité
        - Tâche automatique pour mettre à jour les états
    """,
    'author': 'Votre Nom',
    'category': 'Sales/Rental',
    'depends': [
        'base',      # Framework de base Odoo
        'product',   # Gestion des produits (vélos)
        'contacts',  # Gestion des clients
        'sale',      # Module de vente
        'website',   # Interface web
        'account',   # Module comptable pour la facturation
    ],
    'data': [
        # Sécurité : définition des droits d'accès aux modèles
        'security/ir.model.access.csv',

        # Vues : interfaces utilisateur
        'views/product_views.xml',           # Extension des vues produit
        'views/rental_contract_views.xml',   # Vues principales des contrats
        'views/rental_report_views.xml',     # Vues des rapports
        'views/bike_occupation_views.xml',   # Vue du taux d'occupation

        # Rapports PDF
        'reports/rental_contract_report.xml',   # Template PDF des contrats (doit être avant views)

        # Données et automatisations
        'data/rental_cron.xml',   # Tâche planifiée pour mise à jour auto des états
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
