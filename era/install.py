import frappe


def after_install():
	from era.patches.setup_quotation_custom_field import execute

	execute()
