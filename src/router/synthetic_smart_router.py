"""
Smart Router Tool for Synthetic Monitoring

This module provides a unified MCP tool that routes synthetic monitoring queries
to the appropriate specialized tools.
"""

import logging
from typing import Any, Dict, Optional

from mcp.types import ToolAnnotations  # type: ignore[import-untyped]

from src.core.utils import BaseInstanaClient, register_as_tool

logger = logging.getLogger(__name__)

# Define valid operations for each resource type at module level
SETTINGS_VALID_OPERATIONS = ["get_tests", "filter_by_imap", "get_locations"]
TOOLS_VALID_OPERATIONS = ["create_api_monitor"]

# Define parameter key constants to avoid typos
PARAM_APPLICATION_ID = "application_id"
PARAM_LOCATION_ID = "location_id"
PARAM_CREDENTIAL_NAME = "credential_name"
PARAM_SORT = "sort"
PARAM_FILTER = "filter"
PARAM_IMAP_VALUE = "imap_value"

# Parameters for create_api_monitor
PARAM_LABEL = "label"
PARAM_URL = "url"
PARAM_LOCATIONS = "locations"
PARAM_TEST_FREQUENCY = "test_frequency"
PARAM_METHOD = "method"
PARAM_HEADERS = "headers"
PARAM_BODY = "body"
PARAM_TIMEOUT = "timeout"
PARAM_FOLLOW_REDIRECTS = "follow_redirects"
PARAM_ALLOW_INSECURE = "allow_insecure"
PARAM_EXPECT_STATUS = "expect_status"
PARAM_EXPECT_JSON = "expect_json"
PARAM_EXPECT_MATCH = "expect_match"
PARAM_DESCRIPTION = "description"
PARAM_CUSTOM_PROPERTIES = "custom_properties"
PARAM_ACTIVE = "active"


