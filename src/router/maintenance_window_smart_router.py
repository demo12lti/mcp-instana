"""
Maintenance Window Smart Router Tool

This module provides a unified MCP tool that routes maintenance window queries
to the appropriate maintenance window management tools.
"""

import logging
from typing import Any, Dict, Optional

from mcp.types import ToolAnnotations

from src.core.utils import BaseInstanaClient, register_as_tool

logger = logging.getLogger(__name__)

# Resource type constants
RESOURCE_TYPE_MAINTENANCE_WINDOW = "maintenance_window"

# Valid resource types
VALID_RESOURCE_TYPES = [RESOURCE_TYPE_MAINTENANCE_WINDOW]

# Operation constants
OP_CREATE = "create"
OP_MODIFY = "modify"
OP_CLOSE = "close"
OP_LIST_ACTIVE = "list_active"
OP_LIST_SCHEDULED = "list_scheduled"
OP_LIST_ALL = "list_all"
OP_LIST_EXPIRED = "list_expired"
OP_BULK_CREATE = "bulk_create"
OP_VALIDATE = "validate"
OP_GET_TEMPLATES = "get_templates"

# Valid operations
VALID_OPERATIONS = [
    OP_CREATE,
    OP_MODIFY,
    OP_CLOSE,
    OP_LIST_ACTIVE,
    OP_LIST_SCHEDULED,
    OP_LIST_ALL,
    OP_LIST_EXPIRED,
    OP_BULK_CREATE,
    OP_VALIDATE,
    OP_GET_TEMPLATES
]

# Parameter name constants
PARAM_APPLICATION_ID = "application_id"
PARAM_APPLICATION_IDS = "application_ids"
PARAM_IMAP_CODE = "imap_code"
PARAM_IMAP_CODES = "imap_codes"
PARAM_WINDOW_ID = "window_id"
PARAM_START_TIME = "start_time"
PARAM_END_TIME = "end_time"
PARAM_DURATION_MINUTES = "duration_minutes"
PARAM_DURATION_HOURS = "duration_hours"
PARAM_DURATION_DAYS = "duration_days"
PARAM_REASON = "reason"
PARAM_TEMPLATE = "template"
PARAM_CHANGE_REQUEST_ID = "change_request_id"
PARAM_AFFECTED_SERVICES = "affected_services"
PARAM_NOTIFICATION_CHANNELS = "notification_channels"
PARAM_COMPLETION_NOTES = "completion_notes"
PARAM_USE_TAG_FILTER_EXPRESSION = "use_tag_filter_expression"
PARAM_TAG_NAME = "tag_name"
PARAM_RRULE = "rrule"
PARAM_UNTIL_DATE = "until_date"


