# -*- coding: utf-8 -*-
# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "mapping mr_relay_number (dropoff_site version)",
    'summary': 
        """
        Logistics improvements
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    'description': 
    """
    """,

    'author': "Mind And Go",
    'website': "https://www.mind-and-go.com",
    'category': 'Custom Modules',

    # any module necessary for this one to work correctly
    'depends': [
            'logistics_improvements',
            'connector_prestashop',
            'delivery_dropoff_site'
            ],

    # always loaded
    'data': [

    ],
    'demo': [
       
    ],
	
	'css' : [],
	"test": [],
	"installable": True,
	"auto_install": False,
}
