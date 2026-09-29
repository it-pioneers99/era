# Copyright (c) 2026, Admin and contributors

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate


class SalesQuotationRequest(Document):
	def validate(self):
		self.validate_items()
		self.validate_dates()
		if not self.status:
			self.status = "Draft"

	def validate_items(self):
		if not self.items:
			frappe.throw(_("Please add at least one item"))

		for row in self.items:
			if flt(row.qty) <= 0:
				frappe.throw(_("Quantity must be greater than zero in row {0}").format(row.idx))
			row.amount = flt(row.qty) * flt(row.rate or 0)

	def validate_dates(self):
		if self.valid_till and getdate(self.valid_till) < getdate(self.transaction_date):
			frappe.throw(_("Valid Till cannot be before Request Date"))

	def on_submit(self):
		self.db_set("status", "Approved", update_modified=False)

	def on_cancel(self):
		self.db_set("status", "Cancelled", update_modified=False)


@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.quotation_to = "Customer"
		target.party_name = source.customer
		target.customer_name = source.customer_name
		if source.selling_price_list:
			target.selling_price_list = source.selling_price_list
		if source.currency:
			target.currency = source.currency
		if source.valid_till:
			target.valid_till = source.valid_till
		if source.terms:
			target.terms = source.terms
		target.sales_quotation_request = source.name

	def postprocess(source, target):
		set_missing_values(source, target)

	doc = get_mapped_doc(
		"Sales Quotation Request",
		source_name,
		{
			"Sales Quotation Request": {
				"doctype": "Quotation",
				"validation": {"docstatus": ["=", 1]},
				"field_map": [
					["company", "company"],
					["transaction_date", "transaction_date"],
					["valid_till", "valid_till"],
					["selling_price_list", "selling_price_list"],
					["currency", "currency"],
					["terms", "terms"],
				],
			},
			"Sales Quotation Request Item": {
				"doctype": "Quotation Item",
				"field_map": [
					["item_code", "item_code"],
					["item_name", "item_name"],
					["description", "description"],
					["qty", "qty"],
					["uom", "uom"],
					["rate", "rate"],
				],
			},
		},
		target_doc,
		postprocess,
	)

	set_missing_values(frappe.get_doc("Sales Quotation Request", source_name), doc)
	return doc


def link_quotation_to_request(doc, method=None):
	if not doc.get("sales_quotation_request"):
		return

	frappe.db.set_value(
		"Sales Quotation Request",
		doc.sales_quotation_request,
		{
			"quotation": doc.name,
			"quotation_created": 1,
			"status": "Quotation Created",
		},
		update_modified=False,
	)