class MaintenanceWindowSmartRouterMCPTool(BaseInstanaClient):
    """
    Smart router for maintenance window operations.
    Routes queries to Maintenance Window Management tools.
    """

    def __init__(self, read_token: str, base_url: str):
        """Initialize the Maintenance Window Smart Router MCP tool."""
        super().__init__(read_token=read_token, base_url=base_url)

        # Lazy import to avoid circular dependencies
        from src.maintenance_window.maintenance_window_tool import MaintenanceWindowMCPTools

        # Initialize the maintenance window client
        self.maintenance_window_client = MaintenanceWindowMCPTools(read_token, base_url)

        logger.info("Maintenance Window Smart Router initialized")

    @register_as_tool(
        title="Manage Instana Maintenance Windows",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False)
    )
    async def manage_maintenance_windows(
        self,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
        ctx=None
    ) -> Dict[str, Any]:
        """
        Unified Instana maintenance window manager for lifecycle management.

        Operations:
        - "create": Create a new maintenance window
        - "modify": Modify an existing maintenance window
        - "close": Close and document a maintenance window
        - "list_active": List all active maintenance windows
        - "list_scheduled": List all scheduled maintenance windows
        - "list_all": List all maintenance windows (active, scheduled, and expired)
        - "list_expired": List all expired maintenance windows
        - "bulk_create": Create maintenance windows for multiple applications
        - "validate": Validate maintenance window parameters without creating
        - "get_templates": Retrieve available maintenance window templates

        Parameters (params dict):
        - application_id: Single application ID (legacy support, treated as IMAP code)
        - application_ids: Multiple application IDs for bulk operations
        - imap_code: Single IMAP code (e.g., EAL-012512, ORZ-000012)
        - imap_codes: Multiple IMAP codes for bulk operations
        - window_id: Existing maintenance window ID (for modify/close operations)
        - start_time: Start time in Unix timestamp milliseconds
        - end_time: End time in Unix timestamp milliseconds
        - duration_minutes: Duration in minutes
        - duration_hours: Duration in hours
        - duration_days: Duration in days
        - reason: Reason for maintenance window
        - template: Predefined template name (deployment, database_migration, etc.)
        - change_request_id: ServiceNow change request ID
        - affected_services: List of affected service names
        - notification_channels: List of notification channels
        - completion_notes: Notes for window closure
        - use_tag_filter_expression: Use tag filter expression format
        - tag_name: Tag name for filter expression
        - rrule: Recurrence rule for recurring windows
        - until_date: End date for recurring windows

        Args:
            operation: Operation to perform
            params: Operation-specific parameters (optional)
            ctx: MCP context (internal)

        Returns:
            Dictionary with results from the appropriate tool

        Examples:
            # Create maintenance window
            operation="create", params={
                "imap_code": "EAL-012471",
                "start_time": 1709020800000,
                "duration_minutes": 120,
                "template": "deployment"
            }

            # Modify window duration
            operation="modify", params={
                "window_id": "mw-789",
                "duration_minutes": 60
            }

            # Modify window recurrence
            operation="modify", params={
                "window_id": "mw-789",
                "until_date": "2026-03-18T23:59:59Z"
            }

            # Close window
            operation="close", params={
                "window_id": "mw-789",
                "completion_notes": "Completed successfully"
            }

            # List all windows
            operation="list_all"

            # List active windows
            operation="list_active"

            # List scheduled windows
            operation="list_scheduled"

            # List expired windows
            operation="list_expired"
        """
        try:
            logger.info(f"Maintenance Window Router received: operation={operation}")

            # Initialize params if not provided
            if params is None:
                params = {}

            # Validate operation
            if operation not in VALID_OPERATIONS:
                logger.warning(f"Invalid operation: {operation}")
                return {
                    "error": f"Invalid operation '{operation}'",
                    "valid_operations": VALID_OPERATIONS
                }

            # Extract parameters using constants
            application_id = params.get(PARAM_APPLICATION_ID)
            application_ids = params.get(PARAM_APPLICATION_IDS)
            imap_code = params.get(PARAM_IMAP_CODE)
            imap_codes = params.get(PARAM_IMAP_CODES)
            window_id = params.get(PARAM_WINDOW_ID)
            start_time = params.get(PARAM_START_TIME)
            end_time = params.get(PARAM_END_TIME)
            duration_minutes = params.get(PARAM_DURATION_MINUTES)
            duration_hours = params.get(PARAM_DURATION_HOURS)
            duration_days = params.get(PARAM_DURATION_DAYS)
            reason = params.get(PARAM_REASON)
            template = params.get(PARAM_TEMPLATE)
            change_request_id = params.get(PARAM_CHANGE_REQUEST_ID)
            affected_services = params.get(PARAM_AFFECTED_SERVICES)
            notification_channels = params.get(PARAM_NOTIFICATION_CHANNELS)
            completion_notes = params.get(PARAM_COMPLETION_NOTES)
            use_tag_filter_expression = params.get(PARAM_USE_TAG_FILTER_EXPRESSION, False)
            tag_name = params.get(PARAM_TAG_NAME)
            rrule = params.get(PARAM_RRULE)
            until_date = params.get(PARAM_UNTIL_DATE)

            # Route to the maintenance window client
            logger.info(f"Routing to Maintenance Window client for operation: {operation}")

            result = await self.maintenance_window_client.execute_maintenance_operation(
                operation=operation,
                application_id=application_id,
                application_ids=application_ids,
                imap_code=imap_code,
                imap_codes=imap_codes,
                window_id=window_id,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration_minutes,
                duration_hours=duration_hours,
                duration_days=duration_days,
                reason=reason,
                template=template,
                change_request_id=change_request_id,
                affected_services=affected_services,
                notification_channels=notification_channels,
                completion_notes=completion_notes,
                use_tag_filter_expression=use_tag_filter_expression,
                tag_name=tag_name,
                rrule=rrule,
                until_date=until_date,
                ctx=ctx
            )

            return {
                "operation": operation,
                "results": result
            }

        except Exception as e:
            logger.error(f"Error in maintenance window smart router: {e}", exc_info=True)
            return {
                "error": f"Maintenance window router error: {e!s}",
                "operation": operation
            }

# Made with Bob
