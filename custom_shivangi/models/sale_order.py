from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, get_lang
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    booking_price = fields.Float(string="Booking Price")
    city_id = fields.Many2one('city', string="City")
    cash_discount = fields.Selection([
        ('500', '500'),
        ('300', '300')
    ], string='Cash Discount', copy=False)
    vehicle = fields.Selection([
        ('party_vehicle', 'Party vehicle'),
        ('plant_vehicle', 'Plant Vehicle')
    ], string='Vehicle', copy=False)
    booking_id = fields.Many2one('order.booking', string="Order Booking")
    consignee_billing_discount = fields.Selection([
        ('50', '50'),
    ], string='Consignee Billing Discount', copy=False)
    invoice_discount = fields.Selection([
        ('1000', '1000'),
    ], string='Invoice Discount', copy=False)
    custom_charges = fields.Float(string="Custom Charges")
    freight_discount = fields.Float(string="Freight Discount")
    freight_difference = fields.Float(string="Freight Difference")
    for_price = fields.Selection([
        ('200', '200'),
    ], string='F.O.R', copy=False)
    truck_no = fields.Many2one('truck.no',string="Truck No")
    empty_truck_weight = fields.Float(string="Empty Truck Weight")
    loaded_truck_weight = fields.Float(string="Loaded Truck Weight")
    final_weight = fields.Float(string='Final Weight')

    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        if self.booking_id.pending_quantity < 0:
            raise UserError(_("You can not create more than pending quantity sale order.") )
        return res


    def calculate(self):
        final_price,invoice_discount,cash_discount,consignee_billing_discount,custom_charges,for_price,freight_discount = 0.0,0.0,0.0,0.0,0.0,0.0,0.0
        if self.booking_price:
            if self.invoice_discount:
                invoice_discount +=  1000
            if self.cash_discount:
                cash_discount +=  500 if self.cash_discount == '500' else   300
            if self.consignee_billing_discount:
                consignee_billing_discount += 50
            if self.custom_charges:
                custom_charges +=  self.custom_charges
            if self.for_price:
                for_price +=  200
            if self.freight_discount:
                freight_discount +=  self.freight_discount
            final_price = self.booking_price - invoice_discount - cash_discount - consignee_billing_discount - custom_charges + for_price - freight_discount
            for order_line in self.order_line:
                order_line.write({
                    'final_rate':final_price,
                    'price_unit':final_price+order_line.extra_charges})



    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        vals = {'truck_no': self.truck_no.id,
                'empty_truck_weight': self.empty_truck_weight,
                'loaded_truck_weight': self.loaded_truck_weight,
                'final_weight': self.final_weight,
                'booking_price': self.booking_price,
                'consignee_billing_discount': self.consignee_billing_discount,
                'invoice_discount': self.invoice_discount,
                'custom_charges': self.custom_charges,
                'freight_discount': self.freight_discount,
                'for_price': self.for_price,
                'cash_discount': self.cash_discount,
                }
        res.update(vals)
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bundle = fields.Float(string="Bundle")
    avg_wt_bundle = fields.Float(string="Avg WT/Bundle (kg)")
    extra_charges = fields.Float(string="Extra Charges")
    final_rate = fields.Float(string="Final Rate")

    def _prepare_invoice_line(self):
        """
        override this method for add extra fields values
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
            'bundle': self.bundle,
            'avg_wt_bundle': self.avg_wt_bundle,
            'extra_charges': self.extra_charges,
            'final_rate': self.final_rate
        }
        if self.display_type:
            res['account_id'] = False
        return res

    @api.onchange('product_id')
    def product_id_change(self):
        """override this method for add extra charges in line."""

        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        ####
        if self.product_id.extra_price:
            vals['extra_charges'] = self.product_id.extra_price
        ####
        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        vals.update(name=self.get_sale_order_line_multiline_description_sale(product))

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result