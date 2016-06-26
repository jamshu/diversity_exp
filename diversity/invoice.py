# -*- coding: utf-8 -*-
from openerp import models,api,fields
class account_invoice(models.Model):
    _inherit ="account.invoice"
    div_expense = fields.Float(string="Expense")
    div_payed_amount = fields.Float(string="Payed Amount")
    div_balance = fields.Float(string="Balance")
