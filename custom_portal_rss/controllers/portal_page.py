import base64

from odoo import http
from odoo.http import request


class CustomPortal(http.Controller):


    @http.route(['/rss/task/list', '/rss/task/list/<int:task_id>'], type='http', auth='user', website=True)
    def custom_portal_base(self, task_id=None, **kw):
        TaskModel = request.env['project.task'].sudo()
        countries = request.env['res.country'].sudo().search([])
        brands = request.env['buyer.brand'].sudo().search([])
        state_selection = TaskModel._fields['state'].selection


        page_vals = {
            'countries': countries,
            'brand': brands,
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
                'state_selection':state_selection
            })
            return request.render('custom_portal_rss.portal_form_view_page', page_vals)

        all_tasks = TaskModel.search([])
        stages = request.env['project.task.type'].sudo().search([])
        page_vals.update({
            'task_list': all_tasks,
            'stages': stages,
            'pending_tasks': all_tasks.search([('stage_id.name', 'not in', ['Done','Delivered'])]),
            'pending_tasks_count': len(all_tasks.search([('stage_id.name', 'not in', ['Done','Delivered'])])),
            'done_tasks': all_tasks.search([('stage_id.name', 'in', ['Done','Delivered'])]),
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

        if uploaded_garments_file:
            task.garments_file = base64.b64encode(uploaded_garments_file.read())
            task.garments_filename = uploaded_garments_file.filename

        if order_qty:
            task.order_qty = order_qty


        if uploaded_dump_file:
            task.dump_file = base64.b64encode(uploaded_dump_file.read())
            task.dump_filename = uploaded_dump_file.filename

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
    def save_task_layout_team(self, **post):
        task_id = post.get('task_id')
        if not task_id:
            return request.redirect('/rss/task/list')

        task = request.env['project.task'].sudo().browse(int(task_id))
        uploaded_layout_file_file = request.httprequest.files.get('layout_file')
        if uploaded_layout_file_file:
            task.layout_file = base64.b64encode(uploaded_layout_file_file.read())
            task.layout_filename = uploaded_layout_file_file.filename

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

        email_server = request.env['ir.mail_server'].sudo().search([('name', '=', 'DEFAULT')])
        email_to = task.vendor_id.email
        self.email_from_lauout_design_team(task,email_server,email_to)

        return request.render('custom_portal_rss.portal_form_view_page', {
            'task_view': task,
            'countries': countries,
            'brand': brands,
            'toast_message': 'File Uploaded successfully!',
            'toast':True,
        })

    @http.route('/rss/buyer/task/save', csrf=False, type='http', auth='user', website=True, methods=['POST'])
    def save_task_buyer(self, **post):
        task_id = post.get('task_id')
        if not task_id:
            return request.redirect('/rss/task/list')

        task = request.env['project.task'].sudo().browse(int(task_id))
        state = post.get('state')
        note = post.get('note')
        approved_by = post.get('approved_by')
        approved_date = post.get('approved_date')
        # state = fields.Selection([
        #     ('01_in_progress', 'In Progress'),
        #     ('02_changes_requested', 'Changes Requested'),
        #     ('03_approved', 'Approved'),
        #     *CLOSED_STATES.items(),
        #     ('04_waiting_normal', 'Waiting'),
        # ], string='State', copy=False, default='01_in_progress', required=True, compute='_compute_state',
        #     inverse='_inverse_state', readonly=False, store=True, index=True, recursive=True, tracking=True)


        if state:
             task.state = '03_approved'
        if approved_by:
            task.approved_by = request.env.user.id
        if approved_date:
            task.approved_date = approved_date

        if note:
            task.note = note


        countries = request.env['res.country'].sudo().search([])
        brands = request.env['buyer.brand'].sudo().search([])
        state_selection = request.env['project.task']._fields['state'].selection
        # stages = request.env['project.task.type'].sudo().search([])
        # stage_id = request.env['project.task.type'].sudo().search([
        #     ('name', 'ilike', 'Approved')
        # ], limit=1)
        #
        # if stage_id:
        #     task.sudo().write({'stage_id': stage_id.id})

        if state == '03_approved':
            stage = request.env['project.task.type'].sudo().search([
                ('name', 'ilike', 'Done'),
                ('project_ids', 'in', task.project_id.id)
            ], limit=1)

            if stage:
                task.sudo().write({'stage_id': stage.id})
            task.state = '03_approved'
        # if state == '03_approved':
        #     stage = request.env['project.task.type'].sudo().search([
        #         ('name', 'ilike', 'Approved'),
        #         ('project_ids', 'in', task.project_id.id)
        #     ], limit=1)
        #
        #     if stage:
        #         task.sudo().write({'stage_id': stage.id})
        #     task.state = '03_approved'



        return request.render('custom_portal_rss.portal_form_view_page', {
            'task_view': task,
            'countries': countries,
            'brand': brands,
            'state_selection': state_selection,
            'toast_message': 'Buyer Data Uploaded successfully!',
            'toast':True,
        })


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
    #         # subject = 'Layout Design Updated'
    #         # body_html = 'hello sir, Your expected layout design has been updated please check now'
    #         # email_values = {
    #         #     'subject': subject,
    #         #     'body_html': body_html,
    #         #     'email_to': email_to,
    #         #     'auto_delete': False,
    #         #     'email_from': email_server.smtp_user,
    #         # }
    #         #
    #         # mail_id = request.env['mail.mail'].sudo().create(email_values)
    #         # mail_id.sudo().send()
    #
    #         template = request.env.ref('custom_portal_rss.email_template_task_created')
    #         mail = template.send_mail(task.id, force_send=True)
    #         return mail
    #
    #
    def email_from_lauout_design_team(self,task,email_server,email_to):
        if not task or not task.vendor_id.email:
            return False

        # Ensure mail server exists
        # email_server = request.env['ir.mail_server'].sudo().search([], limit=1)
        if not email_server:

            return False

        try:
            template = request.env.ref('custom_portal_rss.email_template_task_created').sudo()
            # Optional: update context if needed
            template.with_context(
                email_to=email_to,
                default_email_from=email_server.smtp_user,
            ).send_mail(task.id, force_send=True)
            return True
        except Exception as e:
            return False

