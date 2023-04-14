from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    extra_price = fields.Float(string="Extra Price")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    extra_price = fields.Float(string="Extra Price")