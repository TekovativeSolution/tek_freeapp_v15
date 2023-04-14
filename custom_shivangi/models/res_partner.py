# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from functools import reduce


class ResPartner(models.Model):
    _inherit = 'res.partner'

    status_selection = fields.Selection([('int', 'Interested'),
                                         ('not_int', 'Not Interested')], string="Status")
    dealer_pro_selection = fields.Selection([('dealer', 'Dealer'),
                                             ('project', 'Project')], string="Dealer/Project")
    desg_selection = fields.Selection([('cont', 'Contractor'),
                                       ('sub_cont', 'Sub Contractor'),
                                       ('engineer', 'Engineer'),
                                       ('arch', 'Architect')], string="Designation")
    ref = fields.Char(string="Reference")
    existing_broker = fields.Char(string="Existing Broker/Distributor")
    capacity = fields.Integer(string="Capacity")
    brand = fields.Char(string="Brand")
    stage_id = fields.Many2one("stage.name", string="Stage")
    project_type_id = fields.Many2one("project.type", string="Project Type")
    city_id = fields.Many2one("city.name", string="City")
    total_proj_size = fields.Integer(string="Total Project Size(mt)")
    district_id = fields.Many2one("district.name", string="District")
    is_distributor = fields.Boolean(string="Is Distributor?")
    booking_limit = fields.Float(string="Booking Limit")
    pending_limit = fields.Float(string="Pending Limit",compute='_compute_pending_qty')

    @api.onchange('city_id')
    def _onchange_city(self):
        if self.city_id:
            self.district_id = self.city_id.district_id.id
            self.state_id = self.city_id.district_id.state_id.id

    def _compute_pending_qty(self):
        for record in self:
            booking_ids = self.env['order.booking'].search([('distributor_id','=',record.id),('state','=','done')])
            if booking_ids and self.booking_limit:
                self.pending_limit = self.booking_limit - reduce(lambda x, y: x + y, booking_ids.mapped('pending_quantity'), 0.0)
            else:
                self.pending_limit = self.booking_limit