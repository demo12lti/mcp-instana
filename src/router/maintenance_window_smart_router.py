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
        application_id: Optional[str] = None,
        application_ids: Optional[list] = None,
        imap_code: Optional[str] = None,
        imap_codes: Optional[list] = None,
        window_id: Optional[str] = None,
        start_time: Optional[Any] = None,
        end_time: Optional[Any] = None,
        duration_minutes: Optional[Any] = None,
        duration_hours: Optional[Any] = None,
        duration_days: Optional[Any] = None,
        reason: Optional[str] = None,
        template: Optional[str] = None,
        change_request_id: Optional[str] = None,
        affected_services: Optional[list] = None,
        notification_channels: Optional[list] = None,
        completion_notes: Optional[str] = None,
        use_tag_filter_expression: Optional[bool] = False,
        tag_name: Optional[str] = None,
        rrule: Optional[str] = None,
        until_date: Optional[str] = None,
        ctx=None
    ) -> Dict[str, Any]:
        """
        Unified Instana maintenance window manager for lifecycle management.
        
        IMPORTANT: The 'operation' parameter is REQUIRED and must be one of:
        - "create" - Create a new maintenance window
        - "modify" - Modify an existing maintenance window
        - "close" - Close and document a maintenance window
        - "list_active" - List all active maintenance windows
        - "list_scheduled" - List all scheduled maintenance windows
        - "list_all" - List all maintenance windows (active, scheduled, and expired)
        - "list_expired" - List all expired maintenance windows
        - "bulk_create" - Create maintenance windows for multiple applications
        - "validate" - Validate maintenance window parameters without creating
        - "get_templates" - Retrieve available maintenance window templates

        Args:
            operation: (REQUIRED) The operation to perform. Must be one of: create, modify, close, list_active, list_scheduled, list_all, list_expired, bulk_create, validate, get_templates
            application_id: Single application ID (legacy support, treated as IMAP code)
            application_ids: Multiple application IDs for bulk operations
            imap_code: Single IMAP code (e.g., EAL-012512, ORZ-000012, MUR-123456)
            imap_codes: Multiple IMAP codes for bulk operations
            window_id: Existing maintenance window ID (for modify/close operations)
            start_time: Start time (Unix timestamp in ms, ISO string, or natural language like "in 2 hours")
            end_time: End time (Unix timestamp in ms, ISO string, or natural language)
            duration_minutes: Duration in minutes (integer or string like "120" or "2 hours")
            duration_hours: Duration in hours (integer or string)
            duration_days: Duration in days (integer or string)
            reason: Reason for maintenance window
            template: Predefined template name (deployment, database_migration, etc.)
            change_request_id: ServiceNow change request ID
            affected_services: List of affected service names
            notification_channels: List of notification channels
            completion_notes: Notes for window closure
            use_tag_filter_expression: Use tag filter expression format
            tag_name: Tag name for filter expression
            rrule: Recurrence rule for recurring windows
            until_date: End date for recurring windows
            ctx: MCP context (internal)

        Returns:
            Dictionary with results from the appropriate tool

        Examples:
            # Example 1: Create maintenance window with natural language time
            {
                "operation": "create",
                "imap_code": "EAL-012471",
                "start_time": "in 2 hours",
                "duration_minutes": "120",
                "template": "deployment"
            }

            # Example 2: Create with ISO timestamp
            {
                "operation": "create",
                "imap_code": "EAL-012471",
                "start_time": "2026-04-18T14:00:00Z",
                "duration_minutes": 120,
                "reason": "Scheduled deployment"
            }

            # Example 3: Create recurring maintenance window
            {
                "operation": "create",
                "imap_code": "ORZ-000012",
                "start_time": "in 3 hours",
                "duration_minutes": 30,
                "rrule": "FREQ=DAILY;INTERVAL=1",
                "until_date": "2026-05-17T23:59:59Z"
            }

            # Example 4: List all active windows
            {
                "operation": "list_active"
            }

            # Example 5: List windows for specific application
            {
                "operation": "list_active",
                "imap_code": "EAL-012471"
            }

            # Example 6: Modify window duration
            {
                "operation": "modify",
                "window_id": "mw-789",
                "duration_minutes": 60
            }

            # Example 7: Close window with notes
            {
                "operation": "close",
                "window_id": "mw-789",
                "completion_notes": "Completed successfully"
            }

            # Example 8: Get available templates
            {
                "operation": "get_templates"
            }
        """
        try:
            logger.info(f"=== Maintenance Window Router START ===")
            logger.info(f"Operation: {operation}")
            logger.info(f"application_id: {application_id}")
            logger.info(f"imap_code: {imap_code}")
            logger.info(f"start_time: {start_time}")
            logger.info(f"template: {template}")
            
            # Log recurrence parameters if provided
            if rrule:
                logger.info(f"🔁 RECURRING WINDOW - Router received:")
                logger.info(f"  - rrule: {rrule}")
                logger.info(f"  - until_date: {until_date}")

            # Validate operation
            if operation not in VALID_OPERATIONS:
                logger.warning(f"Invalid operation: {operation}")
                return {
                    "error": f"Invalid operation '{operation}'",
                    "valid_operations": VALID_OPERATIONS
                }

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

            logger.info(f"Result from maintenance_window_client: {result}")
            logger.info(f"=== Maintenance Window Router END ===")

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


