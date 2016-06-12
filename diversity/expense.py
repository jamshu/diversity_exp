# -*- coding: utf-8 -*-
from openerp import models,api,fields
class expense_register(models.Model):
    _name = "expense.register"
    _description = "Expense Register"
    name = fields.Char(string="Enter Description")
    date = fields.Date(string="Date",default=fields.Date.context_today)
    exp_desc_ids = fields.One2many('expense.desc.line','exp_id',string="Expense Desc Line")
class expense_desc_line(models.Model):
    _name = "expense.desc.line"
    exp_id = fields.Many2one('expense.register',string='Expense Session')
    date = fields.Date(string="Date",default=fields.Date.context_today)
    name = fields.Char(string="Description")
    payment_type = fields.Selection([('company','Company'),('individual','Individual')],string="Payment Type")
    participant_ids = fields.Many2many('res.partner','rel_partner_exp','exp_id','partner_id',string="Participants")
    paid_by = fields.Many2one('res.partner',string="Paid By")
