from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class RentalContract(models.Model):
    _name = 'rental.contract'
    _description = 'Contrat de location de vélo'
    _order = 'start_date desc'

    bike_id = fields.Many2one(
        'product.template',
        string="Vélo",
        required=True,
        domain=[
            ('categ_id.name', '=', 'Velos'),
            ('rental_available', '=', True),
        ],  # seulement les vélos dispo en location
    )

    name = fields.Char(
        string="Référence",
        required=True,
        default="Nouveau",
        copy=False,
    )

    customer_id = fields.Many2one(
        'res.partner',
        string="Client",
        required=True
    )

    start_date = fields.Datetime(string="Date début", required=True)
    end_date = fields.Datetime(string="Date fin", required=True)

    notes = fields.Text("Notes")

    # Comment on facture : par heure ou par jour
    billing_unit = fields.Selection(
        [
            ('hour', 'Par heure'),
            ('day', 'Par jour'),
        ],
        string="Mode de facturation",
        required=True,
        default='day',
    )

    # Durée calculée
    duration_hours = fields.Float(
        string="Durée (heures)",
        compute="_compute_duration",
        store=True,
    )

    duration_days = fields.Float(
        string="Durée (jours)",
        compute="_compute_duration",
        store=True,
    )

    # Prix unitaire (pris sur le vélo)
    unit_price = fields.Float(
        string="Prix unitaire",
        compute="_compute_unit_price",
        store=True,
    )

    # Prix total calculé
    price = fields.Float(
        string="Prix total",
        compute="_compute_total_price",
        store=True,
    )
    actual_return_date = fields.Datetime(
        string="Date réelle de retour",
        readonly=True,
        help="Date et heure auxquelles le vélo a réellement été rendu."
    )

    is_late = fields.Boolean(
        string="En retard",
        compute="_compute_late",
        store=True
    )

    late_hours = fields.Float(
        string="Heures de retard",
        compute="_compute_late",
        store=True,
        help="Nombre d'heures de retard par rapport à l'heure de fin prévue."
    )
    late_penalty = fields.Float(
        string="Pénalités de retard",
        compute="_compute_late_penalty",
        store=True,
        help="Pénalités = prix location horaire × heures de retard"
    )

    total_amount = fields.Float(
        string="Montant total",
        compute="_compute_total_amount",
        store=True,
        help="Prix location + pénalités de retard"
    )


    state = fields.Selection(
        [
            ('draft', 'Brouillon'),
            ('confirmed', 'Confirmé'),
            ('ongoing', 'En cours'),
            ('done', 'Terminé'),
            ('cancel', 'Annulé'),
        ],
        string="Statut",
        default='draft'
    )


    #=====================
    # Respect des contrat
    #=====================

    @api.depends('state', 'end_date', 'actual_return_date')
    def _compute_late(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.is_late = False
            rec.late_hours = 0.0

            # On ne regarde que les contrats en cours ou terminés
            if rec.end_date and rec.state in ('ongoing', 'done'):
                # Si le contrat est terminé, on prend la date réelle
                ref_date = rec.actual_return_date or now

                if ref_date > rec.end_date:
                    delta = ref_date - rec.end_date
                    rec.late_hours = delta.total_seconds() / 3600.0
                    rec.is_late = True


    # ===============================
    #   CONTRAINTES SUR LES DATES
    # ===============================
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.start_date >= rec.end_date:
                    raise ValidationError(
                        "La date de fin doit être strictement après la date de début."
                    )
                if rec.start_date < fields.Datetime.now():
                    raise ValidationError(
                        "La date de début ne peut pas être dans le passé."
                    )

    # =========================
    #   DURÉE (heures & jours)
    # =========================
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for rec in self:
            rec.duration_hours = 0
            rec.duration_days = 0
            if rec.start_date and rec.end_date and rec.end_date > rec.start_date:
                delta = rec.end_date - rec.start_date
                hours = delta.total_seconds() / 3600
                rec.duration_hours = hours
                rec.duration_days = hours / 24

    # =========================
    #   PRIX UNITAIRE
    # =========================
    @api.depends('bike_id', 'billing_unit')
    def _compute_unit_price(self):
        for rec in self:
            price = 0
            if rec.bike_id:
                if rec.billing_unit == 'hour':
                    price = rec.bike_id.rental_price_hour
                elif rec.billing_unit == 'day':
                    price = rec.bike_id.rental_price_day
            rec.unit_price = price

    # =========================
    #   PRIX TOTAL
    # =========================
    @api.depends('unit_price', 'duration_hours', 'duration_days', 'billing_unit')
    def _compute_total_price(self):
        for rec in self:
            if rec.billing_unit == 'hour':
                rec.price = rec.unit_price * rec.duration_hours
            else:
                rec.price = rec.unit_price * rec.duration_days

    # =========================
    #   DISPONIBILITÉ DU VÉLO
    # =========================
    def _check_bike_availability(self):
        """
        Vérifie qu'il n'existe pas déjà un autre contrat confirmé/en cours
        pour le même vélo et une période qui se chevauche.
        """
        for rec in self:
            if not (rec.bike_id and rec.start_date and rec.end_date):
                continue

            domain = [
                ('id', '!=', rec.id),                 # pas moi-même
                ('bike_id', '=', rec.bike_id.id),    # même vélo
                ('state', 'in', ['confirmed', 'ongoing']),
                ('start_date', '<', rec.end_date),
                ('end_date', '>', rec.start_date),
            ]
            overlapping = self.search_count(domain)
            if overlapping:
                raise ValidationError(
                    f"Le vélo {rec.bike_id.display_name} est déjà loué sur cette période."
                )

    #Passer automatiquement le statut à "En cours" quand le temps arrive
    @api.model
    def cron_update_contract_states(self):
        """Met à jour automatiquement l'état des contrats en fonction du temps."""
        now = fields.Datetime.now()

        # 1. Passer en 'ongoing' les contrats confirmés dont la date de début est passée
        to_start = self.search([
            ('state', '=', 'confirmed'),
            ('start_date', '<=', now),
        ])
        if to_start:
            to_start.action_start()

        # 2. (optionnel) Terminer automatiquement les contrats en cours dont la fin est passée
        to_done = self.search([
            ('state', '=', 'ongoing'),
            ('end_date', '<=', now),
        ])
        if to_done:
            to_done.action_done()


    # =========================
    #   ACTIONS / WORKFLOW
    # =========================
    def action_confirm(self):
        self._check_bike_availability()
        self.state = 'confirmed'

    def action_start(self):
        self._check_bike_availability()
        self.state = 'ongoing'

    def action_done(self):
        self.write({
            'state': 'done',
            'actual_return_date': fields.Datetime.now(),}
        )
        


    def action_cancel(self):
        self.state = 'cancel'

    def action_reset_draft(self):
        self.state = 'draft'
    
    def action_print_contract(self):
        # Chercher le rapport par son nom complet
        report = self.env['ir.actions.report'].search([
            ('report_name', '=', 'bike_rental_module.rental_contract_template')
        ], limit=1)
        
        if not report:
            raise UserError("Le rapport n'existe pas. Vérifie que le fichier XML est bien chargé.")
        
        return report.report_action(self)

    @api.depends('late_hours', 'unit_price', 'billing_unit')
    def _compute_late_penalty(self):
        for rec in self:
            rec.late_penalty = 0.0
            if rec.is_late and rec.late_hours > 0:
                # Utiliser le prix horaire pour calculer la pénalité
                hourly_rate = rec.unit_price if rec.billing_unit == 'hour' else rec.unit_price / 24
                rec.late_penalty = hourly_rate * rec.late_hours

    @api.depends('price', 'late_penalty')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.price + rec.late_penalty
