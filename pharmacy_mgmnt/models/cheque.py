from datetime import datetime, timedelta
from datetime import timedelta
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning


# import models
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, tools, _


class ChequeTransactions(models.Model):
    _name = 'cheque.entry'
    _rec_name = 's_no'

    s_no = fields.Char('Serial Number', readonly=True, required=True, copy=False, default='New')
    name = fields.Many2one('res.partner', 'Name', required=1)
    t_date = fields.Date('Date', required=1)
    cheque_no = fields.Char('Cheque Number')
    cheque_date = fields.Date('Cheque Date')
    deposit_date = fields.Date('Deposit Date')
    clearance_date = fields.Date('Clearance Date')
    cheque_amount = fields.Float('Cheque Amount', required=1)
    invoice_amount = fields.Float('Invoice Amount', compute="_get_balace_amt")
    balance = fields.Float('Balance', compute="_get_balace_amt")
    bank = fields.Char('Bank')
    branch = fields.Char('Branch')
    ifsc = fields.Char('IFSC')
    state = fields.Selection([('draft', 'Draft'), ('post', 'Posted'), ('bounce', 'Bounced'),]
                             , required=True, default='draft')
    invoice_ids = fields.Many2many('account.invoice', string="Select Invoices")

    @api.depends('cheque_amount','invoice_ids')
    def _get_balace_amt(self):
        for rec in self:
            if rec.invoice_ids:
                rec.invoice_amount = sum(rec.invoice_ids.mapped('amount_total'))
                balance = rec.cheque_amount - rec.invoice_amount
                if rec.cheque_amount != rec.invoice_amount:
                    raise except_orm(_('Partial Payments not possible!'), ('Check Customer Payments'))
                else:
                    pass
                if balance<0 :
                    rec.balance = 0
                else:
                    pass


    @api.model
    def create(self, vals):
        vals['s_no'] = self.env['ir.sequence'].next_by_code('cheque.entry.sequence')
        result = super(ChequeTransactions, self).create(vals)
        return result

    @api.multi
    def post(self):
        for rec in self:
            if not rec.invoice_ids:
                raise except_orm(_('No invoices Selected!'), ('please Select some Invoices to pay'))
            else:
                if rec.cheque_amount > 0:
                    rec.balance = rec.cheque_amount
                    balance_cheque_amount = rec.cheque_amount
                    for invoice in rec.invoice_ids:
                        if invoice.state == 'open' and invoice.residual > 0:
                            if invoice.residual <= balance_cheque_amount:
                                balance_cheque_amount = balance_cheque_amount - invoice.residual
                                invoice.paid_bool = True
                                invoice.write({'state': 'paid'})
                            else:
                                if balance_cheque_amount > 0:
                                    move = rec.env['account.move']
                                    move_line = rec.env['account.move.line']
                                    values5 = {
                                        'journal_id': 9,
                                        'date': rec.t_date,
                                        'tds_id': invoice.id
                                        # 'period_id': self.period_id.id,623393
                                    }
                                    move_id = move.create(values5)
                                    balance_amount = invoice.residual - balance_cheque_amount

                                    values4 = {
                                        'account_id': 25,
                                        'name': 'payment for invoice No ' + str(invoice.number2),
                                        'debit': 0.0,
                                        'credit': balance_amount,
                                        'move_id': move_id.id,
                                        'cheque_no': rec.cheque_no,
                                        'invoice_no_id2': invoice.id,
                                    }
                                    line_id1 = move_line.create(values4)

                                    values6 = {
                                        'account_id': invoice.account_id.id,
                                        'name': 'Payment For invoice No ' + str(invoice.number2),
                                        'debit': balance_amount,
                                        'credit': 0.0,
                                        'move_id': move_id.id,
                                        'cheque_no': rec.cheque_no,
                                        # 'invoice_no_id2': line.bill_no.id,
                                    }
                                    line_id2 = move_line.create(values6)

                                    invoice.move_id = move_id.id
                                    invoice.move_lines = move_id.line_id.ids
                                    move_id.button_validate()
                                    move_id.post()
                                    # name = move_id.name
                                    # rec.voucher_relation_id.write({
                                    #     'move_id': move_id.id,
                                    #     'state': 'posted',
                                    #     'number': name,
                                    # })
                                    balance_cheque_amount = 0
                    rec.write({'state': 'post'})


    @api.multi
    def bounce(self):
        for rec in self:
            rec.balance = 0
            rec.write({'state': 'bounce'})




