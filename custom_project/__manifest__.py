# -*- coding: utf-8 -*-
{
    'name': "custom_project",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/project_task.xml',
        'views/project_purchase_order.xml',
        'views/brand.xml',
        'views/buyer_party.xml',
        'security/security.xml',

    ],
    'installable': True,
    'application': False,
}

