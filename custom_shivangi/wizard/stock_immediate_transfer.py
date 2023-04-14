from odoo import api, fields, models, _

class StockImmediateTransfer(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    def process(self):
        res = super(StockImmediateTransfer,self).process()
        for picking_id in self.pick_ids:
            if picking_id.picking_type_id.code == 'outgoing' and picking_id.origin:
                sale_order = self.env['sale.order'].search([('name','=',picking_id.origin)])
                sale_order.write({'truck_no':picking_id.truck_no.id,
                                  'empty_truck_weight':picking_id.empty_truck_weight,
                                  'loaded_truck_weight':picking_id.loaded_truck_weight,
                                  'final_weight':picking_id.final_weight
                                  })

        return res


