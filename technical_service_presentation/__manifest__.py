# -*- coding: utf-8 -*-
{
    'name': "Technical Service Presentation",

    'summary': """
        Presentation and Security Layer for Technical Service Management
    """,

    'description': """
        Technical Service Presentation Module
        ======================================
        This module provides:
        - Role-based access control
        - Custom menu structures per role
        - Security groups and record rules
        - Domain filters for different user types

        Roles Supported:
        ----------------
        1. HR-based Roles:
           - Standard User (base.group_user)
           - Department Manager (hr.group_hr_manager)

        2. Technical Organization Roles:
           - CTO/Technical Director
           - Department Manager (IT, Facility, etc.)
           - Team Leader
           - Senior Technician
           - Technician
           - Dispatcher
           - Location Manager
           - Inventory Manager

        3. Special Roles:
           - External User (Customer/Partner)
    """,

    'author': "Technical Service Team",
    'website': "https://www.example.com",
    'category': 'Services/Security',
    'version': '18.0.1.0.0',

    # Dependencies
    'depends': [
        'technical_service',  # Core module
        'hr',                 # For HR-based roles
        'portal',            # For external users
    ],

    # Data files
    'data': [
        'security/technical_service_presentation_groups.xml',
        'security/technical_service_presentation_rules.xml',
        'security/ir.model.access.csv',
        'views/menu_structure.xml',
        'data/admin_permissions.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}