from odoo import fields,models,api
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = 'price desc'
   
    price = fields.Float()
    status = fields.Selection(
        copy=False,
        selection = [("refused", "Refused"),("accepted", "Accepted")])
    partner_id = fields.Many2one('res.partner', required=True, string="Partner")
    property_id = fields.Many2one('estate.property', required=True)
   
        
    validity = fields.Integer(string="Validity(days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute='_compute_date_deadline', inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one(
        "estate.property.type", related="property_id.property_type_id", string="Property Type", store=True
    )
    
   

    @api.depends('validity')
    def _compute_date_deadline(self):
        for rec in self:
            
            if rec.create_date:
                create_date = rec.create_date.date()
            else:
                create_date = date.today()
            
            rec.date_deadline = create_date + timedelta(days=rec.validity)
    
    def _inverse_date_deadline(self):

        for rec in self:

            if rec.create_date:
                create_date = rec.create_date.date()
            else:
                create_date = date.today()
            
            rec.validity = (rec.date_deadline - create_date).days

    def action_accept(self):
        self.write({'status': 'accepted'})
        self.mapped('property_id').write(
            {
                'selling_price': self.price,
                'buyer_id': self.partner_id,
            }
        )
    
        if self.property_id:
            self.property_id.write({'state': 'offer_accepted'})
    
    def action_refuse(self):
        self.write({'status':'refused'})
        if self.property_id:
            self.property_id.write({'state': 'offer_received'})
    
    
    @api.constrains('price')
    def _check_offer_price(self):
        for rec in self:
            if rec.price <= 0:
                raise ValidationError("Offer price must be positive")
            
    
    

    @api.model
    def create(self, vals):
        
        property_obj = self.env['estate.property'].browse(vals.get('property_id'))
        
        print(vals)
        max_offer = max(property_obj.offer_ids.mapped("price"), default=0)
        print(max_offer)
        
        if vals['price'] <= max_offer:
            
            raise UserError("You cannot create an offer with a lower amount than an existing offer.")


        
        property_obj.write({'state': 'offer_received'})
        
        return super(EstatePropertyOffer, self).create(vals)
        