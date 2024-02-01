# ODOO V16 - API ezyConnect
{
    'name' : 'API EzyConnect Odoo V16',
    'version': '1.0',
    'category': 'Technical',
    'summary':'API EZYConnect',  # texte pour résumé dans info du module
    'description': "Un module pour tester l'API EZYConnect",
    'depends' : ['base', 'product', 'purchase', 'stock'],
    'data': ['security/ir.model.access.csv',
             'views/product_view.xml',
             'views/get_product_menu.xml',
             ],
    'application': True,
    'installable': True,
}