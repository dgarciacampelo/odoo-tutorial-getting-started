# -*- coding: utf-8 -*-

from odoo import fields, models  # api import not required
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    def get_availability_date(self, default_months: int = 3):
        # Ensure default_months is an integer
        months = int(default_months)
        return fields.Datetime.now() + relativedelta(months=months)

    _name = "estate.property"
    _description = "Real Estate Property"

    name = fields.Char("Title", required=True, translate=True)

    # Reserved field. Toggles the global visibility of the record.
    active = fields.Boolean("Active", default=True)

    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "", copy=False, default=lambda self: self.get_availability_date()
    )
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", copy=False, readonly=True)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden Area (sqm)")

    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        help="Type is used to set the garden orientation",
    )

    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        string="State",
        required=True,
        copy=False,
        default="new",
    )

    # Text moved to web-view bottom.
    # Better to use a form view for proper customization.
    description = fields.Text("Description")

    # New many to one field for property type:
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"

    name = fields.Char("Title", required=True, translate=True)
