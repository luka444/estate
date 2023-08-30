from odoo import fields,models,api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate property'
    _order = 'id desc'
    
    name = fields.Char(string='title',trim=True, translate=True, required=True)
    
    bedrooms = fields.Integer()
    
    description = fields.Text()
    
    expected_price = fields.Float(string='price', digits=(12, 2), copy=False)
    
    living_area = fields.Integer()
    
    image = fields.Binary(string='image', attachment=True)
    
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east','East'), ('west','West')],
        help="Type is used to separate Leads and Opportunities",
        default= False)
    test = fields.Html()
    photo = fields.Image(string='photo', max_width=64, max_height=64)
    postcode = fields.Char(copy=False)
    date_availability = fields.Date(string="Available from", default=lambda self: fields.Date.today() + relativedelta(months=+3), copy=False)
    selling_price = fields.Float()
    date_start = fields.Datetime(string='Start time', required=True,default=lambda s: fields.Date.today(s))
    date_end = fields.Datetime(string='End time', required=True, default=lambda s: fields.Date.today())
    active = fields.Boolean(default=True)
    garden_area = fields.Integer(string="Garden Area")
    total_area = fields.Integer(string="Total Area", compute="_compute_total_area", store=True)
    property_type_id = fields.Many2one("estate.property.type")
    seller_id = fields.Many2one("res.users", string='Salesperson', default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string='Buyer', copy=False)
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    garden = fields.Boolean(onchange='_onchange_garden', default=False)
    best_offer = fields.Float(compute='_compute_best_offer', readonly=True, store=True)
    canceled = fields.Boolean(string="canceled",default=False)
    sold = fields.Boolean(string="sold", default=False)
    state = fields.Selection(selection=[('new','New'),('cancel','Cancelled'),('offer_received','Offer received'),('offer_accepted','Offer accepted'),('sold','Sold')], string="Status", default='new')
    
    forbid_write = fields.Boolean(string="Forbid Write")
    
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area
    
    @api.onchange("garden")
    def _onchange_garden(self):
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = False
        else:   
            self.garden_area = 10
            self.garden_orientation = 'north'

    
    @api.constrains("garden_area")
    def _constrains_garden_area(self):
        
        if not self.garden:
            if self.garden_area != 0:
                raise ValidationError("When the garden marker is unchecked, you cannot enter the area of the garden!")
        elif self.garden:
            if self.garden_area <= 0:
                raise ValidationError("When the garden marker is checked, you must enter some numbers in garden area!")
                
    @api.constrains("bedrooms")
    def _constrains_bedrooms(self):
        if self.bedrooms <= 0:
            raise ValidationError("There should be at least 1 bedroom or more!")
    
   
    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
            
            for rec in self:
                rec.best_offer = max(rec.offer_ids.mapped('price'), default=0)
    
    def action_sold(self):
        if "cancel" in self.mapped("state"):
            raise UserError("Canceled properties cannot be sold.")
        return self.write({"state": "sold"})
    
    def action_cancel(self):
        for rec in self:
            if rec.state == 'sold':
                raise UserError("Cannot cancel a property that is already sold.")
        return self.write({"state": "cancel"})
         


    @api.constrains('expected_price')
    def check_expected_price_positive(self):
        rec_with_non_positive_price = self.filtered(lambda r: r.expected_price <= 0)
        if rec_with_non_positive_price:
            raise ValidationError("Expected price must be positive")
        
    @api.constrains('expected_price','selling_price')
    def check_selling_price(self):
        for rec in self.filtered(lambda r: not float_is_zero(r.selling_price, precision_digits=2)and not float_is_zero(r.expected_price, precision_digits=2)):
            price_ratio = rec.selling_price / rec.expected_price
            if price_ratio < 0.9:
                raise ValidationError("Selling price cannot be lower that 90 percent of the expected") 


    @api.ondelete(at_uninstall=False)
    def _delete__new_canceled(self):
        properties_to_delete = self.filtered(lambda p: p.state not in ['new', 'cancel'])
        if properties_to_delete:
            raise UserError("You cannot delete properties that are not in 'New' or 'Canceled' state.")


    def write(self, vals):
        res = super(EstateProperty,self).write(vals) 
        if not self.forbid_write:
            return res
        if any(field in vals and field != 'forbid_write' for field in vals):
            raise UserError("Editing is prohibited when the forbid_write box is checked")
        
