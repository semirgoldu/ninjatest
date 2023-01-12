# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields

class Product(models.Model):
	_inherit = 'product.template'

	product_size_id = fields.Many2one('product.size.chart', string="Product Size Chart")

class ProductSizeChart(models.Model):
	_name  = 'product.size.chart'
	_rec_name = 'chart_name'
	_description = 'Product Size Chart'

	chart_name = fields.Char(string = "Chart Name")
	row = fields.Integer(string = "Value")
	column = fields.Integer(string = "Header")
	product_image_1920= fields.Binary('')
	link_text = fields.Char(string="Link Text")
	size_chart = fields.Html('Size Chart')
	measurement = fields.Html('How To Measure')

	@api.onchange('row','column')
	def onchange_size_chart(self):
		for obj in self:
			t1 = "<table class='table table-striped'>"
			t2 = ""
			t3 = "</table>"
			body_final = ""
			for row in range(obj.row):
				tr1 = "<tr>"
				tr2 = ""
				tr3 = "</tr>"
				for col in range(obj.column):
					tr2 += "<th>Demo</th>"
				h = tr1+tr2+tr3
				body_final = h

			body_str = ""
			for row in range(obj.row):
				r1 = "<tr>"
				r2 = ""
				r3 = "</tr>"
				for col in range(obj.column):
					r2 += "<td>Test</td>"
				r = r1+r2+r3
				body_str += r

			t2 = t1 + body_final + body_str +t3
			obj.size_chart = t2
