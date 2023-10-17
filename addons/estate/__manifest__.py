# -*- coding: utf-8 -*-
{
    'name': "Real Estate",
    'summary': "Odoo Tutorials, Getting started",
    'description': "Module to cover a business area not included in the standard set of modules: real estate.",
    'author': "My Test Company",
    'website': "https://www.dagarcam.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Real Estate',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        #'security/estate_security.xml',
        'security/ir.model.access.csv',
        
        'data/ir_action_data.xml',
        
        'views/estate_property_menu_views.xml',
        
        'views/estate_property_views.xml',
        #'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    #'demo': ['demo/demo.xml',],
    
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
