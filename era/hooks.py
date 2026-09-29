app_name = "era"
app_title = "Era"
app_publisher = "Admin"
app_description = "Sales quotation request"
app_email = "admin@test.com"
app_license = "mit"

required_apps = ["erpnext"]

after_install = "era.install.after_install"

doctype_js = {
	"Sales Quotation Request": "era/doctype/sales_quotation_request/sales_quotation_request.js",
}

doc_events = {
	"Quotation": {
		"after_insert": "era.era.doctype.sales_quotation_request.sales_quotation_request.link_quotation_to_request",
	},
}
