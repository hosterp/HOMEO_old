import datetime
from openerp import api, models, fields, _
from openerp.exceptions import Warning


class TaxReportWizard(models.TransientModel):
    _name = 'tax.report.wizard'

    from_date = fields.Date()
    customer = fields.Many2one('res.partner', domain=[('customer', '=', True)])
    product = fields.Many2one('product.product')
    potency = fields.Many2one('product.medicine.subcat')
    to_date = fields.Date()
    group = fields.Many2one('product.medicine.group')
    company = fields.Many2one('product.medicine.responsible')
    packing = fields.Many2one('product.medicine.packing')
    b2c = fields.Boolean()
    b2b = fields.Boolean()
    by_hsn = fields.Boolean()

    @api.onchange('by_hsn')
    def onchange_by_hsn(self):
        if self.b2c:
            raise Warning(_('Please select any one (by HSN or b2c or b2b)'))

    @api.onchange('b2c')
    def onchange_b2c(self):
        if self.b2c:
            self.by_hsn = False
            self.b2b = False
    @api.onchange('by_hsn')
    def onchange_by_hsn(self):
        if self.by_hsn:
            self.b2c = False
            self.b2b = False
    @api.onchange('b2b')
    def onchange_b2b(self):
        if self.b2b:
            self.by_hsn = False
            self.b2c = False

    @api.multi
    def view_tax_report(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pharmacy_mgmnt.tax_report_template',
            'datas': datas,
            'report_type': 'qweb-html',
        }

    @api.model
    def get_tax_invoices(self):
        domain = [('state', '=', 'paid'), ('type', '=', 'out_invoice')]
        if self.from_date:
            domain = [('invoice_id.date_invoice', '>=', self.from_date)]
        if self.to_date:
            domain += [('invoice_id.date_invoice', '<=', self.to_date)]
        if not self.to_date:
            domain += [('invoice_id.date_invoice', '<=', datetime.datetime.today())]
        if self.customer:
            domain += [('invoice_id.partner_id', '=', self.customer.id)]
        if self.product:
            domain += [('product_id', '=', self.product.id)]
        if self.potency:
            domain += [('medicine_name_subcat', '=', self.potency.id)]
        if self.packing:
            domain += [('medicine_name_packing', '=', self.packing.id)]
        if self.company:
            domain += [('product_of', '=', self.company.id)]
        if self.group:
            domain += [('medicine_grp', '=', self.group.id)]
        res = self.env['account.invoice.line'].search(domain)
        return res

    @api.multi
    def print_tax_report(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pharmacy_mgmnt.tax_report_template',
            'datas': datas,
            'report_type': 'qweb-pdf',
            #
        }

    @api.multi
    def print_tax_report_excel(self):
        if self.by_hsn:
            if self.b2c:
                raise Warning(_('Please select any one (by HSN or b2c)'))
            else:
                datas = {
                    'ids': self._ids,
                    'model': self._name,
                    'form': self.read(),
                    'context': self._context,
                }
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'pharmacy_mgmnt.b2b_hsn_tax_report_template',
                    'datas': datas,
                    'report_type': 'qweb-pdf',
                }

        # excel not working in offline so created PDF for Offline
        # data = {}
                # data['form'] = self.read(['from_date', 'to_date'])
                # return {'type': 'ir.actions.report.xml',
                #         'report_name': 'pharmacy_mgmnt.report_tax_excel.xlsx',
                #         'datas': data
                #         }
        else:
            datas = {
                'ids': self._ids,
                'model': self._name,
                'form': self.read(),
                'context': self._context,
            }
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'pharmacy_mgmnt.b2b_tax_report_template',
                'datas': datas,
                'report_type': 'qweb-pdf',
            }

    @api.multi
    def get_b2b_hsn_tax_invoices(self):
        partner_ids = self.env['res.partner'].search([
            ('b2b', '=', True),])
        
        invoice_ids = self.env['account.invoice'].search([
            ('date_invoice', '>=', self.from_date),
            ('date_invoice', '<=', self.to_date),
            ('partner_id', 'in', partner_ids.ids),
            ('packing_slip','=',False),
            ('holding_invoice','=',False),
            ('type', '=', 'out_invoice')])
        return invoice_ids

    @api.multi
    def get_b2b_tax_invoices(self):
        if self.b2c:
            partner_ids = self.env['res.partner'].search([
                ('b2c', '=', True),('b2b', '=', False) ])

            invoices = self.env['account.invoice'].search(
                [("date_invoice", ">=", self.from_date), ("date_invoice", "<=", self.to_date),
                 ('partner_id.customer', '=', True), ('partner_id', 'in', partner_ids.ids),
                 ('packing_slip','=',False),('holding_invoice','=',False),
                 ('type', '=', 'out_invoice')])
        elif self.b2b:
            partner_ids = self.env['res.partner'].search([
                ('b2b', '=', True), ('b2c', '=', False)])
            invoices = self.env['account.invoice'].search(
                [("date_invoice", ">=", self.from_date), ("date_invoice", "<=", self.to_date),
                 ('partner_id.customer', '=', True), ('partner_id', 'in', partner_ids.ids),
                 ('packing_slip','=',False), ('holding_invoice','=',False),
                 ('type', '=', 'out_invoice')])
        else:
            invoices = self.env['account.invoice'].search(
                [("date_invoice", ">=", self.from_date), ("date_invoice", "<=", self.to_date),
                 ('partner_id.customer', '=', True),
                 ('packing_slip', '=', False), ('holding_invoice', '=', False),
                 ('type', '=', 'out_invoice')])

        data_list = []
        for invoice in invoices:
            tax_5 = invoice.invoice_line.filtered(lambda l: l.invoice_line_tax_id4 == 5)
            tax_12 = invoice.invoice_line.filtered(lambda l: l.invoice_line_tax_id4 == 12)
            tax_18 = invoice.invoice_line.filtered(lambda l: l.invoice_line_tax_id4 == 18)

            tax_5_sum = sum(tax_5.mapped('amt_tax'))
            tax_12_sum = sum(tax_12.mapped('amt_tax'))
            tax_18_sum = sum(tax_18.mapped('amt_tax'))

            total_amount_sgst_5 = tax_5_sum/2
            total_amount_sgst_12 = tax_12_sum/2
            total_amount_sgst_18 = tax_18_sum/2

            total_amount_cgst_5 = tax_5_sum/2
            total_amount_cgst_12 = tax_12_sum/2
            total_amount_cgst_18 = tax_18_sum/2

            vals = {'invoice': invoice,

                    'tax_5_sum': tax_5_sum,
                    'tax_12_sum': tax_12_sum,
                    'tax_18_sum': tax_18_sum,

                    'total_amount_sgst_5': total_amount_sgst_5,
                    'total_amount_sgst_12': total_amount_sgst_12,
                    'total_amount_sgst_18': total_amount_sgst_18,

                    'total_amount_cgst_5': total_amount_cgst_5,
                    'total_amount_cgst_12': total_amount_cgst_12,
                    'total_amount_cgst_18': total_amount_cgst_18}
            data_list.append(vals)
        return data_list
