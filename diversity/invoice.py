# -*- coding: utf-8 -*-
from odoo import models,api,fields
class account_invoice(models.Model):
    _inherit ="account.invoice"
    div_expense = fields.Float(string="Expense",readonly=True)
    div_payed_amount = fields.Float(string="Payed Amount",readonly=True)
    div_return_amount = fields.Float(string="Return Amount",readonly=True)
    div_balance = fields.Float(string="Balance",readonly=True)
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    _order ="date ASC"
    date = fields.Date(string="Date")
    bill_amount = fields.Float(string="Bill Amount")
    paid_by = fields.Many2one('res.partner',string="Paid By")
