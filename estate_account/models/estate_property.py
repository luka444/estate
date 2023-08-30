from odoo import models, fields, api

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        
        res = super(EstateProperty, self).action_sold()

        
        account_move = self.env['account.move'].create({
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids':[
            (0, 0, {
                'name': self.name,
                'quantity': 1,
                'price_unit': self.selling_price * 0.06,
            }),
            (0, 0, {
                'name': 'Administrative Fees',
                'quantity': 1,
                'price_unit': 100.00,
            }),
        ]
            
             
        })

        
        return res