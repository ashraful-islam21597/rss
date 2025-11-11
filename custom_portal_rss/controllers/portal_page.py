import base64
from datetime import date, datetime, timedelta

from odoo import http
from odoo.http import request
import json


class CustomPortal(http.Controller):

    # @http.route(['/rss','/rss/<int:project_id>', '/rss/<int:project_id>/<int:task_id>'], type='http', auth='user',
    #             website=True)
    # def custom_portal_base(self, project_id=None, task_id=None, **kw):
    #     if project_id:
    #         TaskModel = request.env['project.task'].sudo().search([('project_id', '=', project_id)])
    #         all_tasks = TaskModel
    #     else:
    #         projects = request.env['project.project'].sudo()
    #         all_projects = projects.search([])
    #         page_vals = {
    #             'all_projects': all_projects,
    #
    #         }
    #         return request.render('custom_portal_rss.portal_project_form_view_page',page_vals)
    #
    #     countries = request.env['res.country'].sudo().search([])
    #     brands = request.env['buyer.brand'].sudo().search([])
    #     po_list = request.env['project.purchase.order'].sudo().search([])
    #     buyer = request.env['party.buyer'].sudo().search([])
    #     state_selection = TaskModel._fields['state'].selection
    #
    #     page_vals = {
    #         'countries': countries,
    #         'brand': brands,
    #         'po_list': po_list,
    #         'state_selection': state_selection,
    #     }
    #
    #     if task_id:
    #         task_view = TaskModel.browse(task_id)
    #         stages = request.env['project.task.type'].sudo().search([
    #             ('project_ids', 'in', task_view.project_id.id)
    #         ])
    #         state_selection = TaskModel._fields['state'].selection
    #         page_vals.update({
    #             'page_title': task_view.name,
    #             'task_view': task_view,
    #             'stages': stages,
    #             'project_id': task_view.project_id.id,
    #             'countries': countries,
    #             'brand': brands,
    #             'buyer': buyer,
    #             'po_list': po_list,
    #             'state_selection': state_selection
    #         })
    #         return request.render('custom_portal_rss.portal_form_view_page', page_vals)
    #
    #     # all_tasks = TaskModel.search([])
    #     stages = request.env['project.task.type'].sudo().search([])
    #     page_vals.update({
    #         'task_list': all_tasks,
    #         'stages': stages,
    #         'brands': brands,
    #         'buyer': buyer,
    #         'project_id': project_id,
    #         'pending_tasks': all_tasks.search([('stage_id.name', 'not in', ['Done', 'Delivered'])]),
    #         'pending_tasks_count': len(all_tasks.search([('stage_id.name', 'not in', ['Done', 'Delivered'])])),
    #         'done_tasks': all_tasks.search([('stage_id.name', 'in', ['Done', 'Delivered'])]),
    #         'done_tasks_count': len(all_tasks.search([('stage_id.name', 'in', ['Done', 'Delivered'])])),
    #     })
    #
    #     return request.render('custom_portal_rss.portal_base_page', page_vals)



    @http.route('/rss/task/create/<int:project_id>', type='http', methods=['POST'], auth='public', csrf=False, website=True)
    def create_task(self, project_id=None, **kwargs):
        project = request.env['project.project'].sudo().browse(project_id)
        if not project.exists():
            return request.not_found()

        seq = request.env['ir.sequence'].next_by_code('project.task.custom')
        task_identifier = f"RSS / {date.today().year} / {seq}"

        delivery_deadline = kwargs.get('delivery_deadline')

        date_deadline = False
        if delivery_deadline:
            try:
                if ' ' in delivery_deadline:
                    date_obj = datetime.strptime(delivery_deadline, '%Y-%m-%d %H:%M:%S')
                else:
                    date_obj = datetime.strptime(delivery_deadline, '%Y-%m-%d')
                date_obj = date_obj + timedelta(hours=6)

                date_deadline = date_obj.strftime('%Y-%m-%d %H:%M:%S')

            except ValueError as e:
                print(f"Date conversion error: {e}")
                try:
                    date_obj = datetime.strptime(delivery_deadline, '%d-%m-%Y')
                    date_deadline = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    print("All date format conversions failed")
        po = request.env['project.purchase.order'].sudo().create({'name':kwargs.get('po_number')})
        brand = request.env['buyer.brand'].sudo().create({'name':kwargs.get('brand_id')})
        task_vals = {
            'project_id': project.id,
            'name': kwargs.get('short_desc', task_identifier),
            'po': po.id,
            'country_id': kwargs.get('country_id'),
            'buyer_id': kwargs.get('buyer_id'),
            'brand_id': brand.id,
            'order_qty': kwargs.get('order_qty'),
            'date_deadline': date_deadline,
            'style': kwargs.get('style'),
            'color': kwargs.get('color'),
            'task_id': task_identifier,
            'note': kwargs.get('description'),
            'vendor_id' : request.env.user.partner_id.id,
        }
        task = request.env['project.task'].sudo().create(task_vals)

        uploaded_dump_files = request.httprequest.files.getlist('uploaded_file_data[]')
        attachment_ids = []


        for file in uploaded_dump_files:
            content = file.read()
            if not content:
                continue
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(content),  # bytes only
                'type': 'binary',
                'res_model': 'project.task',
                'res_id': task.id,
                'mimetype': file.content_type or 'application/octet-stream',
            })
            attachment_ids.append(attachment.id)

        if attachment_ids:
            task.sudo().write({
                'dump_attachment_ids': [(6, 0, attachment_ids)]  # works if Many2many
            })

        # uploaded_garments_files = request.httprequest.files.getlist('uploaded_garments_file_data[]')
        # garments_attachment_ids = []
        # file_contents = []
        # for file in uploaded_garments_files:
        #     content = file.read()
        #     file_contents.append((file.filename, content))
        # for file in uploaded_garments_files:
        #     content = file.read()
        #     attachment = request.env['ir.attachment'].sudo().create({
        #         'name': file.filename,
        #         'datas': base64.b64encode(content).decode('utf-8'),
        #         'type': 'binary',
        #         'res_model': 'project.task',
        #         'res_id': task.id,
        #     })
        #     garments_attachment_ids.append(attachment.id)
        # if garments_attachment_ids:
        #     task.sudo().write({
        #         'garments_attachment_ids': [(4, att_id) for att_id in attachment_ids]
        #     })

        uploaded_garments_files = request.httprequest.files.getlist('uploaded_garments_file_data[]')
        garments_attachment_ids = []

        for file in uploaded_garments_files:
            content = file.read()
            if not content:
                continue
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(content),
                'type': 'binary',
                'res_model': 'project.task',
                'res_id': task.id,
                'mimetype': file.content_type or 'application/octet-stream',
            })
            garments_attachment_ids.append(attachment.id)

        if garments_attachment_ids:
            task.sudo().write({
                'garments_attachment_ids': [(6, 0, garments_attachment_ids)]  # many2many
            })

        return request.make_response("Task created successfully.")

    @http.route(['/rss/<int:project_id>', '/rss/<int:project_id>/<int:task_id>'], type='http', auth='user', website=True)
    def custom_portal_base(self,project_id=None, task_id=None, **kw):
        if project_id:
            TaskModel = request.env['project.task'].sudo().search(
                [('project_id', '=', project_id)],
                order='create_date desc'
            )

            all_tasks = TaskModel
        else:
            TaskModel = request.env['project.task'].sudo()
            all_tasks =  TaskModel.search([])


        countries = request.env['res.country'].sudo().search([])
        brands = request.env['buyer.brand'].sudo().search([])
        po_list = request.env['project.purchase.order'].sudo().search([])
        buyer = request.env['party.buyer'].sudo().search([])
        state_selection = TaskModel._fields['state'].selection


        page_vals = {
            'countries': countries,
            'brand': brands,
            'po_list':po_list,
            'state_selection': state_selection,
        }

        if task_id:
            task_view = TaskModel.browse(task_id)
            stages = request.env['project.task.type'].sudo().search([
                ('project_ids', 'in', task_view.project_id.id)
            ])
            state_selection = TaskModel._fields['state'].selection
            page_vals.update({
                'page_title': task_view.name,
                'task_view': task_view,
                'stages': stages,
                'project_id': task_view.project_id.id,
                'countries': countries,
                'brand': brands,
                'buyer': buyer,
                'po_list': po_list,
                'state_selection':state_selection
            })
            return request.render('custom_portal_rss.portal_form_view_page', page_vals)


        stages = request.env['project.task.type'].sudo().search([])
        page_vals.update({
            'task_list': all_tasks,
            'stages': stages,
            'brands': brands,
            'buyer': buyer,
            'project_id':project_id,
            'pending_tasks': all_tasks.search([('stage_id.name', 'not in', ['Done','Delivered'])],order='create_date desc'),
            'pending_tasks_count': len(all_tasks.search([('stage_id.name', 'not in', ['Done','Delivered'])])),
            'done_tasks': all_tasks.search([('stage_id.name', 'in', ['Done','Delivered'])],order='create_date desc'),
            'done_tasks_count': len(all_tasks.search([('stage_id.name', 'in', ['Done','Delivered'])])),
        })

        return request.render('custom_portal_rss.portal_base_page', page_vals)

    @http.route('/rss/vendor/task/save', csrf=False, type='http', auth='user', website=True, methods=['POST'])
    def save_task_vendor(self, **post):
        task_id = post.get('task_id')
        if not task_id:
            return request.redirect('/rss/task/list')

        task = request.env['project.task'].sudo().browse(int(task_id))

        brand_id = post.get('brand_id')
        order_qty = post.get('order_qty')
        country_id = post.get('country_id')
        style = post.get('style')
        ref = post.get('ref_no')
        color = post.get('color')
        color_code = post.get('color_code_display')
        date_deadline = post.get('date_deadline')
        uploaded_garments_file = request.httprequest.files.get('garments_file')
        uploaded_dump_file = request.httprequest.files.get('dump_file')
        if country_id:
            task.country_id = int(country_id)
        if brand_id:
            task.brand_id = int(brand_id)
        if date_deadline:
            task.date_deadline = date_deadline

        # if uploaded_garments_file:
        #     task.garments_file = base64.b64encode(uploaded_garments_file.read())
        #     task.garments_filename = uploaded_garments_file.filename

        if order_qty:
            task.order_qty = order_qty


        # if uploaded_dump_file:
        #     task.dump_file = base64.b64encode(uploaded_dump_file.read())
        #     task.dump_filename = uploaded_dump_file.filename

        if style:
            task.style = style

        if ref:
            task.color = color

        if color:
            task.ref_no = ref




        countries = request.env['res.country'].sudo().search([])
        brands = request.env['buyer.brand'].sudo().search([])
        buyer_party = request.env['party.buyer'].sudo().search([('id','=',task.buyer_id.id)])
        state_selection = request.env['project.task']._fields['state'].selection
        #stages = request.env['project.task.type'].sudo().search([])
        # task.stage_id = stages.search([('name', 'ilike', 'In Progress')], limit=1).id

        email_server = request.env['ir.mail_server'].sudo().search([('name', '=', 'DEFAULT')])
        # for user in buyer_party.user_ids:
        #     email_to = user.email
        #     self.email_from_vendor(email_server,email_to)

        #task.stage_id = stages.search([('name','ilike','In Progress')],limit=1).id

        stage = request.env['project.task.type'].sudo().search([
            ('name', 'ilike', 'In Progress'),
            ('project_ids', 'in', task.project_id.id)
        ], limit=1)

        if stage:
            task.sudo().write({'stage_id': stage.id})
        task.state = '01_in_progress'

        email_server = request.env['ir.mail_server'].sudo().search([('name', '=', 'DEFAULT')])
        # for user in buyer_party.user_ids:
        #     email_to = user.email
        #     self.email_from_vendor(email_server,email_to)

        return request.render('custom_portal_rss.portal_form_view_page', {
            'task_view': task,
            'countries': countries,
            'brand': brands,
            'state_selection': state_selection,
            'toast_message': 'Vendor data Saved successfully!',
            'toast':True,


        })

    @http.route('/rss/design/task/save', csrf=False, type='http', auth='user', website=True, methods=['POST'])
    def save_task_layout_team(self, **kwargs):
        task_id = kwargs.get('task_id')
        if not task_id:
            return request.redirect('/rss/task/list')

        task = request.env['project.task'].sudo().browse(int(task_id))
        #uploaded_layout_file_file = request.httprequest.files.get('layout_file')
        # if uploaded_layout_file_file:
        #     task.layout_file = base64.b64encode(uploaded_layout_file_file.read())
        #     task.layout_filename = uploaded_layout_file_file.filename

        uploaded_layout_files = request.httprequest.files.getlist('layout_file[]')
        attachment_ids = []

        for file in uploaded_layout_files:
            content = file.read()
            if not content:
                continue
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(content),
                'type': 'binary',
                'res_model': 'project.task',
                'res_id': task.id,
                'mimetype': file.content_type or 'application/octet-stream',
            })
            attachment_ids.append(attachment.id)

        if attachment_ids:
            task.sudo().write({
                'layout_attachment_ids': [(6, 0, attachment_ids)]  # works if Many2many
            })

        countries = request.env['res.country'].sudo().search([])
        brands = request.env['buyer.brand'].sudo().search([])
        state_selection = request.env['project.task']._fields['state'].selection

        # stage = request.env['project.task.type'].sudo().search([
        #     ('name', 'ilike', 'In Progress'),
        #     ('project_ids', 'in', task.project_id.id)
        # ], limit=1)
        #
        # if stage:
        #     task.sudo().write({'stage_id': stage.id})
        # task.state = '01_in_progress'



        stage = request.env['project.task.type'].sudo().search([
            ('name', 'ilike', 'In Progress'),
            ('project_ids', 'in', task.project_id.id)
        ], limit=1)

        if stage:
            task.sudo().write({'stage_id': stage.id})
        task.state = '01_in_progress'

        email_server = request.env['ir.mail_server'].sudo().search([('name', '=', 'DEFAULT')])
        email_to = task.vendor_id.email
        self.email_from_layout_design_team(task, email_server, email_to)

        return request.render('custom_portal_rss.portal_form_view_page', {
            'task_view': task,
            'countries': countries,
            'brand': brands,
            'toast_message': 'File Uploaded successfully!',
            'toast':True,
        })

    # @http.route('/rss/buyer/task/save', csrf=False, type='http', auth='user', website=True, methods=['POST'])
    # def save_task_buyer(self, **post):
    #     task_id = post.get('task_id')
    #     if not task_id:
    #         return request.redirect('/rss/task/list')
    #
    #     task = request.env['project.task'].sudo().browse(int(task_id))
    #     state = post.get('state')
    #     note = post.get('note')
    #     approved_by = post.get('approved_by')
    #     approved_date = post.get('approved_date')
    #     # state = fields.Selection([
    #     #     ('01_in_progress', 'In Progress'),
    #     #     ('02_changes_requested', 'Changes Requested'),
    #     #     ('03_approved', 'Approved'),
    #     #     *CLOSED_STATES.items(),
    #     #     ('04_waiting_normal', 'Waiting'),
    #     # ], string='State', copy=False, default='01_in_progress', required=True, compute='_compute_state',
    #     #     inverse='_inverse_state', readonly=False, store=True, index=True, recursive=True, tracking=True)
    #
    #
    #     if state:
    #          task.state = '03_approved'
    #     if approved_by:
    #         task.approved_by = request.env.user.id
    #     if approved_date:
    #         task.approved_date = approved_date
    #
    #     if note:
    #         task.note = note
    #
    #
    #     countries = request.env['res.country'].sudo().search([])
    #     brands = request.env['buyer.brand'].sudo().search([])
    #     state_selection = request.env['project.task']._fields['state'].selection
    #     # stages = request.env['project.task.type'].sudo().search([])
    #     # stage_id = request.env['project.task.type'].sudo().search([
    #     #     ('name', 'ilike', 'Approved')
    #     # ], limit=1)
    #     #
    #     # if stage_id:
    #     #     task.sudo().write({'stage_id': stage_id.id})
    #
    #     if state == '03_approved':
    #         stage = request.env['project.task.type'].sudo().search([
    #             ('name', 'ilike', 'Done'),
    #             ('project_ids', 'in', task.project_id.id)
    #         ], limit=1)
    #
    #         if stage:
    #             task.sudo().write({'stage_id': stage.id})
    #         task.state = '03_approved'
    #     # if state == '03_approved':
    #     #     stage = request.env['project.task.type'].sudo().search([
    #     #         ('name', 'ilike', 'Approved'),
    #     #         ('project_ids', 'in', task.project_id.id)
    #     #     ], limit=1)
    #     #
    #     #     if stage:
    #     #         task.sudo().write({'stage_id': stage.id})
    #     #     task.state = '03_approved'
    #
    #
    #
    #     return request.render('custom_portal_rss.portal_form_view_page', {
    #         'task_view': task,
    #         'countries': countries,
    #         'brand': brands,
    #         'state_selection': state_selection,
    #         'toast_message': 'Buyer Data Uploaded successfully!',
    #         'toast':True,
    #     })


    def email_from_vendor(self,email_server,email_to):
        if email_server and email_to:
            subject = 'Task Updated'
            body_html = 'Task updated and files uploaded by vendor'
            email_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': email_to,
                'auto_delete': False,
                'email_from': email_server.smtp_user,
            }

            mail_id = request.env['mail.mail'].sudo().create(email_values)
            mail_id.sudo().send()

            return mail_id

    # def email_from_lauout_design_team(self,task,email_server,email_to):
    #     if email_server and email_to:
    #         subject = f"Updated Layout Design for Your Review – {task.name}"
    #         body_html = f"""
    #                 <div style="font-family: Arial, sans-serif; color: #333; font-size: 14px; line-height: 1.6;">
    #                     <p>Hi Sir/Ma’am,</p>
    #                     <p>We’ve prepared the attached layout as per your specifications.</p>
    #                     <p>
    #                         Could you please take a moment to review it and confirm if it’s okay to proceed?
    #                         If you’d like any changes, just let us know — we’ll revise it right away.
    #                     </p>
    #                     <p>Thanks for your time and support!</p>
    #                     <br>
    #                     <p>Regards, <br>
    #                     <strong>{request.env.user.name}</strong><br>
    #                     Cell: {request.env.user.phone}
    #                     </p>
    #                 </div>
    #                 """
    #         email_values = {
    #             'subject': subject,
    #             'body_html': body_html,
    #             'email_to': email_to,
    #             'auto_delete': False,
    #             'email_from': email_server.smtp_user,
    #         }
    #
    #         mail_id = request.env['mail.mail'].sudo().create(email_values)
    #         mail_id.sudo().send()
    #
    #         # template = request.env.ref('custom_portal_rss.email_template_task_created')
    #         # mail = template.send_mail(task.id, force_send=True)
    #         # return mail

    # def email_from_lauout_design_team(self,task,email_server,email_to):
    #     if not task or not task.vendor_id.email:
    #         return False
    #
    #     # Ensure mail server exists
    #     # email_server = request.env['ir.mail_server'].sudo().search([], limit=1)
    #     if not email_server:
    #
    #         return False
    #
    #     try:
    #         template = request.env.ref('custom_portal_rss.email_template_task_created').sudo()
    #         template.with_context(
    #             email_to=email_to,
    #             default_email_from=email_server.smtp_user,
    #         ).send_mail(task.id, force_send=True)
    #         return True
    #     except Exception as e:
    #         return False

    def email_from_layout_design_team(self, task, email_server, email_to):
        if not (email_server and email_to and task):
            return False

        task_details = {
            'Task Name': task.name,
            'Task ID': task.task_id,
            'PO Number': task.po.name or '-',
            'Buyer': task.buyer_id.name if task.buyer_id else '-',
            'Country': task.country_id.name if task.country_id else '-',
            'Deadline': task.date_deadline.strftime('%Y-%m-%d') if task.date_deadline else '-',
            'Stage': task.stage_id.name if task.stage_id else '-',
        }

        subject = f"Updated Layout Design for Your Review – {task.name or 'Layout Task'}"
        table_rows = ""
        for key, value in task_details.items():
            table_rows += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #333; font-weight: bold;">{key}</td>
                <td style="padding: 8px; border: 1px solid #333;">{value}</td>
            </tr>
            """
        body_html = f"""
                   <div style="font-family: Arial, sans-serif; color: #333; font-size: 14px; line-height: 1.6;">
                       <p>Hi Sir/Ma’am,</p>
                       <p>We’ve prepared the attached layout as per your specifications.</p>
                       <p>
                           Could you please take a moment to review it and confirm if it’s okay to proceed?
                           If you’d like any changes, just let us know — we’ll revise it right away.
                       </p>
                       <p>Thanks for your time and support!</p>
                       <br>
                       <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                            {table_rows}
                        </table>
                       <p>Regards, <br>
                       <strong>{request.env.user.name}</strong><br>
                       Cell: {request.env.user.phone}
                       </p>
                   </div>
                   """

        email_values = {
            'subject': subject,
            'body_html': body_html,
            'email_to': email_to,
            'auto_delete': False,
            'email_from': email_server.smtp_user,
            'attachment_ids': [(6, 0, task.layout_attachment_ids.ids)]
        }

        Mail = request.env['mail.mail'].sudo()
        mail_id = Mail.create(email_values)

        if task.attachment_ids:
            for attachment in task.attachment_ids:
                attachment.copy(default={
                    'res_model': 'mail.mail',
                    'res_id': mail_id.id
                })
        mail_id.sudo().send()

        return True


