import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"Quotation": [
				{
					"fieldname": "sales_quotation_request",
					"label": "Sales Quotation Request",
					"fieldtype": "Link",
					"options": "Sales Quotation Request",
					"insert_after": "party_name",
					"read_only": 1,
					"no_copy": 1,
				}
			]
		}
	)
	frappe.clear_cache(doctype="Quotation")
