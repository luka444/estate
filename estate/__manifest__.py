{
    'name': 'Real Estate',
    'author': 'odoo mate',
    'category': 'Real Estate/Brokerage',
    'depends' : ['base'],
    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',

    ],
    
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
