from odoo import http
from odoo.http import request

class MyPortal(http.Controller):

    @http.route(['/my/base'], type='http', auth='public', website=True)
    def portal_base_page(self, **kw):
        values = {
            'page_title': 'Welcome to My Custom Portal Page',
            'user': request.env.user,
        }
        return request.render('custom_portal_rss.portal_base_page', values)


