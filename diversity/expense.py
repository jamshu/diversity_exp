# -*- coding: utf-8 -*-
from openerp import models,api,fields
import itertools


class expense_register(models.Model):
    _name = "expense.register"
    _description = "Expense Register"
    _inherit = ['mail.thread']


    def od_deduplicate(self,l):
        result = []
        for item in l :
            check = False
            # check item, is it exist in result yet (r_item)
            for r_item in result :
                if item['partner_id'] == r_item['partner_id'] :
                    # if found, add all key to r_item ( previous record)
                    check = True
                    exp_amount = r_item.get('exp_amount',0)
                    exp_amount +=item.get('exp_amount',0)
                    payed_amount = r_item.get('payed_amount',0)
                    payed_amount += item.get('payed_amount',0)
                    return_amount = r_item.get('return_amount',0)
                    return_amount += item.get('return_amount',0)
                    r_item['exp_amount'] = exp_amount
                    r_item['payed_amount'] =payed_amount
                    r_item['return_amount'] = return_amount
            if check == False :
                # if not found, add item to result (new record)
                result.append( item )

        return result
    @api.multi
    def open_report_wiz(self):

        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'individual.wiz',
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    def get_ind_detail(self,partner_id):
        data = []
        for line in self.exp_desc_ids:
            exp_amount = line.amount
            ppl_count = len(line.participant_ids)
            if ppl_count:
                unit_amount = exp_amount/ppl_count
                for part in line.participant_ids:
                    if  part.id == partner_id:
                        data.append({'date':line.date,'name':line.name,'total_expense':exp_amount,'share':unit_amount,'paid_by':line.paid_by and line.paid_by.id})
        return data
    def get_payment_detail(self,partner_id):
        data = []
        for line in self.exp_desc_ids:
            if line.paid_by and line.paid_by.id == partner_id:
                data.append({'date':line.date,'name':line.name,'payed_amount':line.amount})
        for line in self.cash_flow_ids:
            if line.partner_id and line.partner_id.id == partner_id:
                data.append({'date':line.date,'name':'Cash Payment To Company','payed_amount':line.amount})
        return data
    def get_ind_header(self,partner_id):
        expense = self.get_expenses()
        return_vals = self.get_return_vals()
        payments = self.get_payments()
        p_exp = 0.0
        p_pay = 0.0
        return_amount = 0.0
        for exp in expense:
            if exp['partner_id'] == partner_id:
                p_exp = exp['exp_amount']
        for pay in payments:
            if pay['partner_id'] == partner_id:
                p_pay = pay['payed_amount']
        for ret in return_vals:
            if ret['partner_id'] == partner_id:
                return_amount = ret['return_amount']
        return p_pay,p_exp,return_amount
    def get_expenses(self):
        exp_list= []

        for line in self.exp_desc_ids:
            exp_amount = line.amount
            ppl_count = len(line.participant_ids)
            if ppl_count:
                unit_amount = exp_amount/ppl_count
                for part in line.participant_ids:
                    exp_list.append({'partner_id':part.id,'exp_amount':unit_amount})
        result = self.od_deduplicate(exp_list)
        # result = reduce(lambda x, y: dict((k, v + y[k]) for k, v in x.iteritems()), exp_list)
        return result

    def get_return_vals(self):
        return_list = []
        for line in self.cash_return_ids:
            val={'partner_id':line.partner_id.id,'return_amount':line.amount}
            return_list.append(val)
        result = self.od_deduplicate(return_list)
        return result
    def get_payments(self):
        pay_list = []
        for line in self.exp_desc_ids:
            if line.paid_by:
                val={'partner_id':line.paid_by.id,'payed_amount':line.amount}
                pay_list.append(val)
        for line in self.cash_flow_ids:
            if line.partner_id:
                val={'partner_id':line.partner_id.id,'payed_amount':line.amount}
                pay_list.append(val)
        result = self.od_deduplicate(pay_list)
        return result
    def get_return(self):
        pay_list = []
        for line in self.cash_return_ids:
            if line.partner_id:
                val={'partner_id':line.partner_id.id,'return_amount':line.amount}
                pay_list.append(val)
        result = self.od_deduplicate(pay_list)
        return result
    def get_vals(self):
        exp_id = self.id
        expenses = self.get_expenses()
        payments = self.get_payments()
        return_vals = self.get_return()
        vals = expenses + payments + return_vals
        result= self.od_deduplicate(vals)
        return result
    @api.one
    def get_report_line(self):
        report_obj = self.env['cash.report']
        exp_id = self.id
        vals = self.get_vals()
        self.report_ids.unlink()
        for val in vals:
            val.update({'exp_id':exp_id})
            report_obj.create(val)

    @api.one
    @api.depends('exp_desc_ids','cash_flow_ids')
    def _compute_exp(self):
        income = 0
        expense = 0
        debt = 0
        for line in self.cash_flow_ids:
            income += line.amount
        for line in self.exp_desc_ids:
            if line.payment_type == 'company':
                expense += line.amount
            if line.payment_type == 'individual':
                debt += line.amount
        for line in self.cash_return_ids:
            expense += line.amount
        balance = income - expense
        self.company_income = income
        self.company_payment = expense
        self.company_debt = debt
        self.company_balance =balance
    @api.one
    def set_clear(self):
        self.state = 'clear'
    name = fields.Char(string="Enter Description")
    date = fields.Date(string="Date",default=fields.Date.context_today)
    company_income = fields.Float(string="Company Income",compute="_compute_exp")
    company_payment = fields.Float(string="Company Payment",compute="_compute_exp")
    company_balance = fields.Float(string="Company Payment",compute="_compute_exp")
    company_debt = fields.Float(string="Company Debt",compute="_compute_exp")
    exp_desc_ids = fields.One2many('expense.desc.line','exp_id',string="Expense Desc Line")
    cash_flow_ids = fields.One2many('cash.flow','exp_id',string="Expense Received Line")
    cash_return_ids = fields.One2many('cash.return','exp_id',string="Cash Return")
    report_ids = fields.One2many('cash.report','exp_id',string="Reports",readonly=True)
    state = fields.Selection([('draft','In Progress'),('clear','Cleared')],string="Status",default="draft")

