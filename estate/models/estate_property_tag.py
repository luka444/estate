from odoo import fields,models,api

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate property tag"
    _order = "name"

    name = fields.Char(string="Tags", required=True)
    color = fields.Integer(string="Tag Color")
