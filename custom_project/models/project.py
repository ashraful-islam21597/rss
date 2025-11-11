from odoo import models, fields, api


class custom_project(models.Model):
    _inherit = 'project.task'
    _description = "Task"

    po = fields.Many2one('project.purchase.order', string="PO")
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    dump_file = fields.Binary(string="Dump File", attachment=True)
    # dump_filename = fields.Char(string="Dump File Name", attachment=True)
    garments_file = fields.Binary(string="Garments Photo", attachment=True)
    # garments_filename = fields.Char(string="Garments File Name")
    country_id = fields.Many2one('res.country', string="Country")
    brand_id = fields.Many2one('buyer.brand', string="Brand")
    order_qty = fields.Float(string="Order Qty")
    tentative_delivery_date = fields.Date(string="Tentative Delivery Date")
    buyer_id = fields.Many2one('party.buyer',string="Buyer Name")
    layout_file = fields.Binary(string="Layout", attachment=True)
    # layout_filename = fields.Char(string="Layout File Name", attachment=True)
    approval_status = fields.Selection([('draft','Draft'),('approved','Approved'),('rejected','Rejected')])
    approved_by = fields.Many2one('res.users',string="Approved By")
    approved_date = fields.Date(string="Approved Date")
    note = fields.Text(string='Note')
    style = fields.Char(string="Style")
    color = fields.Char(string="Color")
    color_code_text = fields.Char(string="Color Code", related="color", readonly=True)
    ref_no = fields.Char(string="Reference No")
    task_id = fields.Char(string="Task ID")

    # dump_attachment_ids = fields.Many2many(
    #     'ir.attachment',
    #     string='Add Attachments',
    #     column2='attachment_id'
    # )

    dump_attachment_ids = fields.Many2many('ir.attachment', 'attachment_project_task_rel', 'task_id', 'attach_id',
                                      string='Add Dump Attachments')

    garments_attachment_ids = fields.Many2many('ir.attachment', 'attachment_garments_project_task_rel', 'task_id', 'garments_attach_id',
                                           string='Add Garments Attachments')


    @api.model
    def create(self, vals):

        if not vals.get('name') or vals.get('name') == 'New':
            project = self.env['project.project'].browse(vals.get('project_id'))
            # seq = self.env['ir.sequence'].next_by_code('project.task.custom')
            # vals['display_name'] = f"{seq}/{self.project.name}"

            email_server = self.env['ir.mail_server'].sudo().search([('name', '=', 'DEFAULT')])
            email_to = 'ashraful.xsellencebdltd@gmail.com'

            if email_server and email_to:
                subject = f'New Task Created: {vals['display_name']}'
                body_html = f'''New task has been created for you.
                        
                        Task Name: {vals['display_name']}
                        Project: {project.name}
                
                        
                        Created By: Md. Ashraful Islam '''
                email_values = {
                    'subject': subject,
                    'body_html': body_html,
                    'email_to': email_to,
                    'auto_delete': False,
                    'email_from': email_server.smtp_user,
                }

                mail_id = self.env['mail.mail'].sudo().create(email_values)
                mail_id.sudo().send()
                print('Email sent')
        return super().create(vals)


class Brand(models.Model):
    _name = 'party.buyer'
    _description = "Buyer"

    name = fields.Char(string="Name")
    user_ids = fields.Many2many('res.users',string="Users")
    partner_ids = fields.Many2many('res.partner',string="Contact Person")

class Brand(models.Model):
    _name = 'buyer.brand'
    _description = "Brand"

    name = fields.Char(string="Name")

