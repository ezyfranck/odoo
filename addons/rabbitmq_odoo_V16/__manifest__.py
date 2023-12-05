# -*- coding: utf-8 -*-
{
    'name': "RabbitMQ Odoo V16 automated for Stock Picking",

    'summary': """RabbitMq play by Ezytail.""",

    'description': """
        RabbitMq play for stock picking for Ezyflow.
    """,

    'author': "Ezytail",
    'website': "https://ezytail.com",

    'category': 'Technical',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','base_automation'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/parameters.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}