class SmartRouterSyntheticMCPTool(BaseInstanaClient):
    """
    Smart router for synthetic monitoring operations.
    Routes queries to Synthetic Monitoring tools.
    """

    def __init__(self, read_token: str, base_url: str):
        """Initialize the Smart Router Synthetic MCP tool."""
        super().__init__(read_token=read_token, base_url=base_url)

        # Lazy import to avoid circular dependencies
        from src.synthetic.synthetic_setting import SyntheticMonitoringMCPTools
        from src.synthetic.synthetic_tools import SyntheticMonitoringTools

        # Initialize the synthetic monitoring clients
        self.synthetic_monitoring_client = SyntheticMonitoringMCPTools(read_token, base_url)
        self.synthetic_tools_client = SyntheticMonitoringTools(read_token, base_url)

        logger.info("Smart Router Synthetic initialized with Monitoring and Tools clients")

    @register_as_tool(
        title="Manage Instana Synthetic Monitoring Resources",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False)
    )
    async def manage_synthetic_monitoring(
        self,
        resource_type: str,
        operation: str,
        # Flat parameters for Watson Orchestrate compatibility
        label: Optional[str] = None,
        url: Optional[str] = None,
        locations: Optional[str] = None,
        imap: Optional[str] = None,
        env: Optional[str] = None,
        test_frequency: Optional[str] = None,
        method: Optional[str] = None,
        headers: Optional[str] = None,
        body: Optional[str] = None,
        timeout: Optional[str] = None,
        follow_redirects: Optional[str] = None,
        allow_insecure: Optional[str] = None,
        expect_status: Optional[str] = None,
        expect_json: Optional[str] = None,
        expect_match: Optional[str] = None,
        description: Optional[str] = None,
        application_id: Optional[str] = None,
        active: Optional[str] = None,
        # Settings parameters
        location_id: Optional[str] = None,
        credential_name: Optional[str] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        imap_value: Optional[str] = None,
        ctx=None
    ) -> Dict[str, Any]:
        """
        Unified Instana synthetic monitoring resource manager for test retrieval and management.

        ALL PARAMETERS ARE FLAT STRINGS - No nested objects required!

        Resource Types:
            - "settings": Manage synthetic test configurations
            - "tools": Create and manage synthetic monitors

        SETTINGS (resource_type="settings"):
            operations: get_tests, filter_by_imap, get_locations

            get_locations - Get all available synthetic monitoring locations
                No parameters required
                Returns: List of locations with id, displayLabel, and other metadata
                IMPORTANT: Always call this FIRST when creating monitors to show user available locations

            get_tests - Retrieve all synthetic monitoring tests
                Optional parameters:
                - application_id: Filter by application ID
                - location_id: Filter by location ID
                - credential_name: Filter by credential name
                - sort: Sort attribute ('+' for ASC, '-' for DESC, e.g., '+label' or '-createdAt')
                - filter: Custom filter string (e.g., 'label=MyTest')

            filter_by_imap - Filter all tests by custom properties 'imap' key
                Required parameter:
                - imap_value: The imap value to search for in custom properties

        TOOLS (resource_type="tools"):
            operations: create_api_monitor

            create_api_monitor - Create a new API synthetic monitor
                
                ALL PARAMETERS ARE FLAT STRINGS!
                
                Required parameters:
                - label: Monitor name starting with IMAP value (e.g., "EAL-012471_MyAPI")
                - url: API endpoint (e.g., "https://ibm.com")
                - locations: JSON array string or comma-separated (e.g., '["bxx9yzjHmKFn1u2oz3Kg"]' or "loc1,loc2")
                - imap: IMAP identifier string (e.g., "EAL-012471")
                - env: Environment string (e.g., "dev", "prod", "test")
                
                Optional parameters (all as strings):
                - test_frequency: Test frequency in minutes (default: "15")
                - method: HTTP method (default: "GET")
                - headers: JSON string of headers (e.g., '{"Content-Type": "application/json"}')
                - body: Request body string
                - timeout: Request timeout in milliseconds (default: "10000")
                - follow_redirects: "true" or "false" (default: "true")
                - allow_insecure: "true" or "false" (default: "false")
                - expect_status: Expected HTTP status code (default: "200")
                - expect_json: JSONPath expression to validate response
                - expect_match: Regex pattern to match in response body
                - description: Description of the test
                - application_id: Associate test with an application
                - active: "true" or "false" (default: "true")

        Args:
            resource_type: "settings" or "tools"
            operation: Specific operation for the resource type
            All other parameters are optional and operation-specific
            ctx: MCP context (internal)

        Returns:
            Dictionary with results from the appropriate tool

        Examples:
            # Get all synthetic tests
            resource_type="settings", operation="get_tests"

            # Get tests filtered by application
            resource_type="settings", operation="get_tests", application_id="app123"

            # Filter tests by imap custom property
            resource_type="settings", operation="filter_by_imap", imap_value="EAL-012471"

            # Create a new API monitor
            resource_type="tools", operation="create_api_monitor",
            label="EAL-012471_MyAPI", url="https://ibm.com",
            locations='["bxx9yzjHmKFn1u2oz3Kg"]', imap="EAL-012471", env="dev"
        """

        try:
            logger.debug(f"Synthetic Router: resource_type={resource_type}, operation={operation}")

            # Build params dict from flat parameters
            params = {}
            if label is not None:
                params['label'] = label
            if url is not None:
                params['url'] = url
            if locations is not None:
                params['locations'] = locations
            if imap is not None:
                params['imap'] = imap
            if env is not None:
                params['env'] = env
            if test_frequency is not None:
                params['test_frequency'] = test_frequency
            if method is not None:
                params['method'] = method
            if headers is not None:
                params['headers'] = headers
            if body is not None:
                params['body'] = body
            if timeout is not None:
                params['timeout'] = timeout
            if follow_redirects is not None:
                params['follow_redirects'] = follow_redirects
            if allow_insecure is not None:
                params['allow_insecure'] = allow_insecure
            if expect_status is not None:
                params['expect_status'] = expect_status
            if expect_json is not None:
                params['expect_json'] = expect_json
            if expect_match is not None:
                params['expect_match'] = expect_match
            if description is not None:
                params['description'] = description
            if application_id is not None:
                params['application_id'] = application_id
            if active is not None:
                params['active'] = active
            if location_id is not None:
                params['location_id'] = location_id
            if credential_name is not None:
                params['credential_name'] = credential_name
            if sort is not None:
                params['sort'] = sort
            if filter is not None:
                params['filter'] = filter
            if imap_value is not None:
                params['imap_value'] = imap_value

            # Validate resource_type
            if resource_type not in ["settings", "tools"]:
                return {
                    "error": f"Invalid resource_type '{resource_type}'. Valid types: 'settings', 'tools'",
                    "valid_types": ["settings", "tools"]
                }

            # Route to the appropriate resource handler
            if resource_type == "settings":
                return await self._handle_settings(operation, params, ctx)
            elif resource_type == "tools":
                return await self._handle_tools(operation, params, ctx)
            else:
                return {
                    "error": f"Unsupported resource_type: {resource_type}",
                    "supported_types": ["settings", "tools"]
                }

        except Exception as e:
            logger.error(
                f"Error in synthetic smart router: {e} | "
                f"resource_type={resource_type}, operation={operation}, params={params}",
                exc_info=True
            )
            return {
                "error": f"Synthetic router error: {e!s}",
                "resource_type": resource_type,
                "operation": operation
            }

    async def _handle_settings(
        self,
        operation: str,
        params: Dict[str, Any],
        ctx
    ) -> Dict[str, Any]:
        """Handle settings resource operations."""
        if operation not in SETTINGS_VALID_OPERATIONS:
            return {
                "error": f"Invalid operation '{operation}' for settings",
                "valid_operations": SETTINGS_VALID_OPERATIONS,
                "hint": "Use 'get_tests' to retrieve synthetic monitoring tests"
            }

        if operation == "get_tests":
            return await self.synthetic_monitoring_client.get_synthetic_tests(
                application_id=params.get(PARAM_APPLICATION_ID),
                location_id=params.get(PARAM_LOCATION_ID),
                credential_name=params.get(PARAM_CREDENTIAL_NAME),
                sort=params.get(PARAM_SORT),
                filter=params.get(PARAM_FILTER),
                ctx=ctx
            )
        
        elif operation == "get_locations":
            return await self.synthetic_monitoring_client.get_locations(ctx=ctx)
        
        elif operation == "filter_by_imap":
            imap_value = params.get(PARAM_IMAP_VALUE)
            if not imap_value:
                return {
                    "error": "Missing required parameter 'imap_value'",
                    "hint": "Provide imap_value to filter tests by custom properties"
                }
            return await self.synthetic_monitoring_client.filter_tests_by_imap(
                imap_value=imap_value,
                ctx=ctx
            )

        return {
            "error": f"Operation '{operation}' not implemented",
            "valid_operations": SETTINGS_VALID_OPERATIONS
        }

    async def _handle_tools(
        self,
        operation: str,
        params: Dict[str, Any],
        ctx
    ) -> Dict[str, Any]:
        """Handle tools resource operations."""
        if operation not in TOOLS_VALID_OPERATIONS:
            return {
                "error": f"Invalid operation '{operation}' for tools",
                "valid_operations": TOOLS_VALID_OPERATIONS,
                "hint": "Use 'create_api_monitor' to create a new API synthetic monitor"
            }

        if operation == "create_api_monitor":
            # Convert all parameters to strings for the flattened API
            import json
            
            label = params.get(PARAM_LABEL)
            url = params.get(PARAM_URL)
            locations = params.get(PARAM_LOCATIONS)
            imap = params.get("imap")
            env = params.get("env")

            if not label:
                return {
                    "error": "Missing required parameter 'label'",
                    "hint": "Provide a name for the synthetic monitor"
                }
            if not url:
                return {
                    "error": "Missing required parameter 'url'",
                    "hint": "Provide the API endpoint URL to monitor"
                }
            if not locations:
                return {
                    "error": "Missing required parameter 'locations'",
                    "hint": "Provide a list of location IDs where the test should run"
                }
            if not imap:
                return {
                    "error": "Missing required parameter 'imap'",
                    "hint": "Provide IMAP identifier (e.g., 'EAL-012471')"
                }
            if not env:
                return {
                    "error": "Missing required parameter 'env'",
                    "hint": "Provide environment (e.g., 'dev', 'prod', 'test')"
                }

            # Convert locations to string format (JSON array or comma-separated)
            if isinstance(locations, list):
                locations_str = json.dumps(locations)
            else:
                locations_str = str(locations)
            
            # Convert headers to JSON string if it's a dict
            headers = params.get(PARAM_HEADERS)
            headers_str = json.dumps(headers) if isinstance(headers, dict) else headers

            return await self.synthetic_tools_client.create_api_synthetic_monitor(
                label=str(label),
                url=str(url),
                locations=locations_str,
                imap=str(imap),
                env=str(env),
                test_frequency=str(params.get(PARAM_TEST_FREQUENCY, 15)),
                method=str(params.get(PARAM_METHOD, "GET")),
                headers=headers_str,
                body=params.get(PARAM_BODY),
                timeout=str(params.get(PARAM_TIMEOUT, 10000)),
                follow_redirects=str(params.get(PARAM_FOLLOW_REDIRECTS, True)).lower(),
                allow_insecure=str(params.get(PARAM_ALLOW_INSECURE, False)).lower(),
                expect_status=str(params.get(PARAM_EXPECT_STATUS, 200)),
                expect_json=params.get(PARAM_EXPECT_JSON),
                expect_match=params.get(PARAM_EXPECT_MATCH),
                description=params.get(PARAM_DESCRIPTION),
                application_id=params.get(PARAM_APPLICATION_ID),
                active=str(params.get(PARAM_ACTIVE, True)).lower(),
                ctx=ctx
            )

        return {
            "error": f"Operation '{operation}' not implemented",
            "valid_operations": TOOLS_VALID_OPERATIONS
        }

# Made with Bob
