# -*- coding: utf-8 -*-
from openerp import fields,models,api
class individual_wiz(models.TransientModel):
    _name = "individual.wiz"
    partner_id = fields.Many2one('res.partner',string="Partner")
    expense = fields.Float(string="Total Expense",readonly=True)
    payment = fields.Float(string="Total Payment",readonly=True)
    balance = fields.Float(string="Balance",readonly=True)
    report_line = fields.One2many('individual.report.line','wiz_id',string="Report Line",readonly=True)
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
