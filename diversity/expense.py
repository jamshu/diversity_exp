# -*- coding: utf-8 -*-
from openerp import models,api,fields
class expense_register(models.Model):
    _name = "expense.register"
    _description = "Expense Register"

    @api.model
    def create(self,vals):
        print "valsddfdfdfdfffffffffffffffff",vals
        return super(expense_register,self).create(vals)
    @api.one
    def get_report_line(self):
        report_obj = self.env['cash.report']
        exp_id = self.id
        lines = [{'payed_amount': 45, 'balance': 550, 'partner_id': 6, 'exp_amount': 344,'exp_id':exp_id}]
        self.report_ids.unlink()
        for line in lines:
            report_obj.create(line)

    name = fields.Char(string="Enter Description")
    date = fields.Date(string="Date",default=fields.Date.context_today)
    exp_desc_ids = fields.One2many('expense.desc.line','exp_id',string="Expense Desc Line")
    cash_flow_ids = fields.One2many('cash.flow','exp_id',string="Expense Desc Line")
    report_ids = fields.One2many('cash.report','exp_id',string="Reports",readonly=True)
class expense_desc_line(models.Model):
    _name = "expense.desc.line"
    exp_id = fields.Many2one('expense.register',string='Expense Session')
    date = fields.Date(string="Date",default=fields.Date.context_today)
    name = fields.Char(string="Description")
    payment_type = fields.Selection([('company','Company'),('individual','Individual')],string="Payment Type")
    participant_ids = fields.Many2many('res.partner','rel_partner_exp','exp_id','partner_id',string="Participants")
    amount = fields.Float(string="Amount")
    paid_by = fields.Many2one('res.partner',string="Paid By")
class cash_flow(models.Model):
    _name ="cash.flow"
    exp_id = fields.Many2one('expense.register',string='Expense Session')
    date = fields.Date(string="Date",default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner',string="Giver")
    amount = fields.Float(string="Amount")
class cash_report(models.Model):
    _name  = "cash.report"
    exp_id = fields.Many2one('expense.register',string='Expense Session')
    partner_id = fields.Many2one('res.partner',string="Partner")
    exp_amount = fields.Float(string="Expense")
    payed_amount = fields.Float(string="Payed Amount")
    balance = fields.Float(string="Balance")
