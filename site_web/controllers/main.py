from odoo import http

class SiteWeb(http.Controller):

    @http.route('/site_web', type='http', auth='public', website=True)
    def home(self, **kw):
        return http.request.render('site_web.template_page_home', {})

#cd /home/odoo/src/odoo
#python3 ./odoo-bin -d velo_web -u velo_amis \
#  --addons-path=/home/odoo/src/odoo/addons,/home/odoo/src/custo