class exp_type(models.Model):
    _name = "exp.type"
    name = fields.Char(string="Exp Type")
class expense_desc_line(models.Model):
    _name = "expense.desc.line"
    _order = "sequence"
    sequence = fields.Integer(string="Sequence",default=10)
    exp_id = fields.Many2one('expense.register',string='Expense Session')
    date = fields.Date(string="Date",default=fields.Date.context_today)
    name = fields.Char(string="Description")
    payment_type = fields.Selection([('company','Company'),('individual','Individual')],string="Payment Type",required=True,default="company")
    fav_id = fields.Many2one('fav.group',string="Favorite")
    participant_ids = fields.Many2many('res.partner','rel_partner_exp','exp_id','partner_id',string="Participants")
    amount = fields.Float(string="Amount")
    exp_type_id = fields.Many2one('exp.type',string="Expense Type")
    paid_by = fields.Many2one('res.partner',string="Paid By")
    @api.onchange('fav_id')
    def onchange_fav_id(self):
        if self.fav_id:
            self.participant_ids = self.fav_id.participant_ids
class cash_flow(models.Model):
    _name ="cash.flow"
    exp_id = fields.Many2one('expense.register',string='Expense Session')
    date = fields.Date(string="Date",default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner',string="Giver")
    amount = fields.Float(string="Amount")
class cash_return(models.Model):
    _inherit = "cash.flow"
    _name ="cash.return"
class cash_report(models.Model):
    _name  = "cash.report"
    @api.one
    @api.depends('exp_amount','payed_amount')
    def get_balance(self):
        self.balance = self.payed_amount - (self.exp_amount + self.return_amount)
    exp_id = fields.Many2one('expense.register',string='Expense Session')
    partner_id = fields.Many2one('res.partner',string="Partner")
    exp_amount = fields.Float(string="Expense")
    payed_amount = fields.Float(string="Payed Amount")
    return_amount = fields.Float(string="Return Amount")
    balance = fields.Float(string="Balance",compute="get_balance")
class fav_group(models.Model):
    _name = "fav.group"
    name = fields.Char(string="Group Name")
    participant_ids = fields.Many2many('res.partner','rel_fav_group_partner','group_id','partner_id')
