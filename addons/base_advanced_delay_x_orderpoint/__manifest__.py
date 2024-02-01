# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base module for advanced delays",
    "summary": "Delay fields",
    "version": "16.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Tools",
    "website": "https://mind-and-go.com",
    "author": "<Florent THOMAS>, Mind And Go (M&Go)",
    "maintainers": ["flotho"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "stock",
        "base_advanced_delay",
    ],
    "data": [
        "views/orderpoint.xml",
    ],
    "demo": [],
    "qweb": [],
}
