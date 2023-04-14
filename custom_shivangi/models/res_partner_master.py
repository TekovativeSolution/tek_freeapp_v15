from odoo import api, fields, models, _


class Stage(models.Model):
    _name = 'stage.name'

    name = fields.Char(string="Stage Name")


class ProjectType(models.Model):
    _name = 'project.type'

    name = fields.Char(string="Project Type")


class District(models.Model):
    _name = 'district.name'

    name = fields.Char(string="District")
    state_id = fields.Many2one("res.country.state", string="State")


class City(models.Model):
    _name = 'city.name'

    name = fields.Char(string="City")
    district_id = fields.Many2one("district.name", string="District")
    freight_discount = fields.Float(string="Freight Discount")

class TruckNo(models.Model):
    _name = 'truck.no'
    _description = 'Truck No'
    _rec_name = 'name'

    name = fields.Char(string="Truck No",required="1")
