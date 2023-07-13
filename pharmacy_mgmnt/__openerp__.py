# -*- coding: utf-8 -*-
##############################################################################

##############################################################################
{
    'name': "Pharmacy Management",
    'version': '10.0.1.1.1',
    'summary': """Pharmacy Management and Customer/Supplier Invoice""",
    'description': """This Module for Pharmacy Management and it Enables To Create Stocks Picking From Customer/Supplier Invoice""",
    'author': "Hiworth Solutions",
    'company': 'Hiworth Solutions',
    'website': "https://www.hiworthsolutions.com",
    'category': 'Accounting',
    'depends': ['base', 'account', 'stock', 'purchase', 'sale',
                'report_xlsx',
                'account_accountant', 'product_expiry', 'product_expiry_simple', 'Key_shortcuts',],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/menu.xml',
        'views/rack_transfer.xml',
        'views/partial_transfer.xml',
        'views/credit_limit.xml',
        'views/invoice_history.xml',
        'views/invoice_stock_move_view.xml',
        'views/product.xml',
        'views/invoice.xml',
        'views/stockpicking.xml',
        'views/master_menu.xml',
        'expiry_manage/expiry_manage_view.xml',
        'report/customer_inv_report.xml',
        'report/supplier_inv_report.xml',
        'report/pending_invoice_report.xml',
        'report/customer_inv_history.xml',
        'report/supplier_inv_history.xml',
        'report/purchase_report.xml',
        'report/tax_report_excel_to_pdf.xml',

        'report/inherit_supplier_invoice_report.xml',

        'report/packing_holding_history.xml',
        'report/tax_report_view.xml',
        'report/tax_report_excel.xml',
        'views/account_invoice_view.xml',
        'views/invoice_report.xml',

    ],
    'qweb': [
        "static/src/css/template.xml",
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
