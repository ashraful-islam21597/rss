from datetime import date

from odoo import http
from odoo.http import request


class CustomProject(http.Controller):
    def _get_basic_page_values(self):
        vals = {}
        vals['description'] = 'RSS Portal'

        vals['default_user_types'] = ['Admin', 'Vendor', 'Buyer']

        # User details
        vals['user'] = request.env.user
        vals['user_id'] = request.env.user.id
        vals['user_name'] = request.env.user.name
        vals['user_type'] = "warehouse"

        # security_role_agent_portal
        # security_role_warehouse_portal

        # Notification Details
        # notifications = request.env['notification'].sudo().search(
        #     [('user_id', '=', vals['user_id']), ('active', '=', True), ('state', '=', 'unread')], order='id desc')
        # vals['notifi_count'] = len(notifications)
        # vals['notifi_list'] = request.env['notification'].sudo().get_notifications_data(notifications=notifications[:4])

        return vals

    @http.route(['/rss/project/tasks/list', '/rss/project/tasks/list/<int:task_id>'], type='http', auth='user',
                website=True, sitemap=False)
    def project_tasks_list(self, task_id=None, **kw):
        page_vals = self._get_basic_page_values()
        page_vals['page_title'] = "Tasks List"
        page_vals['description'] = "Tasks Requests"
        page_vals['page_name'] = "task_request_list"
        # if task_id:
        #     booking_request = request.env['direct.booking.request'].sudo().browse(booking_id)
        #     page_vals['page_title'] = booking_request.name
        #     page_vals['booking_request'] = booking_request
        #     return request.render('custom_freightmanagement_portal.booking_request_portal_template', page_vals)
        # else:
        # year = kw.get('year', date.today().year)
        # start_date = "%s-01-01" % str(year)
        # end_date = "%s-12-31" % str(year)
        # start_year = request.env['sequence.key'].sudo().search([('key', '=', 'company_start_year')]).value
        domain = [
            ('customer_id', '=', request.env.user.partner_id.id),
                  # ('booking_date', '>=', start_date),
                  # ('booking_date', '<=', end_date)
                  ]

        domain=[]

        # page_vals['current_year'] = date.today().year
        # page_vals['active_year'] = int(year)
        # page_vals['year_list'] = sorted(
        #     [year for year in range(int(start_year or page_vals['current_year']), page_vals['current_year'] + 1)],
        #     reverse=True)

        page_vals['tasks_list'] = request.env['project.task'].sudo().search(domain)
        return request.render('custom_project.rss_task_list', page_vals)


