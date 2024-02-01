# -*- coding: utf-8 -*-
# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Make render method public again",
    'summary': 
        """
        Patch 
        https://github.com/odoo/odoo/issues/78528
        """,
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    'description': 
    """
        
    """,

    'author': "Mind And Go",
    'website': "https://www.mind-and-go.com",
    'category': 'Delivery',

    # any module necessary for this one to work correctly
    'depends': [
            'base',
            ],

    # always loaded
    'data': [
        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
	
	'css' : [],
	"test": [],
	"installable": True,
	"auto_install": False,
}
