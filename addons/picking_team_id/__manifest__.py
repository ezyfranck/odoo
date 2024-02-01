# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale team in stock picking",
    "summary": "team",
    "version": "14.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Tools",
    "website": "https://mind-and-go.com",
    "author": "[Mind And Go] (M&Go) : Torrecillas Gaël",
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
        "sale","crm"
    ],
    "data": [
        "views/picking.xml",
    ],
    "demo": [],
    "qweb": [],
}
