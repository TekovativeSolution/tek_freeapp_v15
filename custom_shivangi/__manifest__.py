# -*- coding: utf-8 -*-
{
    'name' : 'Custom Shivangi',
    'version' : '13.0.0.1',
    'summary': 'Custom Shivangi',
    'description': """Added custom fields""",
    'author' : "Sona Solani, Mansi Vaghela",
    'category': 'sales',
    'website': 'www.teknovatesolution.com',
    'depends' : ['base','contacts','sale','stock'],
    'data': [
                'security/ir.model.access.csv',
                'data/ir_sequence.xml',
                'views/res_partner_view.xml',
                'views/stage.xml',
                'views/project_type.xml',
                'views/city.xml',
                'views/district.xml',
                'views/sale_order.xml',
                'views/order_booking.xml',
                'views/account_move.xml',
                'views/stock_picking.xml',
                'views/product_template.xml',
            ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
