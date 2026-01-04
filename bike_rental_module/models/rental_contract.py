"""
Module de gestion des contrats de location de vélos.

Ce module permet de créer et gérer des contrats de location avec :
- Calcul automatique de la durée et du prix
- Gestion des pénalités de retard
- Vérification de disponibilité des vélos
- Génération de factures Odoo
- Workflow complet de location (brouillon -> confirmé -> en cours -> terminé)
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class RentalContract(models.Model):
    """
    Modèle principal pour la gestion des contrats de location de vélos.

    Gère l'ensemble du cycle de vie d'une location :
    - Réservation et vérification de disponibilité
    - Calcul automatique des durées et prix
    - Détection et facturation des retards
    - Génération de factures clients
    """
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

    invoice_id = fields.Many2one(
        'account.move',
        string="Facture",
        readonly=True,
        copy=False,
        help="Facture Odoo générée pour ce contrat de location"
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


    # ====================================
    # CALCUL DES RETARDS ET PENALITES
    # ====================================

    @api.depends('state', 'end_date', 'actual_return_date')
    def _compute_late(self):
        """
        Calcule si le contrat est en retard et le nombre d'heures de retard.

        Logique :
        - Pour les contrats "en cours" : compare la date actuelle avec la date de fin prévue
        - Pour les contrats "terminés" : compare la date de retour réelle avec la date de fin prévue
        - Calcule le nombre d'heures de retard pour la facturation des pénalités

        Le retard est calculé uniquement pour les contrats confirmés ou terminés,
        pas pour les brouillons ou annulés.
        """
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
        """
        Valide la cohérence des dates de début et de fin du contrat.

        Règles de validation :
        1. La date de fin doit être strictement après la date de début
        2. La date de début ne peut pas être dans le passé

        Lève une ValidationError si les règles ne sont pas respectées.
        Cette méthode est appelée automatiquement à chaque modification
        des champs start_date ou end_date.
        """
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
        """
        Calcule automatiquement la durée de location en heures et en jours.

        Le calcul se base sur la différence entre la date de fin et la date de début.
        Les deux durées sont stockées pour permettre une facturation flexible :
        - duration_hours : utilisée pour la facturation horaire
        - duration_days : utilisée pour la facturation journalière

        Ce calcul est déclenché automatiquement à chaque modification des dates.
        """
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
        Vérifie la disponibilité du vélo pour la période demandée.

        Cette méthode empêche la double réservation en vérifiant qu'aucun autre
        contrat confirmé ou en cours n'existe pour le même vélo sur une période
        qui chevauche la période demandée.

        Algorithme de détection de chevauchement :
        - Un chevauchement existe si :
          (start_date_existant < end_date_nouveau) ET (end_date_existant > start_date_nouveau)

        Seuls les contrats confirmés et en cours sont vérifiés.
        Les brouillons et annulés n'affectent pas la disponibilité.

        Lève une ValidationError si le vélo est déjà réservé sur cette période.
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

    @api.model
    def cron_update_contract_states(self):
        """
        Tâche planifiée pour mettre à jour automatiquement les états des contrats.

        Cette méthode est exécutée périodiquement (toutes les heures par défaut)
        via une tâche cron Odoo.

        Actions automatiques :
        1. Passe les contrats "Confirmés" à "En cours" quand la date de début est atteinte
        2. Passe les contrats "En cours" à "Terminé" quand la date de fin est dépassée

        Cela évite aux utilisateurs d'avoir à changer manuellement les états
        et assure une transition fluide du workflow.

        Note : Les dates sont comparées avec l'heure actuelle du serveur.
        """
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

    def action_create_invoice(self):
        """
        Crée une facture client Odoo (account.move) pour ce contrat de location.

        Workflow :
        1. Vérifie qu'aucune facture n'existe déjà (protection contre duplication)
        2. Vérifie que le contrat est dans un état facturable (en cours ou terminé)
        3. Crée une facture avec les informations du contrat
        4. Ajoute une ligne pour la location du vélo
        5. Ajoute une ligne pour les pénalités de retard si applicable
        6. Lie la facture au contrat via le champ invoice_id
        7. Ouvre automatiquement la facture créée

        Calcul des lignes de facture :
        - Ligne location : quantité = durée (heures ou jours) × prix unitaire
        - Ligne pénalité : quantité = jours de retard × prix pénalité par jour

        Returns:
            dict: Action Odoo pour ouvrir la facture créée dans une vue formulaire

        Raises:
            UserError: Si une facture existe déjà ou si l'état n'est pas valide
        """
        self.ensure_one()

        # Vérifier qu'une facture n'existe pas déjà
        if self.invoice_id:
            raise UserError("Une facture a déjà été créée pour ce contrat.")

        # Vérifier que le contrat est dans un état valide
        if self.state not in ('ongoing', 'done'):
            raise UserError("Le contrat doit être 'En cours' ou 'Terminé' pour créer une facture.")

        # Créer la facture
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_origin': self.name,
            'invoice_line_ids': [],
        }

        # Ligne 1 : Location du vélo
        # Déterminer la quantité et le prix unitaire selon le mode de facturation
        if self.billing_unit == 'day':
            quantity = self.duration_days
            unit_price = self.unit_price
            description = f"Location vélo {self.bike_id.name} - {self.duration_days:.2f} jours"
        else:  # hour
            quantity = self.duration_hours
            unit_price = self.unit_price
            description = f"Location vélo {self.bike_id.name} - {self.duration_hours:.2f} heures"

        # Créer la ligne de location
        invoice_line_vals = {
            'product_id': self.bike_id.product_variant_id.id if self.bike_id.product_variant_id else False,
            'name': description,
            'quantity': quantity,
            'price_unit': unit_price,
        }
        invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

        # Ligne 2 : Pénalités de retard (si applicable)
        if self.is_late and self.late_hours > 0:
            # Calculer le prix unitaire de la pénalité par jour
            hourly_rate = self.unit_price if self.billing_unit == 'hour' else self.unit_price / 24
            late_days = self.late_hours / 24
            penalty_unit_price = hourly_rate * 24  # Prix par jour de retard

            penalty_line_vals = {
                'name': f"Pénalité retard - {self.late_hours:.2f} heures ({late_days:.2f} jours)",
                'quantity': late_days,
                'price_unit': penalty_unit_price,
            }
            invoice_vals['invoice_line_ids'].append((0, 0, penalty_line_vals))

        # Créer la facture
        invoice = self.env['account.move'].create(invoice_vals)

        # Lier la facture au contrat
        self.invoice_id = invoice.id

        # Retourner l'action pour ouvrir la facture
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facture',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

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
