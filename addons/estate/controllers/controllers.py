# -*- coding: utf-8 -*-
import json
import logging
from datetime import date
from werkzeug.wrappers import Response
from odoo import http
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


# TODO: Setup permissions for the API endpoints, using security/ir.model.access.csv:
# ? access_estate_property,estate.property,model_estate_property,base.group_user,1,1,1,1


class EstateController(http.Controller):
    # HTTP request routes definition
    get_route = "/estate/properties"
    post_route = "/estate/properties/create"

    @http.route(get_route, auth="public", type="http", sitemap=False, methods=["GET"])
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
            _logger.info("Estate Properties data: %s", properties_data)

            response_data = json.dumps(properties_data, ensure_ascii=False)
            return Response(
                response=response_data, content_type="application/json", status=200
            )

        except Exception as e:
            error_response = {"error": str(e)}
            _logger.error(f"Error at {self.get_route}: {e}")
            return Response(
                response=json.dumps(error_response),
                content_type="application/json",
                status=500,
            )

    @http.route(post_route, auth="public", type="json", methods=["POST"])
    def create_estate_property(self, **kw):
        request_json_data = json.loads(http.request.httprequest.data)
        request_data = request_json_data.get("data", {})
        _logger.info(f"Create Estate Property parameters: {request_data}")

        if not request_data:
            error_response = {"error": "No data provided in the request."}
            return Response(
                response=json.dumps(error_response),
                content_type="application/json",
                status=400,  # Bad Request status code
            )

        # Extract the property details from the request
        property_name = request_data.get("name", "")
        property_type_name = request_data.get("propertyTypeName", "Unspecified")
        post_code = request_data.get("postCode", "")
        bedrooms = request_data.get("bedrooms", None)  # Default model value is 2
        living_area = request_data.get("livingArea", None)
        expected_price = request_data.get("expectedPrice", 0)

        # Find the property type by name
        property_type = http.request.env["estate.property.type"].search(
            [("name", "=", property_type_name)], limit=1
        )

        if not property_type:
            error_response = {
                "error": f"Property type '{property_type_name}' not found."
            }
            return Response(
                response=json.dumps(error_response),
                content_type="application/json",
                status=404,  # Not Found status code
            )

        # Create a new estate property, using a dictionary
        fields = {
            "active": True,
            "name": property_name,
            "property_type_id": property_type.id,
            "postcode": post_code,
            "expected_price": expected_price,
        }
        # Add fields with default model values, if provided
        if bedrooms:
            fields["bedrooms"] = bedrooms
        if living_area:
            fields["living_area"] = living_area

        estate_property = http.request.env["estate.property"].create(fields)

        if estate_property:
            success_response = {
                "success": f"Estate property '{property_name}' created with ID {estate_property.id}"
            }
            return Response(
                response=json.dumps(success_response),
                content_type="application/json",
                status=201,  # Created status code
            )
        else:
            error_response = {"error": "Failed to create the estate property."}
            return Response(
                response=json.dumps(error_response),
                content_type="application/json",
                status=500,  # Internal Server Error status code
            )
