from odoo import fields,models,api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "sequence, name"


    name = fields.Char(string="Property Types", required=True)
    property_type_id = fields.Many2one("estate.property.type")
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    property_ids = fields.One2many("estate.property", "property_type_id")
    
    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer", store=False)
    offer_ids = fields.One2many("estate.property.offer", "property_type_id", string="Offers")

    
    def _compute_offer(self):
        for property_type in self:
            print("================")
            property_type.offer_count = len(property_type.offer_ids)
            print(len(property_type.offer_ids))


    
    def action_view_offers(self):
        res = self.env.ref("estate.estate_property_offer_action").read()[0]
        res["domain"] = [("id", "in", self.offer_ids.ids)]
        return res