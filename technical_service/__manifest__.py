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
        'security/technical_service_security.xml',  # Security groups for organization
        'security/ir.model.access.csv',
        'security/record_rules.xml',  # Task 07 Phase 6B: Record rules for visibility
        'data/sequence_data.xml',
        'data/technical_service_stages.xml',  # Task 07: Service request stages
        'data/root_team_data.xml',  # Task 06: Root team for hierarchy
        'views/technical_service_actions.xml',  # Load actions first
        'views/menu_actions.xml',  # Additional menu actions
        'views/missing_actions.xml',  # Missing actions for complete menu structure
        'views/placeholder_views.xml',  # Placeholder views for development in progress
        'views/technical_service_request_views.xml',
        'views/technical_service_work_order_views.xml',
        'views/technical_service_asset_views.xml',
        'views/technical_service_location_views.xml',
        'views/technical_service_sla_views.xml',
        'views/technical_service_team_views.xml',  # Team hierarchy views
        'views/technical_service_team_hierarchy.xml',  # Task 06: Org hierarchy
        'views/technical_service_preventive_views.xml',  # Add preventive maintenance views
        'views/technical_service_organization_views.xml',  # Technical organization views
        'views/wizard_views.xml',  # Task 07: Wizard views for manual actions
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

    # Assets - Temporarily disabled JS files for debugging
    'assets': {
        'web.assets_backend': [
            'technical_service/static/src/scss/technical_service.scss',
            'technical_service/static/src/scss/form_buttons.scss',
            # 'technical_service/static/src/js/dashboard_widget.js',
            # 'technical_service/static/src/js/form_buttons.js',
            # 'technical_service/static/src/xml/dashboard_templates.xml',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

