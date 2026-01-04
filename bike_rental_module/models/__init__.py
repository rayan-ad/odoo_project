"""
Initialisation des modèles du module Bike Rental.

Ordre d'import :
1. product_template : Extension du modèle produit (doit être chargé en premier)
2. rental_contract : Modèle principal des contrats de location
3. rental_report : Modèles de reporting (vues SQL)

Chaque import charge un fichier Python contenant un ou plusieurs modèles Odoo.
"""

from . import product_template
from . import rental_contract
from . import rental_report
