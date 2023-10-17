# -*- coding: utf-8 -*-
import json
import logging
from datetime import date
from werkzeug.wrappers import Response
from odoo import http
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class EstateController(http.Controller):
    route = "/estate/properties"

    @http.route(route, auth="public", type="http", sitemap=False, methods=["GET"])
    def get_estate_properties(self, **kw):
        # Get query parameters from the request
        domain = safe_eval(kw.get("domain", "[]"))
        offset = int(kw.get("offset", 0))
        limit = int(kw.get("limit", 10))
        order = kw.get("order", "id")  # Default sorting by ID

        try:
            # Perform a search with the specified parameters
            estate_properties = http.request.env["estate.property"].search_read(
                domain,
                fields=list(http.request.env["estate.property"]._fields),
                offset=offset,
                limit=limit,
                order=order,
            )
            properties_data = []

            for property in estate_properties:
                property_data = {}
                for field_name, field_value in property.items():
                    if isinstance(field_name, str):
                        # Convert datetime.date to ISO string
                        if isinstance(field_value, date):
                            field_value = field_value.strftime("%Y-%m-%d")  # ISO format

                        # Handle custom serialization for estate.property.type objects (tuple)
                        if field_name == "property_type_id":
                            field_value = field_value[1] if field_value else None

                        property_data[field_name] = field_value

                # Include property type, JSON key names must be camel-cased, ASCII strings.
                property_data["propertyType"] = (
                    property["property_type_id"]
                    and property["property_type_id"][1]
                    or None
                )

                # Handle custom serialization for create_uid and write_uid (tuple)
                create_uid = property["create_uid"]
                write_uid = property["write_uid"]
                property_data["create_uid"] = create_uid and create_uid[1] or None
                property_data["write_uid"] = write_uid and write_uid[1] or None

                properties_data.append(property_data)

            # Log estate_properties
            _logger.info("Estate Properties API: %s", self.route)
            for property in estate_properties:
                _logger.info(
                    "Property ID: %s, Name: %s, Price: %s",
                    property["id"],
                    property["name"],
                    property["expected_price"],
                )

            _logger.info("Estate Properties data: %s", properties_data)

            response_data = json.dumps(properties_data, ensure_ascii=False)
            return Response(
                response=response_data, content_type="application/json", status=200
            )

        except Exception as e:
            error_response = {"error": str(e)}
            _logger.error(f"Error at {self.route}: {e}")
            return Response(
                response=json.dumps(error_response),
                content_type="application/json",
                status=500,
            )
