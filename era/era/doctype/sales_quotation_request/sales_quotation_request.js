// Copyright (c) 2026, Admin and contributors

frappe.ui.form.on("Sales Quotation Request", {
	setup(frm) {
		frm.set_query("customer_address", () => ({
			filters: {
				link_doctype: "Customer",
				link_name: frm.doc.customer || "",
			},
		}));

		frm.set_query("contact_person", () => ({
			filters: {
				link_doctype: "Customer",
				link_name: frm.doc.customer || "",
			},
		}));

		frm.set_query("selling_price_list", () => ({
			filters: { selling: 1, company: frm.doc.company || "" },
		}));
	},

	customer(frm) {
		if (!frm.doc.customer) {
			return;
		}

		frappe.db.get_value("Customer", frm.doc.customer, ["tax_id"]).then((r) => {
			if (r.message?.tax_id) {
				frm.set_value("tax_id", r.message.tax_id);
			}
		});

		frappe.call({
			method: "frappe.contacts.doctype.contact.contact.get_default_contact",
			args: { link_doctype: "Customer", link_name: frm.doc.customer },
			callback(r) {
				if (r.message) {
					frm.set_value("contact_person", r.message);
					frappe.call({
						method: "frappe.contacts.doctype.contact.contact.get_contact_details",
						args: { contact: r.message },
						callback(res) {
							if (res.message) {
								frm.set_value("contact_mobile", res.message.mobile_no || res.message.phone);
								frm.set_value("contact_email", res.message.email_id);
							}
						},
					});
				}
			},
		});
	},

	refresh(frm) {
		if (frm.doc.docstatus !== 1 || frm.doc.quotation_created) {
			if (frm.doc.quotation) {
				frm.add_custom_button(__("View Quotation"), () => {
					frappe.set_route("Form", "Quotation", frm.doc.quotation);
				});
			}
			return;
		}

		frm.add_custom_button(__("Create Quotation"), () => {
			frappe.model.open_mapped_doc({
				method: "era.era.doctype.sales_quotation_request.sales_quotation_request.make_quotation",
				frm,
				run_link_triggers: true,
			});
		}, __("Create"));
	},
});

frappe.ui.form.on("Sales Quotation Request Item", {
	item_code(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.item_code) {
			return;
		}

		frappe.db.get_value("Item", row.item_code, ["item_name", "stock_uom", "description"]).then((r) => {
			if (!r.message) {
				return;
			}
			frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
			frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
			if (!row.description) {
				frappe.model.set_value(cdt, cdn, "description", r.message.description);
			}
		});
	},

	qty(frm, cdt, cdn) {
		calculate_amount(cdt, cdn);
	},

	rate(frm, cdt, cdn) {
		calculate_amount(cdt, cdn);
	},
});

function calculate_amount(cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.rate));
}
