"""
Smart Router Tool

This module provides a unified MCP tool that routes queries to the appropriate
application-specific tools for Instana monitoring.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from mcp.types import ToolAnnotations

from src.core.utils import BaseInstanaClient, register_as_tool

logger = logging.getLogger(__name__)


class SmartRouterMCPTool(BaseInstanaClient):
    """
    Smart router that routes queries to Application Metrics, Alert Configuration, and Catalog tools.
    The LLM agent determines the appropriate operation based on query understanding.
    """

    def __init__(self, read_token: str, base_url: str):
        """Initialize the Smart Router MCP tool."""
        super().__init__(read_token=read_token, base_url=base_url)

        # Initialize the application tool clients
        from src.application.application_alert_config import ApplicationAlertMCPTools
        from src.application.application_call_group import ApplicationCallGroupMCPTools
        from src.application.application_catalog import ApplicationCatalogMCPTools
        from src.application.application_global_alert_config import (
            ApplicationGlobalAlertMCPTools,
        )
        from src.application.application_resources import ApplicationResourcesMCPTools
        from src.application.application_settings import ApplicationSettingsMCPTools

        self.app_call_group_client = ApplicationCallGroupMCPTools(read_token, base_url)
        self.app_alert_config_client = ApplicationAlertMCPTools(read_token, base_url)
        self.app_global_alert_config_client = ApplicationGlobalAlertMCPTools(read_token, base_url)
        self.app_resources_client = ApplicationResourcesMCPTools(read_token, base_url)
        self.app_settings_client = ApplicationSettingsMCPTools(read_token, base_url)
        self.app_catalog_client = ApplicationCatalogMCPTools(read_token, base_url)

        logger.info("Smart Router initialized with Application tools")

    @register_as_tool(
        title="Manage Instana Application Resources",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False)
    )
    async def manage_applications(
        self,
        resource_type: str,
        operation: str,
        # Flat parameters for Watson Orchestrate compatibility - ALL AS STRINGS
        # Settings parameters (for create application)
        imap: Optional[str] = None,
        label: Optional[str] = None,
        scope: Optional[str] = None,
        boundary_scope: Optional[str] = None,
        access_rules: Optional[str] = None,
        tag_filter_expression: Optional[str] = None,
        # Common parameters
        resource_subtype: Optional[str] = None,
        id: Optional[str] = None,
        application_id: Optional[str] = None,
        application_name: Optional[str] = None,
        payload: Optional[str] = None,
        request_body: Optional[str] = None,
        # Alert config parameters
        alert_ids: Optional[str] = None,
        valid_on: Optional[str] = None,
        created: Optional[str] = None,
        # Metrics parameters
        query: Optional[str] = None,
        time_frame: Optional[str] = None,
        metrics: Optional[str] = None,
        group: Optional[str] = None,
        order: Optional[str] = None,
        pagination: Optional[str] = None,
        include_internal: Optional[str] = None,
        include_synthetic: Optional[str] = None,
        # Catalog parameters
        use_case: Optional[str] = None,
        data_source: Optional[str] = None,
        var_from: Optional[str] = None,
        ctx=None
    ) -> Dict[str, Any]:
        """
        Unified Instana application resource manager for metrics, alerts, configurations, and catalog.

        ALL PARAMETERS ARE FLAT STRINGS - No nested objects required!

        Resource Types:
        - "metrics": Query application metrics, services, and endpoints
        - "alert_config": Manage application-specific alert configurations
        - "global_alert_config": Manage global application alert configurations
        - "settings": Manage application perspectives, endpoints, services, manual services
        - "catalog": Access application tag and metric catalog information

        METRICS (resource_type="metrics"):
            operation: "application"
            Parameters (all strings): query, time_frame, metrics, tag_filter_expression, group, order, pagination, include_internal, include_synthetic

        ALERT_CONFIG (resource_type="alert_config"):
            operations: find_active, find_versions, find, create, update, delete, enable, disable, restore, update_baseline
            Parameters (all strings): application_id OR application_name, id, alert_ids, valid_on, created, payload

        GLOBAL_ALERT_CONFIG (resource_type="global_alert_config"):
            operations: find_active, find_versions, find, create, update, delete, enable, disable, restore
            Parameters (all strings): application_id OR application_name, id, alert_ids, valid_on, created, payload

        SETTINGS (resource_type="settings"):
            operations: get_all, get, create, update, delete, order, replace_all
            Parameters (all strings): resource_subtype, id, application_name, imap, label, scope, boundary_scope, access_rules, tag_filter_expression, payload, request_body

            resource_subtypes: "application", "endpoint", "service", "manual_service"

            Creating application perspectives (resource_subtype="application", operation="create"):
            - REQUIRED: imap (IMAP identifier string, e.g., "EAL-012471")
            - REQUIRED: label (application name string, MUST start with IMAP, e.g., "EAL-012471_MyApp")
            - OPTIONAL: scope (string, default: "INCLUDE_ALL_DOWNSTREAM")
            - OPTIONAL: boundary_scope (string, default: "ALL")
            - OPTIONAL: access_rules (JSON string, default: '[{"accessType": "READ_WRITE", "relationType": "GLOBAL"}]')

        CATALOG (resource_type="catalog"):
            operations: get_tag_catalog, get_metric_catalog
            Parameters (all strings): use_case, data_source, var_from

        Args:
            resource_type: "metrics", "alert_config", "global_alert_config", "settings", or "catalog"
            operation: Specific operation for the resource type
            All other parameters are optional strings, operation-specific
            ctx: MCP context (internal)

        Returns:
            Dictionary with results from the appropriate tool

        Examples:
            # Create application perspective (flat parameters)
            resource_type="settings", operation="create",
            resource_subtype="application", imap="EAL-012471", label="EAL-012471_MyApp"

            # Find active alerts by name
            resource_type="alert_config", operation="find_active", application_name="All Services"

            # Get application config by name
            resource_type="settings", operation="get", resource_subtype="application", application_name="MCP_TEST_DEMO"

            # Get application tag catalog
            resource_type="catalog", operation="get_tag_catalog", use_case="GROUPING", data_source="CALLS"
        """
        try:
            logger.info(f"Smart Router received: resource_type={resource_type}, operation={operation}")

            # Build params dict from flat parameters
            params = {}
            if imap is not None:
                params['imap'] = imap
            if label is not None:
                params['label'] = label
            if scope is not None:
                params['scope'] = scope
            if boundary_scope is not None:
                params['boundary_scope'] = boundary_scope
            if access_rules is not None:
                params['access_rules'] = access_rules
            if tag_filter_expression is not None:
                params['tag_filter_expression'] = tag_filter_expression
            if resource_subtype is not None:
                params['resource_subtype'] = resource_subtype
            if id is not None:
                params['id'] = id
            if application_id is not None:
                params['application_id'] = application_id
            if application_name is not None:
                params['application_name'] = application_name
            if payload is not None:
                params['payload'] = payload
            if request_body is not None:
                params['request_body'] = request_body
            if alert_ids is not None:
                params['alert_ids'] = alert_ids
            if valid_on is not None:
                params['valid_on'] = valid_on
            if created is not None:
                params['created'] = created
            if query is not None:
                params['query'] = query
            if time_frame is not None:
                params['time_frame'] = time_frame
            if metrics is not None:
                params['metrics'] = metrics
            if group is not None:
                params['group'] = group
            if order is not None:
                params['order'] = order
            if pagination is not None:
                params['pagination'] = pagination
            if include_internal is not None:
                params['include_internal'] = include_internal
            if include_synthetic is not None:
                params['include_synthetic'] = include_synthetic
            if use_case is not None:
                params['use_case'] = use_case
            if data_source is not None:
                params['data_source'] = data_source
            if var_from is not None:
                params['var_from'] = var_from

            # Validate resource_type
            if resource_type not in ["metrics", "alert_config", "global_alert_config", "settings", "catalog"]:
                return {
                    "error": f"Invalid resource_type '{resource_type}'. Must be 'metrics', 'alert_config', 'global_alert_config', 'settings', or 'catalog'",
                    "suggestion": "Choose 'metrics' for querying data, 'alert_config' for application-specific alerts, 'global_alert_config' for global alerts, 'settings' for application perspective configurations, or 'catalog' for tag and metric catalog information"
                }

            # Route to the appropriate resource handler
            if resource_type == "metrics":
                return await self._handle_metrics(operation, params, ctx)
            elif resource_type == "alert_config":
                return await self._handle_alert_config(operation, params, ctx)
            elif resource_type == "global_alert_config":
                return await self._handle_global_alert_config(operation, params, ctx)
            elif resource_type == "settings":
                return await self._handle_settings(operation, params, ctx)
            elif resource_type == "catalog":
                return await self._handle_catalog(operation, params, ctx)
            else:
                return {
                    "error": f"Unsupported resource_type: {resource_type}",
                    "supported_types": ["metrics", "alert_config", "global_alert_config", "settings", "catalog"]
                }

        except Exception as e:
            logger.error(f"Error in smart router: {e}", exc_info=True)
            return {
                "error": f"Smart router error: {e!s}",
                "resource_type": resource_type,
                "operation": operation
            }

    async def _handle_metrics(
        self,
        operation: str,
        params: Dict[str, Any],
        ctx
    ) -> Dict[str, Any]:
        """Handle application metrics queries."""
        if operation != "application":
            return {
                "error": f"Invalid operation '{operation}' for metrics. Only 'application' is supported.",
                "valid_operations": ["application"]
            }

        # Extract parameters
        query = params.get("query", "")
        time_frame = params.get("time_frame")
        metrics = params.get("metrics")
        tag_filter_expression = params.get("tag_filter_expression")
        group = params.get("group")
        order = params.get("order")
        pagination = params.get("pagination")
        include_internal = params.get("include_internal")
        include_synthetic = params.get("include_synthetic")

        # Route to Application Call Group Metrics
        logger.info("Routing to Application Call Group Metrics")

        result = await self.app_call_group_client.get_grouped_calls_metrics(
            metrics=metrics,
            time_frame=time_frame,
            group=group,
            tag_filter_expression=tag_filter_expression,
            include_internal=include_internal,
            include_synthetic=include_synthetic,
            order=order,
            pagination=pagination,
            ctx=ctx
        )

        return {
            "resource_type": "metrics",
            "technology": "application",
            "query": query,
            "results": result
        }

    async def _handle_alert_config(
        self,
        operation: str,
        params: Dict[str, Any],
        ctx
    ) -> Dict[str, Any]:
        """Handle Application Alert Config operations."""
        valid_operations = [
            "find_active", "find_versions", "find", "create", "update",
            "delete", "enable", "disable", "restore", "update_baseline"
        ]

        if operation not in valid_operations:
            return {
                "error": f"Invalid operation '{operation}' for alert_config",
                "valid_operations": valid_operations
            }

        # Extract parameters
        application_id = params.get("application_id")
        application_name = params.get("application_name")
        id = params.get("id")
        alert_ids = params.get("alert_ids")
        valid_on = params.get("valid_on")
        created = params.get("created")
        payload = params.get("payload")

        # If application_name is provided but not application_id, resolve it
        if application_name and not application_id:
            logger.info(f"Resolving application name '{application_name}' to application ID")
            app_id_result = await self._get_application_id_by_name(application_name, ctx)

            if "error" in app_id_result:
                return {
                    "resource_type": "alert_config",
                    "operation": operation,
                    "error": f"Failed to resolve application name '{application_name}': {app_id_result['error']}"
                }

            application_id = app_id_result.get("application_id")
            logger.info(f"Resolved application '{application_name}' to ID: {application_id}")

        # Route to the alert config client
        result = await self.app_alert_config_client.execute_alert_config_operation(
            operation=operation,
            application_id=application_id,
            id=id,
            alert_ids=alert_ids,
            valid_on=valid_on,
            created=created,
            payload=payload,
            ctx=ctx
        )

        return {
            "resource_type": "alert_config",
            "operation": operation,
            "application_name": application_name,
            "application_id": application_id,
            "results": result
        }

    async def _handle_global_alert_config(
        self,
        operation: str,
        params: Dict[str, Any],
        ctx
    ) -> Dict[str, Any]:
        """Handle Global Application Alert Config operations."""
        valid_operations = [
            "find_active", "find_versions", "find", "create", "update",
            "delete", "enable", "disable", "restore"
        ]

        if operation not in valid_operations:
            return {
                "error": f"Invalid operation '{operation}' for global_alert_config",
                "valid_operations": valid_operations
            }

        # Extract parameters
        application_id = params.get("application_id")
        application_name = params.get("application_name")
        id = params.get("id")
        alert_ids = params.get("alert_ids")
        valid_on = params.get("valid_on")
        created = params.get("created")
        payload = params.get("payload")

        # If application_name is provided but not application_id, resolve it
        if application_name and not application_id:
            logger.info(f"Resolving application name '{application_name}' to application ID")
            app_id_result = await self._get_application_id_by_name(application_name, ctx)

            if "error" in app_id_result:
                return {
                    "resource_type": "global_alert_config",
                    "operation": operation,
                    "error": f"Failed to resolve application name '{application_name}': {app_id_result['error']}"
                }

            application_id = app_id_result.get("application_id")
            logger.info(f"Resolved application '{application_name}' to ID: {application_id}")

        # Route to the global alert config client
        result = await self.app_global_alert_config_client.execute_alert_config_operation(
            operation=operation,
            application_id=application_id,
            id=id,
            alert_ids=alert_ids,
            valid_on=valid_on,
            created=created,
            payload=payload,
            ctx=ctx
        )

        return {
            "resource_type": "global_alert_config",
            "operation": operation,
            "application_name": application_name,
            "application_id": application_id,
            "results": result
        }

    async def _handle_settings(
        self,
        operation: str,
        params: Dict[str, Any],
        ctx
    ) -> Dict[str, Any]:
        """Handle Application Settings operations."""
        valid_operations = [
            "get_all", "get", "create", "update", "delete", "order", "replace_all"
        ]

        if operation not in valid_operations:
            return {
                "error": f"Invalid operation '{operation}' for settings",
                "valid_operations": valid_operations
            }

        # Extract parameters
        resource_subtype = params.get("resource_subtype")
        id = params.get("id")
        application_name = params.get("application_name")
        payload = params.get("payload")
        request_body = params.get("request_body")
        
        # For create operation with flat parameters, build payload from individual fields
        if operation == "create" and resource_subtype == "application":
            # Check if we have flat parameters (imap, label) instead of payload
            imap = params.get("imap")
            label = params.get("label")
            
            if imap or label:
                # Build payload from flat parameters
                payload_dict = {}
                if imap:
                    payload_dict["imap"] = imap
                if label:
                    payload_dict["label"] = label
                
                # Add optional parameters if provided
                if params.get("scope"):
                    payload_dict["scope"] = params.get("scope")
                if params.get("boundary_scope"):
                    payload_dict["boundaryScope"] = params.get("boundary_scope")
                if params.get("access_rules"):
                    # Parse access_rules if it's a JSON string
                    access_rules = params.get("access_rules")
                    if isinstance(access_rules, str):
                        try:
                            import json
                            payload_dict["accessRules"] = json.loads(access_rules)
                        except:
                            payload_dict["accessRules"] = access_rules
                    else:
                        payload_dict["accessRules"] = access_rules
                if params.get("tag_filter_expression"):
                    # Parse tag_filter_expression if it's a JSON string
                    tag_filter = params.get("tag_filter_expression")
                    if isinstance(tag_filter, str):
                        try:
                            import json
                            payload_dict["tagFilterExpression"] = json.loads(tag_filter)
                        except:
                            payload_dict["tagFilterExpression"] = tag_filter
                    else:
                        payload_dict["tagFilterExpression"] = tag_filter
                
                payload = payload_dict
                logger.info(f"Built payload from flat parameters: {payload}")

        # Validate resource_subtype
        valid_subtypes = ["application", "endpoint", "service", "manual_service"]
        if not resource_subtype or resource_subtype not in valid_subtypes:
            return {
                "error": f"Invalid or missing resource_subtype. Must be one of: {valid_subtypes}",
                "resource_subtype": resource_subtype
            }

        # If application_name is provided for application resource_subtype and operation is "get"
        # resolve it to application ID
        if resource_subtype == "application" and operation == "get" and application_name and not id:
            logger.info(f"Resolving application name '{application_name}' to application config ID")

            # First, get all application configs
            all_configs_result = await self.app_settings_client.execute_settings_operation(
                operation="get_all",
                resource_subtype="application",
                ctx=ctx
            )

            # Search for matching application name in configs
            if isinstance(all_configs_result, list):
                for config in all_configs_result:
                    if isinstance(config, dict):
                        config_label = config.get('label', '')
                        config_id = config.get('id', '')

                        # Case-insensitive match
                        if config_label.lower() == application_name.lower() and config_id:
                            logger.info(f"Found application config '{config_label}' with ID: {config_id}")
                            id = config_id
                            break

                if not id:
                    return {
                        "resource_type": "settings",
                        "resource_subtype": resource_subtype,
                        "operation": operation,
                        "error": f"No application perspective found with name '{application_name}'"
                    }
            else:
                return {
                    "resource_type": "settings",
                    "resource_subtype": resource_subtype,
                    "operation": operation,
                    "error": "Failed to retrieve application perspectives for name resolution"
                }

        # Route to the settings client
        result = await self.app_settings_client.execute_settings_operation(
            operation=operation,
            resource_subtype=resource_subtype,
            id=id,
            payload=payload,
            request_body=request_body,
            ctx=ctx
        )

        return {
            "resource_type": "settings",
            "resource_subtype": resource_subtype,
            "operation": operation,
            "application_name": application_name if application_name else None,
            "resolved_id": id if application_name else None,
            "results": result
        }

    async def _get_application_id_by_name(
        self,
        application_name: str,
        ctx
    ) -> Dict[str, Any]:
        """
        Get application ID by application name using the Application Resources API.

        Args:
            application_name: Name of the application
            ctx: MCP context

        Returns:
            Dictionary with application_id or error
        """
        try:
            from datetime import datetime

            logger.info(f"Resolving application name '{application_name}' to application ID using Application Resources API")

            # Set time range (last hour)
            to_time = int(datetime.now().timestamp() * 1000)
            window_size = 60 * 60 * 1000  # 1 hour

            # Use the app_resources_client to get applications
            result = await self.app_resources_client._get_applications_internal(
                name_filter=application_name,
                window_size=window_size,
                to_time=to_time,
                ctx=ctx
            )

            logger.debug(f"Application Resources API result: {result}")

            # Extract items from the result
            items = result.get('items', []) if isinstance(result, dict) else []

            if not items:
                logger.warning(f"No application found with name filter '{application_name}'")
                return {"error": f"No application found with name '{application_name}'"}

            # Find exact match (case-insensitive)
            for item in items:
                if isinstance(item, dict):
                    label = item.get('label', '')
                    app_id = item.get('id', '')

                    if label.lower() == application_name.lower() and app_id:
                        logger.info(f"Found application '{label}' with ID: {app_id}")
                        return {
                            "application_id": app_id,
                            "application_name": label
                        }

            # If no exact match, return the first result
            first_item = items[0]
            if isinstance(first_item, dict):
                label = first_item.get('label', '')
                app_id = first_item.get('id', '')

                if app_id:
                    logger.info(f"Using closest match: '{label}' with ID: {app_id}")
                    return {
                        "application_id": app_id,
                        "application_name": label
                    }

            return {"error": f"No application found with name '{application_name}'"}

        except Exception as e:
            logger.error(f"Error fetching application ID: {e}", exc_info=True)
            return {"error": f"Failed to fetch application ID: {e!s}"}

    async def _handle_catalog(
        self,
        operation: str,
        params: Dict[str, Any],
        ctx
    ) -> Dict[str, Any]:
        """Handle Application Catalog operations."""
        valid_operations = ["get_tag_catalog", "get_metric_catalog"]

        if operation not in valid_operations:
            return {
                "error": f"Invalid operation '{operation}' for catalog",
                "valid_operations": valid_operations
            }

        # Extract parameters
        use_case = params.get("use_case")
        data_source = params.get("data_source")
        var_from = params.get("var_from")

        # Route to the appropriate catalog method
        if operation == "get_tag_catalog":
            logger.info("Routing to Application Tag Catalog")
            result = await self.app_catalog_client.get_application_tag_catalog(
                use_case=use_case,
                data_source=data_source,
                var_from=var_from,
                ctx=ctx
            )

            return {
                "resource_type": "catalog",
                "operation": operation,
                "results": result
            }

        elif operation == "get_metric_catalog":
            logger.info("Routing to Application Metric Catalog")
            result = await self.app_catalog_client.get_application_metric_catalog(
                ctx=ctx
            )

            return {
                "resource_type": "catalog",
                "operation": operation,
                "results": result
            }

        return {
            "error": f"Unsupported catalog operation: {operation}",
            "valid_operations": valid_operations
        }

