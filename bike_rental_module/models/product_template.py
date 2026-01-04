"""
Extension du modèle produit pour supporter la location de vélos.

Ce module ajoute des champs spécifiques à la location sur le modèle
standard product.template d'Odoo.
"""

from odoo import models, fields


class ProductTemplate(models.Model):
    """
    Héritage du modèle product.template pour ajouter les fonctionnalités de location.

    Ajoute trois champs :
    - rental_available : indique si le produit peut être loué
    - rental_price_hour : prix de location par heure
    - rental_price_day : prix de location par jour

    Ces champs permettent de gérer la tarification flexible des locations
    et de filtrer facilement les produits disponibles en location.

    Utilise _inherit pour étendre le modèle existant sans le remplacer.
    """
    _inherit = 'product.template'

    rental_available = fields.Boolean(
        string="Disponible en location",
        default=False,
        help="Cocher si ce produit peut être loué aux clients"
    )

    rental_price_hour = fields.Float(
        string="Prix location / heure",
        help="Tarif de location par heure pour ce produit"
    )

    rental_price_day = fields.Float(
        string="Prix location / jour",
        help="Tarif de location par jour pour ce produit"
    )
