# -*- coding: utf-8 -*-
from openerp import fields,models,api
class individual_wiz(models.TransientModel):
    _name = "individual.wiz"
    partner_id = fields.Many2one('res.partner',string="Partner",required=True)
    expense = fields.Float(string="Total Expense",readonly=True)
    payment = fields.Float(string="Total Payment",readonly=True)
    balance = fields.Float(string="Balance",readonly=True)
    report_line = fields.One2many('individual.report.line','wiz_id',string="Report Line",readonly=True)

    def get_journal(self):
        journal_obj = self.env['account.journal']
        journal_type = 'sale'
        journal = journal_obj.search([('type', '=', journal_type)],limit=1)
        return journal.id
    def get_invoice_line_val(self):
        data = []
        for line in self.report_line:
            data.append({'name':line.name,'price_unit':line.share})
        return data
    @api.multi
    def create_invoice(self):
        invoice = self.env['account.invoice']
        invoice_line_vals = self.env['account.invoice.line']
        account_vals  =invoice_line_vals.default_get(['account_id','quantity'])
        partner_id = self.partner_id and self.partner_id.id
        journal_id = self.get_journal()
        account_id = self.partner_id and self.partner_id.property_account_receivable and self.partner_id.property_account_receivable.id
        vals = {'partner_id':partner_id,'journal_id':journal_id,'account_id':account_id,'type':'out_invoice'}
        invoice_line = self.get_invoice_line_val()
        line_vals = []
        for val in invoice_line:
            val.update(account_vals)
            line_vals.append((0,0,val))
        vals.update({'invoice_line':line_vals})
        invoice_id = invoice.create(vals)
        models_data = self.env['ir.model.data']
        dummy, form_view = models_data.get_object_reference('account','invoice_form')
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'views': [(form_view or False, 'form')],
                'res_id':invoice_id.id,
                'type': 'ir.actions.act_window',
            }
    @api.multi
    def load(self):
        ctx = self.env.context
        active_id = ctx.get('active_id',False)
        wiz_id = self.id
        expense_reg = self.env['expense.register']
        expense_obj = expense_reg.browse(active_id)
        partner_id = self.partner_id and self.partner_id.id
        payment,expense = expense_obj.get_ind_header(partner_id)
        self.payment = payment
        self.expense = expense
        self.balance = payment - expense
        details = expense_obj.get_ind_detail(partner_id)
        self.report_line = details
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'individual.wiz',
                'res_id':wiz_id,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
class individual_report_line(models.TransientModel):
    _name = "individual.report.line"
    wiz_id = fields.Many2one('individual.wiz',string="Wizard")
    total_expense = fields.Float(string="Actual Expense")
    share = fields.Float(string="Your Share")
    name = fields.Char(string="Expense Detail")
    date = fields.Date(string="Date")
