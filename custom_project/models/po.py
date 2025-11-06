

from odoo import models, fields, api


class purchaseProjectOrder(models.Model):
    _name = 'project.purchase.order'
    _description = "Project Purchase Order"

    name = fields.Char(string="Name")
