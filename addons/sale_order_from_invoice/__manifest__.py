# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order from Invoice",
    "summary": "Go to sale orders associated to the current invoice",
    "version": "16.0.1.0.1",
    "category": "Uncategorized",
    "website": "https://mind-and-go.com/",
    "author": "Florent THOMAS",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale",
        "account"
        
    ],
    "data": [   
        "views/account_views.xml",
        
    ],
    "demo": [
        
    ],
    "qweb": [

    ]
}
