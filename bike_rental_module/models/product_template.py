from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rental_available = fields.Boolean(
        string="Disponible en location"
    )

    rental_price_hour = fields.Float(
        string="Prix location / heure"
    )

    rental_price_day = fields.Float(
        string="Prix location / jour"
    )
