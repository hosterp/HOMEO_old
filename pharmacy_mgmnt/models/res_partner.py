from openerp import models, fields, api
from openerp import models, fields, api, tools, _


class CusArea(models.Model):
    _name = 'customer.area'
    _rec_name = 'cus_area'

    cus_area = fields.Char(string="Customer Area")


class CustomerTypes(models.Model):
    _name = 'customer.title'
    _rec_name = 'cus_type'

    cus_type = fields.Char(string="Customer Type")


class ResPartner(models.Model):
    _inherit = "res.partner"

    discount_category = fields.Many2one('cus.discount','Discount Category')
    cus_title = fields.Many2one('customer.title', "Customer Type")
    cust_area = fields.Many2one('customer.area', "Customer Area")

    @api.constrains('name')
    def _check_name_product(self):
        for record in self:
            old_record = self.search([('name', '=', record.name)])
            if len(old_record.ids) > 1:
                raise models.ValidationError('Record Already existing with same name')


    # _sql_constraints = [
    #     ('name_uniq', 'UNIQUE(name)', 'The name of batch must be unique !'),
    # ]

    @api.onchange('b2b')
    def _change_boolean_b2b(self):
        for rec in self:
            if rec.b2b:
                rec.b2c = False
    @api.onchange('b2c')
    def _change_boolean_b2c(self):
        for rec in self:
            if rec.b2c:
                rec.b2b = False
    @api.onchange('interstate_customer')
    def _change_boolean_interstate_customer(self):
        for rec in self:
            if rec.interstate_customer:
                rec.local_customer = False

    @api.onchange('local_customer')
    def _change_boolean_local_customer(self):
        for rec in self:
            if rec.local_customer:
                rec.interstate_customer = False


    # @api.multi
    # @api.depends('gst_no')
    # def _change_boolean_status(self):
    #     for rec in self:
    #         if rec.gst_no:
    #             rec.b2b = True
    #             rec.b2c = False
    #         else:
    #             rec.b2c = True
    #             rec.b2b = False

    local_customer = fields.Boolean(default=True)
    interstate_customer = fields.Boolean()
    b2b = fields.Boolean()
    # b2b = fields.Boolean(compute="_change_boolean_status")
    b2c = fields.Boolean()
    gst_no = fields.Char()
    drug_license_number = fields.Char()
    address_new = fields.Text('Address')
    res_person_id = fields.Boolean('Sale Responsible Person ?')

    @api.multi
    def open_tree_view(self, context=None):
        field_ids = self.env['account.invoice'].search([('res_person', '=', self.id),('packing_slip','=',False),('holding_invoice','=',False)]).ids

        domain = [('id', 'in', field_ids)]

        view_id_tree = self.env['ir.ui.view'].search([('name', '=', "model.tree")])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'tree,form',
            # 'views': [(view_id_tree[0].id, 'tree'), (False, 'form')],
            'view_id ref="pharmacy_mgmnt.tree_view"': '',
            'target': 'current',
            'domain': domain,
        }


# GROUPS AND RESTRICTIONS

class ResUsers(models.Model):
    _inherit = 'res.users'

    hide_menu_access_ids = fields.Many2many('ir.ui.menu', 'ir_ui_hide_menu_rel', 'uid', 'menu_id',
                                            string='Hide Access Menu')


class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(Menu, self)._visible_menu_ids(debug)
        if self.env.user.hide_menu_access_ids and not self.env.user.has_group('base.group_system'):
            for rec in self.env.user.hide_menu_access_ids:
                menus.discard(rec.id)
            return menus
        return menus



