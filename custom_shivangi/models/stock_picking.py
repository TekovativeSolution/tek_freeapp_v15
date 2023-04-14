from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    truck_no = fields.Many2one('truck.no',string="Truck No")
    empty_truck_weight = fields.Float(string="Empty Truck Weight")
    loaded_truck_weight = fields.Float(string="Loaded Truck Weight")
    final_weight = fields.Float(string='Final Weight' )

    @api.onchange('empty_truck_weight','loaded_truck_weight')
    def _onchange_city(self):
        if self.loaded_truck_weight and self.empty_truck_weight:
            self.final_weight = self.loaded_truck_weight - self.empty_truck_weight

