# -*- coding: utf-8 -*-
{
    "name": "Online Courses",
    "summary": """
        Manage online courses, teachers, and students.""",
    "description": """
        A simple module to manage online courses.
    """,
    "author": "Adam Mitrenga",
    "website": "https://www.vilgain.cz",
    "category": "Education",
    "version": "18.0.1.0.0",
    'license': 'LGPL-3',
    "depends": ["base"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "views/course_views.xml",
        "views/res_users_views.xml",
        "views/menus.xml",
    ],
    "demo": [
        "demo/users_demo.xml",
        "demo/course_demo.xml",
    ],
    "installable": True,
    "application": True,
}
