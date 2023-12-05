{
    'name':'Module Test',  # nom qui apparaitra dans odoo applications
    'version':'1.0',
    'category':'Sales',    # catégorie ou apparaitra name
    'summary':'Gestion immobilière',  # texte pour résumé dans info du module
    'description': "Un module pour tester la création de nouveau module",
    'depends':['base'],
    'data':['security/ir.model.access.csv',
            'views/estate_property_offer_views.xml',
            'views/module_test_property_views.xml',
            'views/estate_property_type_views.xml',
            'views/estate_property_tag_views.xml',
            'views/modele_test_menu.xml',    
    ],
    'application':True,
    'installable':True
}