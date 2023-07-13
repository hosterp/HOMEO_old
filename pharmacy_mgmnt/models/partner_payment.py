from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.tools import safe_eval
from datetime import datetime
from dateutil.relativedelta import relativedelta


class InvoiceDetails(models.Model):
    _name = 'invoice.details'
    _inherits = {'account.invoice': 'invoice_id'}

    invoice_id = fields.Many2one('account.invoice', required=True)
    partner_payment_id = fields.Many2one('partner.payment')
    select = fields.Boolean()

    @api.model
    def create(self, vals):
        if not vals.get('account_id'):
            account_id = self.env['account.invoice'].browse(int(vals.get('invoice_id'))).account_id.id
            vals.update({'account_id': account_id})
        return super(InvoiceDetails, self).create(vals)


class PartnerPayment(models.Model):
    _inherits = {'account.voucher': 'voucher_relation_id'}
    _name = 'partner.payment'
    _rec_name = 'reference_number'

    voucher_relation_id = fields.Many2one('account.voucher', required=True)
    res_person_id = fields.Many2one('res.partner', domain=[('res_person_id', '=', True)])
    partner_id = fields.Many2one('res.partner', domain=[('customer', '=', True), ('res_person_id', '=', False)])
    reference_number = fields.Char()
    date = fields.Date()
    payment_method = fields.Selection([('cheque', 'Cheque'), ('cash', 'Cash')], string="Mode of Payment")
    cheque_no = fields.Char()
    cheque_date = fields.Date()
    remarks = fields.Text()
    # total_amount = fields.Float(compute='_compute_amount')
    total_amount = fields.Float(compute='_compute_value', store=True)
    payment_amount = fields.Float()
    balance_amount = fields.Float(compute='_compute_balance')
    # balance_amount = fields.Float()
    invoice_ids = fields.One2many('invoice.details', 'partner_payment_id', compute='generate_lines', readonly=False,
                                  store=True)
    state = fields.Selection([('new', 'New'), ('draft', 'Draft'), ('paid', 'Paid')])

    # modified code
    #
    #     @api.onchange('partner_id')
    #     def onchange_partner_id(self):
    #         for rec in self:
    #             if rec.partner_id:
    #                 rec.invoice_ids = []
    #                 list = []
    #                 invoices = self.env['account.invoice'].search(
    #                     [('partner_id', '=', rec.partner_id.id),('packing_slip','=',False),('holding_invoice','=',False)])
    #                 if invoices:
    #                     print("fetched the invoices for payments........................")
    #                     for line in invoices:
    #                         # if line.state == 'open':
    #                             list.append([0, 0, {'partner_id': line.partner_id.id,
    #                                                 'name': line.name,
    #                                                 'reference': line.reference,
    #                                                 'type': line.type,
    #                                                 'state': line.state,
    #                                                 'amount_total': line.amount_total,
    #                                                 'amount_untaxed': line.amount_untaxed,
    #                                                 'amount_tax': line.amount_tax,
    #                                                 'residual': line.residual,
    #                                                 'currency_id': line.currency_id.id,
    #                                                 'origin': line.origin,
    #                                                 'date_invoice': line.date_invoice,
    #                                                 'journal_id': line.journal_id.id,
    #                                                 'period_id': line.period_id.id,
    #                                                 'company_id': line.company_id.id,
    #                                                 'user_id': line.user_id.id,
    #                                                 'date_due': line.date_due,
    #                                                 'number2': line.number2,
    #                                                 'account_id': line.account_id.id,
    #                                                 'invoice_id': line.id
    #                                                 }
    #                                          ])
    #                 rec.invoice_ids = list
    #                 print ('onchange')
    #                 print(list)
    #
    #     @api.onchange('res_person_id')
    #     def onchange_res_partner_id(self):
    #         for rec in self:
    #             if rec.partner_id:
    #                 rec.invoice_ids = []
    #                 list = []
    #                 invoices = self.env['account.invoice'].search(
    #                                 [('partner_id', '=', rec.partner_id.id), ('res_person', '=', rec.res_person_id.id),('packing_slip','=',False),('holding_invoice','=',False)])
    #                 if invoices:
    #                     print("fetched the invoices for payments........................")
    #                     for line in invoices:
    #                         # if line.state == 'open':
    #                         list.append([0, 0, {'partner_id': line.partner_id.id,
    #                                             'name': line.name,
    #                                             'reference': line.reference,
    #                                             'type': line.type,
    #                                             'state': line.state,
    #                                             'amount_total': line.amount_total,
    #                                             'amount_untaxed': line.amount_untaxed,
    #                                             'amount_tax': line.amount_tax,
    #                                             'residual': line.residual,
    #                                             'currency_id': line.currency_id.id,
    #                                             'origin': line.origin,
    #                                             'date_invoice': line.date_invoice,
    #                                             'journal_id': line.journal_id.id,
    #                                             'period_id': line.period_id.id,
    #                                             'company_id': line.company_id.id,
    #                                             'user_id': line.user_id.id,
    #                                             'date_due': line.date_due,
    #                                             'number2': line.number2,
    #                                             'account_id': line.account_id.id,
    #                                             'invoice_id': line.id
    #                                             }
    #                                      ])
    #                 rec.invoice_ids = list
    #                 print('onchange')
    #                 print(list)

    #     -----------------------------

    @api.onchange('res_person_id', 'partner_id')
    def onchange_id(self):
        print('I am herte')
        for rec in self:
            print('I am herte22')
            if rec.res_person_id and rec.partner_id:
                rec.invoice_ids = []
                print('I am herte333')
                list = []
                invoices = self.env['account.invoice'].search(
                    [('partner_id', '=', rec.partner_id.id), ('res_person', '=', rec.res_person_id.id),
                     ('packing_slip', '=', False), ('holding_invoice', '=', False)])
                if invoices:
                    for line in invoices:
                        if line.state == 'open':
                            list.append([0, 0, {'partner_id': line.partner_id.id,
                                                'name': line.name,
                                                'reference': line.reference,
                                                'type': line.type,
                                                'state': line.state,
                                                'amount_total': line.amount_total,
                                                'amount_untaxed': line.amount_untaxed,
                                                'amount_tax': line.amount_tax,
                                                'residual': line.residual,
                                                'currency_id': line.currency_id.id,
                                                'origin': line.origin,
                                                'date_invoice': line.date_invoice,
                                                'journal_id': line.journal_id.id,
                                                'period_id': line.period_id.id,
                                                'company_id': line.company_id.id,
                                                # 'user_id': line.user_id.id,
                                                'date_due': line.date_due,
                                                'number2': line.number2,
                                                'account_id': line.account_id.id,
                                                'invoice_id': line.id
                                                }
                                         ])
                rec.invoice_ids = list

    @api.depends('res_person_id', 'partner_id')
    def generate_lines(self):
        print(self)
        for rec in self:
            rec.account_id = 25
            rec.invoice_ids = []
            if rec.res_person_id and rec.partner_id:
                list = []
                invoices = self.env['account.invoice'].search(
                    [('partner_id', '=', rec.partner_id.id), ('res_person', '=', rec.res_person_id.id),
                     ('packing_slip', '=', False), ('holding_invoice', '=', False)])
                if invoices:
                    for line in invoices:
                        if line.state == 'open':
                            list.append([0, 0, {'partner_id': line.partner_id.id,
                                                'name': line.name,
                                                'reference': line.reference,
                                                'type': line.type,
                                                'state': line.state,
                                                'amount_total': line.amount_total,
                                                'amount_untaxed': line.amount_untaxed,
                                                'residual': line.residual,
                                                'currency_id': line.currency_id.id,
                                                'origin': line.origin,
                                                'date_invoice': line.date_invoice,
                                                'journal_id': line.journal_id.id,
                                                'period_id': line.period_id.id,
                                                'company_id': line.company_id.id,
                                                # 'user_id': line.user_id.id,
                                                'date_due': line.date_due,
                                                'number2': line.number2,
                                                'account_id': line.account_id.id,
                                                'invoice_id': line.id
                                                }
                                         ])
                rec.invoice_ids = list
                print('depends')

                print(list)

    @api.onchange('invoice_ids')
    def onchange_compute(self):
        for record in self:
            if record.invoice_ids:
                # record.total_amount = sum(line.residual for line in record.invoice_ids)
                record.total_amount = sum(line.residual for line in record.invoice_ids)

    @api.depends('invoice_ids')
    def _compute_value(self):
        for record in self:
            if record.invoice_ids:
                # record.total_amount = sum(line.residual for line in record.invoice_ids) - sum(line.amount_tax for line in record.invoice_ids)
                record.total_amount = sum(line.residual for line in record.invoice_ids)

    @api.depends('total_amount', 'payment_amount')
    def _compute_balance(self):
        for record in self:
            if record.total_amount and record.payment_amount:
                difference = record.total_amount - record.payment_amount
                if difference < 0:
                    raise osv.except_osv(_('Warning!'), _("Total amount is less than payment amount."))
                record.balance_amount = max(difference, 0.0)

    @api.multi
    def action_payment_all(self, context=None):
        payment_amount = self.payment_amount
        for record in self.invoice_ids:
            if record.select:
                amount = 0
                invoice = record.invoice_id
                if payment_amount > 0:
                    if invoice.residual < payment_amount:
                        amount = invoice.residual
                    else:
                        amount = payment_amount
                    self.voucher_relation_id.amount = self.payment_amount
                    if amount == invoice.residual:
                        invoice.state = 'paid'
                        invoice.paid_bool = True
                    else:

                        move = self.env['account.move']
                        move_line = self.env['account.move.line']

                        values5 = {
                            'journal_id': 9,
                            'date': self.date,
                            'tds_id': invoice.id
                            # 'period_id': self.period_id.id,623393
                        }
                        move_id = move.create(values5)
                        balance_amount = invoice.residual - payment_amount
                        balance_amount += invoice.amount_tax
                        values4 = {
                            'account_id': 25,
                            'name': 'payment for invoice No ' + str(invoice.number2),
                            'debit': 0.0,
                            'credit': balance_amount,
                            'move_id': move_id.id,
                            'cheque_no': self.cheque_no,
                            'invoice_no_id2': invoice.id,
                        }
                        line_id1 = move_line.create(values4)

                        values6 = {
                            'account_id': invoice.account_id.id,
                            'name': 'Payment For invoice No ' + str(invoice.number2),
                            'debit': balance_amount,
                            'credit': 0.0,
                            'move_id': move_id.id,
                            'cheque_no': self.cheque_no,
                            # 'invoice_no_id2': line.bill_no.id,
                        }
                        line_id2 = move_line.create(values6)

                        invoice.move_id = move_id.id
                        invoice.move_lines = move_id.line_id.ids
                        move_id.button_validate()
                        move_id.post()
                        name = move_id.name
                        self.voucher_relation_id.write({
                            'move_id': move_id.id,
                            'state': 'posted',
                            'number': name,
                        })
                    payment_amount = payment_amount - amount
                    self.state = 'paid'
        payment_records = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner_id.id), ('state', '!=', 'draft')])
        print("records invoice", payment_records)
        record_count = len(payment_records)
        count = 0
        if payment_records:
            for rec in payment_records:
                if rec.state == 'paid':
                    count = count + 1
        if count == record_count:
            print("all payments are done")
            customer_details = self.env['res.partner'].browse(self.partner_id.id)
            if customer_details:
                date_today = self.date
                x = datetime.strptime(date_today, '%Y-%m-%d')
                next_date = x + relativedelta(days=customer_details.days_credit_limit)
                cal_date = datetime.strftime(next_date, '%Y-%m-%d')
                customer_details.write({'credit_end_date': cal_date})

        else:
            print("there are payments to be completed")

        return True

    @api.multi
    def open_tree_view_history(self, context=None):
        if self.res_person_id:
            field_ids = self.env['account.invoice'].search(
                [('res_person', '=', self.res_person_id.id), ('packing_slip', '=', False),
                 ('holding_invoice', '=', False)]).ids
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

    @api.model
    def create(self, vals):
        if not vals.get('reference_number'):
            vals['reference_number'] = self.env['ir.sequence'].next_by_code(
                'partner.payment')
        vals.update({'state': 'draft'})
        vals.update({'account_id': 25})
        result = super(PartnerPayment, self).create(vals)
        return result


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    @api.model
    def compute_refund(self, mode='refund'):
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False

        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    pass
                    # raise UserError(_('Cannot refund draft/proforma/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    pass
                    # raise UserError(_(
                    #     'Cannot refund invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)

                created_inv.append(refund.id)
                if inv.picking_transfer_id.code == 'outgoing':
                    data = self.env['stock.picking.type'].search(
                        [('warehouse_id.company_id', '=', company_id), ('code', '=', 'incoming')], limit=1)
                    refund.picking_transfer_id = data.id
                if inv.picking_type_id.code == 'incoming':
                    data = self.env['stock.picking.type'].search(
                        [('warehouse_id.company_id', '=', company_id), ('code', '=', 'outgoing')], limit=1)
                    refund.picking_type_id = data.id
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.action_invoice_open()
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                    to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
                    if mode == 'modify':
                        invoice = inv.read(inv_obj._get_refund_modify_read_fields())
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line'])
                        invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                        })
                        for field in inv_obj._get_refund_common_fields():
                            if inv_obj._fields[field].type == 'many2one':
                                invoice[field] = invoice[field] and invoice[field][0]
                            else:
                                invoice[field] = invoice[field] or False
                        inv_refund = inv_obj.create(invoice)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = (inv.type in ['out_refund', 'out_invoice']) and 'action_invoice_tree1' or \
                         (inv.type in ['in_refund', 'in_invoice']) and 'action_invoice_tree2'
                # Put the reason in the chatter
                subject = _("Invoice refund")
                body = description
                refund.message_post(body=body, subject=subject)
        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True
