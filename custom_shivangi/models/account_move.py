from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    cash_discount = fields.Selection([
        ('500', '500'),
        ('300', '300')
    ], string='Cash Discount', copy=False)
    truck_no = fields.Many2one('truck.no',string="Truck No")
    empty_truck_weight = fields.Float(string="Empty Truck Weight")
    loaded_truck_weight = fields.Float(string="Loaded Truck Weight")
    final_weight = fields.Float(string='Final Weight')
    consignee_billing_discount = fields.Selection([
        ('50', '50'),
    ], string='Consignee Billing Discount', copy=False)
    invoice_discount = fields.Selection([
        ('1000', '1000'),
    ], string='Invoice Discount', copy=False)
    custom_charges = fields.Float(string="Custom Charges")
    freight_discount  = fields.Float(string="Freight Discount")
    freight_difference = fields.Float(string="Freight Difference")
    booking_price = fields.Float(string="Booking Price")
    for_price = fields.Selection([
        ('200', '200'),
    ], string='F.O.R', copy=False)



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    bundle = fields.Float(string="Bundle")
    avg_wt_bundle = fields.Float(string="Avg WT/Bundle (kg)")
    extra_charges = fields.Float(string="Extra Charges")
    final_rate = fields.Float(string="Final Rate")