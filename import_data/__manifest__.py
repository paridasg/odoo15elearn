# -*- coding: utf-8 -*-
{
    "name": "Import Data from Excel",
    "summary": "Import Data from Excel",
    "description": """
      Import Questions and answers in E-Learning
    """,
    'author': "Wabsol",
    'website': "https://www.wabsol.com/",
    "license": "OPL-1",
    'version': '15.1',
    "depends": [
        "base", "website_slides_survey",
    ],
    "data": [
        "security/ir.model.access.csv",

        "wizards/data_import_view.xml",
        "views/survey_survey_views.xml",
    ],

    "application": True,
    "installable": True,
    "auto_install": False,
}
