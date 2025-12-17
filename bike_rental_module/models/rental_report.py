from odoo import models, fields, api, tools

class RentalReport(models.Model):
    _name = 'rental.report'
    _description = 'Rapport de location'
    _auto = False
    _rec_name = 'bike_id'
    _order = 'start_date desc'

    # Dimensions
    bike_id = fields.Many2one('product.template', string='Vélo', readonly=True)
    customer_id = fields.Many2one('res.partner', string='Client', readonly=True)
    start_date = fields.Datetime(string='Date début', readonly=True)
    end_date = fields.Datetime(string='Date fin', readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('ongoing', 'En cours'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé'),
    ], string='Statut', readonly=True)
    
    # Mesures (pour les calculs)
    duration_days = fields.Float(string='Durée (jours)', readonly=True)
    duration_hours = fields.Float(string='Durée (heures)', readonly=True)
    price = fields.Float(string='Prix location', readonly=True)
    late_penalty = fields.Float(string='Pénalités', readonly=True)
    total_amount = fields.Float(string='Montant total', readonly=True)
    is_late = fields.Boolean(string='En retard', readonly=True)
    late_hours = fields.Float(string='Heures de retard', readonly=True)
    
    # Champs pour les analyses
    month = fields.Char(string='Mois', readonly=True)
    year = fields.Char(string='Année', readonly=True)
    
    # Nouveaux champs pour le taux d'occupation
    days_rented = fields.Float(string='Jours loués', readonly=True, group_operator='sum')

    def init(self):
        """Vue SQL pour les statistiques de location"""
        query = """
            CREATE OR REPLACE VIEW rental_report AS (
                SELECT
                    rc.id as id,
                    rc.bike_id,
                    rc.customer_id,
                    rc.start_date,
                    rc.end_date,
                    rc.state,
                    rc.duration_days,
                    rc.duration_hours,
                    rc.price,
                    rc.late_penalty,
                    rc.total_amount,
                    rc.is_late,
                    rc.late_hours,
                    TO_CHAR(rc.start_date, 'YYYY-MM') as month,
                    TO_CHAR(rc.start_date, 'YYYY') as year,
                    CASE 
                        WHEN rc.state IN ('confirmed', 'ongoing', 'done') 
                        THEN rc.duration_days 
                        ELSE 0 
                    END as days_rented
                FROM rental_contract rc
                WHERE rc.state != 'cancel'
            )
        """
        self.env.cr.execute(query)


class BikeOccupationReport(models.Model):
    """Rapport spécifique pour le taux d'occupation des vélos"""
    _name = 'bike.occupation.report'
    _description = 'Taux d\'occupation des vélos'
    _auto = False
    _rec_name = 'bike_id'

    bike_id = fields.Many2one('product.template', string='Vélo', readonly=True)
    total_days_rented = fields.Float(string='Total jours loués', readonly=True)
    number_of_rentals = fields.Integer(string='Nombre de locations', readonly=True)
    total_revenue = fields.Float(string='Revenu total', readonly=True)
    occupation_rate = fields.Float(string='Taux d\'occupation (%)', readonly=True)
    period_days = fields.Integer(string='Période (jours)', readonly=True)

    def init(self):
        """
        Vue SQL calculant le taux d'occupation par vélo
        Période = 365 jours (dernière année)
        """
        query = """
            CREATE OR REPLACE VIEW bike_occupation_report AS (
                SELECT
                    ROW_NUMBER() OVER (ORDER BY pt.id) as id,
                    pt.id as bike_id,
                    COALESCE(SUM(rc.duration_days), 0) as total_days_rented,
                    COALESCE(COUNT(rc.id), 0) as number_of_rentals,
                    COALESCE(SUM(rc.total_amount), 0) as total_revenue,
                    365 as period_days,
                    CASE 
                        WHEN SUM(rc.duration_days) > 0 
                        THEN ROUND(CAST((SUM(rc.duration_days) / 365.0) * 100 AS NUMERIC), 2)
                        ELSE 0 
                    END as occupation_rate
                FROM product_template pt
                LEFT JOIN rental_contract rc ON rc.bike_id = pt.id 
                    AND rc.state IN ('confirmed', 'ongoing', 'done')
                    AND rc.start_date >= (CURRENT_DATE - INTERVAL '365 days')
                WHERE pt.categ_id IN (
                    SELECT id FROM product_category WHERE name = 'Velos'
                )
                GROUP BY pt.id
            )
        """
        self.env.cr.execute(query)