# -*- coding: utf-8 -*-
{
    'name': "Technical Service Management",

    'summary': """
        Comprehensive Technical Service and IT Help Desk Management System
    """,

    'description': """
        Technical Service Management System for handling:
        - General Technical Service (mechanical, electrical, facility, equipment)
        - IT Support (hardware, network, software, user support)
        - Service requests and incident management
        - Work order management
        - Asset tracking and maintenance
        - SLA management and escalation
        - Stock and spare parts management

        Inherited from:
        - maintenance: For maintenance request management
        - project: For work order and task management
        - stock: For spare parts inventory
        - mail: For communication and notifications
        - hr: For technician management
    """,

    'author': "Technical Service Team",
    'website': "https://www.example.com",
    'category': 'Services/Field Service',
    'version': '18.0.1.0.0',

    # Dependencies - Using standard Odoo modules for inheritance
    'depends': [
        'base',
        'mail',
        'maintenance',
        'project',
        'stock',
        'hr',
        'product',
        'portal',
    ],

    # Data files
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/technical_service_actions.xml',  # Load actions first
        'views/technical_service_request_views.xml',
        'views/technical_service_work_order_views.xml',
        'views/technical_service_asset_views.xml',
        'views/technical_service_location_views.xml',
        'views/technical_service_sla_views.xml',
        'views/technical_service_dashboard.xml',
        'views/technical_service_reports.xml',
        'views/technical_service_menu.xml',  # Menu definitions must be loaded first
        'views/res_config_settings_views.xml',  # Settings configuration (after menu)
        'views/technical_service_menu_override.xml',  # Override maintenance module menus
    ],

    # Demo data
    'demo': [
        # 'demo/technical_service_demo.xml',
    ],

    # Assets
    'assets': {
        'web.assets_backend': [
            'technical_service/static/src/scss/technical_service.scss',
            'technical_service/static/src/scss/form_buttons.scss',
            'technical_service/static/src/js/dashboard_widget.js',
            'technical_service/static/src/js/form_buttons.js',
            'technical_service/static/src/xml/dashboard_templates.xml',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

