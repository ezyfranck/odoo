{
    'name':'Module Test',  # nom qui apparaitra dans odoo
    'version':'1.0',
    'category':'Sales',    # catégorie ou apparaitra name
    'summary':'Un module de test',  # texte pour résumé dans info du module
    'description': "Un module pour tester la création de nouveau module",
    'depends':['base'],
    'data':['security/ir.model.access.csv',
            'views/module_test_property_views.xml',
            'data/module_test_property.xml'],
    'application':True,
    'installable':True
}