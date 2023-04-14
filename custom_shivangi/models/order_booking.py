from odoo import api, fields, models, _
import time
from functools import reduce
from odoo.exceptions import UserError

class OrderBooking(models.Model):
    _name = 'order.booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name desc'
    _description = "Order Booking"

    name = fields.Char(string="Name",copy=False)
    distributor_id = fields.Many2one('res.partner',string="Distributor", track_visibility='onchange')
    quantity = fields.Float(string="Order Qty(MT)", track_visibility='onchange')
    pending_quantity = fields.Float(string="Pending Quantity", track_visibility='onchange',compute='_compute_pending_qty')
    rate = fields.Float(string="Rate", track_visibility='onchange')
    order_date = fields.Date(string="Order Date",default=time.strftime('%Y-%m-%d'), track_visibility='onchange')
    pending_limit = fields.Float(string="Pending Limit", track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Booked'),
        ('completed', 'Completed'),
        ('cancel', 'Cancel'),
    ], string='Status', readonly=True, copy=False, default='draft', track_visibility='onchange')
    order_count = fields.Integer(compute='_compute_orders_number', string='Number of Orders')

    def _compute_orders_number(self):
        """:fun: Count len of sale order. """

        for record in self:
            sale_orders = self.env['sale.order'].search([('booking_id','=',record.id)])
            record.order_count = len(sale_orders)

    def _compute_pending_qty(self):
        for record in self:
            sale_order = self.env['sale.order'].search([('booking_id', '=', record.id),('state','=','sale')])
            if sale_order:
                record.pending_quantity = record.quantity - reduce(lambda x, y: x + y, sale_order.order_line.mapped('product_uom_qty'), 0.0)
                if record.pending_quantity == 0:
                    record.state = 'completed'
            else:
                record.pending_quantity = record.quantity


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if vals:
                vals['name'] = self.env['ir.sequence'].next_by_code('order.booking') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('order.booking', sequence_date=seq_date) or _(
                    'New')
        result = super(OrderBooking, self).create(vals)
        return result

    @api.onchange('distributor_id')
    def onchange_distributor_id(self):
        """ :fun: Show only distributor partner."""

        partner_id = self.env['res.partner'].search([('is_distributor', '!=', False)])
        if partner_id:
            return {'domain': {'distributor_id': [('id', 'in', partner_id.ids)]}}
        else:
            return {'domain': {'distributor_id': [('id', 'in', [])]}}

    def open_quotation(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        action['context'] = {'default_partner_id': self.distributor_id.id,
                             'default_partner_invoice_id': self.distributor_id.id,
                             'default_booking_price': self.rate,
                             'default_booking_id':self.id}
        return action

    def action_view_sale_order(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        order_ids = self.env['sale.order'].search([('booking_id', '=', self.id)])
        if order_ids:
            action['domain'] = [('id', 'in', order_ids.ids)]
        else:
            action['domain'] = [('id', 'in', [])]
        action['views'] = [(self.env.ref('sale.view_order_tree').id, 'tree'),(self.env.ref('sale.view_order_form').id, 'form')]

        return action

    def done_booking(self):
        if self.quantity and self.quantity > self.distributor_id.pending_limit:
            raise UserError(_("You can not create more than %s pending quantity booking order.") % (self.distributor_id.pending_limit))

        self.state = 'done'


    





