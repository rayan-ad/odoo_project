{
    'name': 'Bike Rental Module',
    'version': '1.0',
    'summary': 'Module pour la gestion de location des vélos',
    'depends': ['base', 'product', 'contacts', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/rental_contract_views.xml',
        'views/rental_report_views.xml',
        'views/bike_occupation_views.xml',
        'reports/rental_contract_report.xml',   # <-- doit être avant views qui l'utilise
        'data/rental_cron.xml',
    ],

    'installable': True,
    'application': True,
}
