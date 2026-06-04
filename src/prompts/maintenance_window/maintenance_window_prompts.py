"""
Maintenance Window Prompts for WatsonX Assistant Integration

These prompts help WatsonX Assistant understand how to map natural language
requests to the maintenance window management tool parameters.
"""

from typing import Optional

from src.prompts import auto_register_prompt


class MaintenanceWindowPrompts:
    """Class containing maintenance window related prompts"""

    @auto_register_prompt
    @staticmethod
    def create_maintenance_window(
        imap_code: str,
        start_time: str,
        duration_minutes: Optional[str] = None,
        duration_hours: Optional[str] = None,
        template: Optional[str] = None,
        reason: Optional[str] = None
    ) -> str:
        """
        Create a new maintenance window in Instana for an APPLICATION or IMAP code.

        Use this when the user says things like:
        - "Create a maintenance window for EAL-012471"
        - "Schedule maintenance for my application"
        - "Set up a maintenance window starting in 2 hours"
        - "Create a deployment maintenance window"
        - "Open a maintenance window for the next 2 hours"
        - "Schedule downtime for application EAL-012471"

        **DO NOT USE THIS PROMPT** if the user mentions ANY of these keywords:
        - "synthetic test" or "synthetic tests"
        - "synthetic monitor" or "synthetic monitoring"
        - "synthetic" (in the context of monitoring/testing)
        
        For synthetic tests/monitors, use create_maintenance_window_for_synthetic_tests_by_name instead.

        The start_time can be in natural language like "in 2 hours" or "tomorrow at 10am".
        """
        # Check if this looks like synthetic test names (contains multiple comma-separated values or "and")
        # Also check the reason field since WatsonX might put the full list there
        is_synthetic_test = False
        test_source = None
        
        # Check if reason contains "synthetic test" and multiple test names
        if reason and 'synthetic test' in reason.lower():
            # Extract test names from reason if it contains commas or "and"
            if ',' in reason or ' and ' in reason.lower():
                is_synthetic_test = True
                test_source = reason
                # Try to extract just the test names part
                import re
                # Look for patterns like "EAL-012471-alert-test, EAL-009683_Figma" or "EAL-012471-alert-test and EAL-009683_Figma"
                test_pattern = r'([A-Z]{3}-\d{6}[-_][^\s,]+(?:\s*(?:,|and)\s*[A-Z]{3}-\d{6}[-_][^\s,]+)*)'
                match = re.search(test_pattern, reason)
                if match:
                    test_source = match.group(1)
        
        # Fallback to imap_code if reason didn't have it
        if not is_synthetic_test and imap_code and (',' in imap_code or ' and ' in imap_code.lower()):
            is_synthetic_test = True
            test_source = imap_code
        
        if is_synthetic_test and test_source:
            import re
            test_list = re.split(r',|\s+and\s+', test_source)
            test_list = [t.strip() for t in test_list if t.strip()]
            synthetic_test_names_json = str(test_list).replace("'", '"')
        
        if is_synthetic_test:
            return f"""
DETECTED: This appears to be for SYNTHETIC TESTS (multiple test names detected)

Create a maintenance window for SYNTHETIC TESTS:
- Synthetic Test Names: {imap_code}
- Start Time: {start_time}
- Duration (minutes): {duration_minutes or '(not specified)'}
- Duration (hours): {duration_hours or '(not specified)'}
- Reason: {reason or '(not specified)'}

CRITICAL: Call the manage_maintenance_windows tool with these EXACT parameters for SYNTHETIC TESTS:
{{
  "resource_type": "window",
  "operation": "create",
  "apply_on_synthetic_tests": "true",
  "synthetic_test_names": '{synthetic_test_names_json}',
  "start_time": "{start_time}",
  "duration_minutes": "{duration_minutes or ''}",
  "duration_hours": "{duration_hours or ''}",
  "reason": "{reason or ''}"
}}

DO NOT use imap_code parameter!
"""
        else:
            return f"""
Create a maintenance window for APPLICATION:
- IMAP Code: {imap_code}
- Start Time: {start_time}
- Duration (minutes): {duration_minutes or '(use template default)'}
- Duration (hours): {duration_hours or '(not specified)'}
- Template: {template or '(not specified)'}
- Reason: {reason or '(not specified)'}

IMPORTANT: Call the manage_maintenance_windows tool with:
{{
  "resource_type": "window",
  "operation": "create",
  "imap_code": "{imap_code}",
  "start_time": "{start_time}",
  "duration_minutes": "{duration_minutes or ''}",
  "duration_hours": "{duration_hours or ''}",
  "template": "{template or ''}",
  "reason": "{reason or ''}"
}}
"""

    @auto_register_prompt
    @staticmethod
    def list_active_maintenance_windows(
        imap_code: Optional[str] = None
    ) -> str:
        """
        List all currently active maintenance windows in Instana.

        Use this when the user says things like:
        - "Show me active maintenance windows"
        - "What maintenance windows are currently running?"
        - "List active maintenance windows"
        - "Are there any maintenance windows active right now?"
        - "Which applications are in maintenance mode?"
        - "Show ongoing maintenance windows"
        """
        return f"""
List active maintenance windows:
- IMAP Code filter: {imap_code or '(all applications — no filter needed)'}

IMPORTANT: Call the manage_maintenance_windows tool IMMEDIATELY with:
{{
  "resource_type": "window",
  "operation": "list_active"{f', "imap_code": "{imap_code}"' if imap_code else ''}
}}

NOTE: imap_code is OPTIONAL. Do NOT ask the user for it. Call the tool immediately without imap_code to list all active windows.
"""

    @auto_register_prompt
    @staticmethod
    def list_all_maintenance_windows(
        imap_code: Optional[str] = None
    ) -> str:
        """
        List all maintenance windows in Instana including active, scheduled, and expired ones.

        Use this when the user says things like:
        - "Show me all maintenance windows"
        - "List all maintenance windows"
        - "Give me a full list of maintenance windows"
        - "Show maintenance window history"
        - "What maintenance windows exist?"
        - "Show all maintenance windows including past ones"
        """
        return f"""
List all maintenance windows (active, scheduled, and expired):
- IMAP Code filter: {imap_code or '(all applications — no filter needed)'}

IMPORTANT: Call the manage_maintenance_windows tool IMMEDIATELY with:
{{
  "resource_type": "window",
  "operation": "list_all"{f', "imap_code": "{imap_code}"' if imap_code else ''}
}}

NOTE: imap_code is OPTIONAL. Do NOT ask the user for it. Call the tool immediately without imap_code to list all windows.
"""

    @auto_register_prompt
    @staticmethod
    def list_scheduled_maintenance_windows(
        imap_code: Optional[str] = None
    ) -> str:
        """
        List all scheduled (upcoming/future) maintenance windows in Instana.

        Use this when the user says things like:
        - "Show me scheduled maintenance windows"
        - "What maintenance windows are scheduled?"
        - "List upcoming maintenance windows"
        - "Show future maintenance windows"
        - "What maintenance is planned?"
        - "Are there any scheduled maintenance windows for my applications?"
        - "Show me planned maintenance windows"
        - "Can you give me scheduled maintenance windows applications?"
        """
        return f"""
List scheduled (upcoming) maintenance windows:
- IMAP Code filter: {imap_code or '(all applications — no filter needed)'}

IMPORTANT: Call the manage_maintenance_windows tool IMMEDIATELY with:
{{
  "resource_type": "window",
  "operation": "list_scheduled"{f', "imap_code": "{imap_code}"' if imap_code else ''}
}}

NOTE: imap_code is OPTIONAL. Do NOT ask the user for it. Call the tool immediately without imap_code to list all scheduled windows across all applications.
"""

    @auto_register_prompt
    @staticmethod
    def modify_maintenance_window(
        window_id: str,
        duration_minutes: Optional[str] = None,
        end_time: Optional[str] = None,
        reason: Optional[str] = None
    ) -> str:
        """
        Modify or update an existing maintenance window in Instana.

        Use this when the user says things like:
        - "Extend maintenance window mw-789 by 30 minutes"
        - "Update the maintenance window duration"
        - "Change the end time of maintenance window"
        - "Modify maintenance window mw-789"
        - "Extend the current maintenance window"
        - "Update the reason for maintenance window"
        """
        return f"""
Modify maintenance window:
- Window ID: {window_id}
- New Duration (minutes): {duration_minutes or '(not changing)'}
- New End Time: {end_time or '(not changing)'}
- New Reason: {reason or '(not changing)'}

IMPORTANT: Call the manage_maintenance_windows tool with:
{{
  "resource_type": "window",
  "operation": "modify",
  "window_id": "{window_id}",
  "duration_minutes": "{duration_minutes or ''}",
  "end_time": "{end_time or ''}",
  "reason": "{reason or ''}"
}}
"""

    @auto_register_prompt
    @staticmethod
    def close_maintenance_window(
        window_id: str,
        completion_notes: Optional[str] = None
    ) -> str:
        """
        Close or end an active maintenance window in Instana.

        Use this when the user says things like:
        - "Close maintenance window mw-789"
        - "End the maintenance window"
        - "Complete maintenance window mw-789"
        - "Mark maintenance window as done"
        - "Finish the maintenance window"
        - "Close the maintenance window with notes"
        """
        return f"""
Close maintenance window:
- Window ID: {window_id}
- Completion Notes: {completion_notes or '(not specified)'}

IMPORTANT: Call the manage_maintenance_windows tool with:
{{
  "resource_type": "window",
  "operation": "close",
  "window_id": "{window_id}",
  "completion_notes": "{completion_notes or ''}"
}}
"""

    @auto_register_prompt
    @staticmethod
    def get_maintenance_templates() -> str:
        """
        Get all available maintenance window templates in Instana.

        Use this when the user says things like:
        - "What maintenance window templates are available?"
        - "Show me maintenance templates"
        - "List maintenance window types"
        - "What templates can I use for maintenance windows?"
        - "Show available maintenance window templates"
        - "What are the predefined maintenance window options?"
        """
        return """
Get maintenance window templates.

IMPORTANT: Call the manage_maintenance_windows tool with:
{
  "resource_type": "templates",
  "operation": "get"
}
"""

    @auto_register_prompt
    @staticmethod
    def create_maintenance_window_for_synthetic_tests_by_name(
        synthetic_test_names: Optional[str] = None,
        start_time: Optional[str] = None,
        duration_minutes: Optional[str] = None,
        duration_hours: Optional[str] = None,
        reason: Optional[str] = None
    ) -> str:
        """
        Create a SINGLE maintenance window for one or more synthetic tests by test name.

        **PRIORITY PROMPT**: Use this when the user mentions "synthetic test", "synthetic tests", "synthetic monitor", or "synthetic monitoring".
        
        This prompt should be PREFERRED over create_maintenance_window when user says "synthetic".
        
        Examples that MUST trigger this prompt:
        - "Create a maintenance window for synthetic tests EAL-012471-alert-test and EAL-009683_Figma"
        - "Schedule maintenance for synthetic test EAL-012471-alert-test"
        - "Set up a maintenance window for these synthetic tests: test1, test2"
        - "Create maintenance window for synthetic monitoring tests"
        - "I want to create a maintenance window for a synthetic monitor"
        - "Create a maintenance window for synthetic monitoring"
        - "maintenance window for synthetic tests named X and Y"
        - "synthetic tests EAL-012471-alert-test and EAL-009683_Figma"
        - "for synthetic tests EAL-012471-alert-test, EAL-009683_Figma"

        IMPORTANT: If the user mentions "synthetic" but doesn't provide test names yet, ask them:
        "To create a maintenance window for synthetic tests, I need:
        1. Test names (e.g., 'EAL-012471-alert-test, EAL-009683_Figma') OR
        2. Custom property filter (e.g., 'imap eal-012471')
        3. Start time (e.g., 'in 2 hours')
        4. Duration (e.g., '2 hours' or '120 minutes')
        5. (Optional) Reason for the maintenance
        
        Please provide the test names or custom property filter."

        CRITICAL PARAMETER EXTRACTION:
        - The synthetic_test_names parameter MUST capture ALL test names as a SINGLE STRING
        - If user says "tests A and B", synthetic_test_names should be "A and B" (not just "A")
        - If user says "tests A, B", synthetic_test_names should be "A, B" (not just "A")
        - DO NOT extract test names separately - keep them together in ONE parameter value
        - This function will be called ONCE with ALL test names, not multiple times
        """
        # Check if we have enough information to create the window
        if not synthetic_test_names and not start_time:
            # User just mentioned synthetic monitor without details - ask for information
            return """
I'll help you create a maintenance window for synthetic tests/monitors.

To proceed, I need the following information:

**Required:**
1. **Test identification** - Choose ONE of:
   - Specific test names (e.g., "EAL-012471-alert-test, EAL-009683_Figma")
   - Custom property filter (e.g., "imap eal-012471" to match all tests with that IMAP code)

2. **Start time** - When should the window begin?
   - Natural language: "in 2 hours", "tomorrow at 10am"
   - ISO format: "2026-06-01T14:00:00Z"

3. **Duration** - How long should the window last?
   - Examples: "2 hours", "120 minutes", "1 day"

**Optional:**
4. **Reason** - Why is this maintenance needed? (e.g., "Deployment", "Testing")

Please provide these details and I'll create the maintenance window for you.
"""
        
        # Convert comma-separated to JSON array if needed
        if synthetic_test_names and not synthetic_test_names.startswith('['):
            # Split by comma or "and" and create JSON array
            import re
            test_list = re.split(r',|\s+and\s+', synthetic_test_names)
            test_list = [t.strip() for t in test_list if t.strip()]
            synthetic_test_names_json = str(test_list).replace("'", '"')
        else:
            synthetic_test_names_json = synthetic_test_names
            
        return f"""
Create a SINGLE maintenance window for SYNTHETIC TESTS by test name:
- Synthetic Test Names: {synthetic_test_names}
- Start Time: {start_time}
- Duration (minutes): {duration_minutes or '(not specified)'}
- Duration (hours): {duration_hours or '(not specified)'}
- Reason: {reason or '(not specified)'}

CRITICAL INSTRUCTIONS:
1. This is for SYNTHETIC TESTS, not applications!
2. Call the tool ONLY ONCE with ALL test names in a single JSON array
3. DO NOT call the tool multiple times (once per test) - that creates separate windows
4. The synthetic_test_names parameter MUST contain ALL test names in ONE call

Call the manage_maintenance_windows tool ONCE with these EXACT parameters:
{{
  "resource_type": "window",
  "operation": "create",
  "apply_on_synthetic_tests": "true",
  "synthetic_test_names": '{synthetic_test_names_json}',
  "start_time": "{start_time}",
  "duration_minutes": "{duration_minutes or ''}",
  "duration_hours": "{duration_hours or ''}",
  "reason": "{reason or ''}"
}}

IMPORTANT:
- Call the tool ONCE, not multiple times
- The JSON array contains ALL test names: {synthetic_test_names_json}
- This creates ONE window with OR logic for all tests
- DO NOT use imap_code or application_id parameters
"""

    @auto_register_prompt
    @staticmethod
    def create_maintenance_window_for_synthetic_tests_by_property(
        custom_property_key: Optional[str] = None,
        custom_property_value: Optional[str] = None,
        start_time: Optional[str] = None,
        duration_minutes: Optional[str] = None,
        duration_hours: Optional[str] = None,
        reason: Optional[str] = None
    ) -> str:
        """
        Create a maintenance window for synthetic tests filtered by custom property.

        Use this when the user explicitly mentions "synthetic test" or "synthetic tests" with a custom property filter.
        
        Examples that should trigger this prompt:
        - "Create a maintenance window for synthetic tests with imap eal-012471"
        - "Schedule maintenance for synthetic tests where imap equals eal-012471"
        - "Set up maintenance window for synthetic tests with custom property imap=eal-012471"
        - "Apply maintenance window on synthetic tests filtered by imap code"
        - "Create maintenance for all synthetic tests tagged with imap eal-012471"
        - "maintenance window for synthetic tests with property X=Y"

        IMPORTANT: This prompt should ONLY be used when the user explicitly says "synthetic test" or "synthetic tests".
        The custom property is typically "imap" but can be any custom property key.
        """
        # Check if we have enough information to create the window
        if not custom_property_key and not start_time:
            # User just mentioned synthetic monitor without details - ask for information
            return """
I'll help you create a maintenance window for synthetic tests/monitors using custom properties.

To proceed, I need the following information:

**Required:**
1. **Custom property filter** - Specify the property to filter tests:
   - Property key (e.g., "imap", "environment", "team")
   - Property value (e.g., "eal-012471", "production", "platform")
   - Example: "imap eal-012471" or "environment production"

2. **Start time** - When should the window begin?
   - Natural language: "in 2 hours", "tomorrow at 10am"
   - ISO format: "2026-06-01T14:00:00Z"

3. **Duration** - How long should the window last?
   - Examples: "2 hours", "120 minutes", "1 day"

**Optional:**
4. **Reason** - Why is this maintenance needed? (e.g., "Deployment", "Testing")

Please provide these details and I'll create the maintenance window for you.
"""
        
        return f"""
Create a maintenance window for SYNTHETIC TESTS by custom property:
- Custom Property Key: {custom_property_key}
- Custom Property Value: {custom_property_value}
- Start Time: {start_time}
- Duration (minutes): {duration_minutes or '(not specified)'}
- Duration (hours): {duration_hours or '(not specified)'}
- Reason: {reason or '(not specified)'}

CRITICAL: This is for SYNTHETIC TESTS, not applications!

Call the manage_maintenance_windows tool with these EXACT parameters:
{{
  "resource_type": "window",
  "operation": "create",
  "apply_on_synthetic_tests": "true",
  "synthetic_custom_property_key": "{custom_property_key}",
  "synthetic_custom_property_value": "{custom_property_value}",
  "start_time": "{start_time}",
  "duration_minutes": "{duration_minutes or ''}",
  "duration_hours": "{duration_hours or ''}",
  "reason": "{reason or ''}"
}}

DO NOT use imap_code or application_id parameters - this is for synthetic tests only!
"""

    @auto_register_prompt
    @staticmethod
    def create_maintenance_window_for_synthetic_tests_with_and_logic(
        custom_property_key: str,
        custom_property_value: str,
        start_time: str,
        duration_minutes: Optional[str] = None,
        duration_hours: Optional[str] = None,
        reason: Optional[str] = None
    ) -> str:
        """
        Create a maintenance window for synthetic tests using AND logic (testName AND custom property).

        Use this when the user explicitly mentions BOTH "test name" AND a custom property with AND logic.
        
        Examples that should trigger this prompt:
        - "Create a maintenance window for synthetic tests with testName and imap eal-012471"
        - "Schedule maintenance for synthetic tests where testName AND imap equals eal-012471"
        - "Set up maintenance window for synthetic tests with both testName and imap eal-012471"
        - "Apply maintenance window on synthetic tests using testName AND custom property imap"
        - "Create maintenance for synthetic tests with testName and property imap=eal-012471"
        - "maintenance window for synthetic tests with testName AND imap code"

        IMPORTANT: This creates AND logic - the test must match BOTH testName AND the custom property.
        The testName will be derived from the custom_property_value.
        """
        return f"""
Create a maintenance window for SYNTHETIC TESTS using AND logic:
- Filter 1: Test Name = {custom_property_value}
- Filter 2: Custom Property {custom_property_key} = {custom_property_value.upper()}
- Logical Operator: AND (test must match BOTH conditions)
- Start Time: {start_time}
- Duration (minutes): {duration_minutes or '(not specified)'}
- Duration (hours): {duration_hours or '(not specified)'}
- Reason: {reason or '(not specified)'}

CRITICAL: This creates AND logic, not OR logic!

Call the manage_maintenance_windows tool with these EXACT parameters:
{{
  "resource_type": "window",
  "operation": "create",
  "apply_on_synthetic_tests": "true",
  "synthetic_custom_property_key": "{custom_property_key}",
  "synthetic_custom_property_value": "{custom_property_value}",
  "synthetic_include_test_name_filter": "true",
  "start_time": "{start_time}",
  "duration_minutes": "{duration_minutes or ''}",
  "duration_hours": "{duration_hours or ''}",
  "reason": "{reason or ''}"
}}

IMPORTANT:
- synthetic_include_test_name_filter: "true" enables AND logic
- This creates TWO filters: testName={custom_property_value} AND {custom_property_key}={custom_property_value.upper()}
- DO NOT use imap_code or application_id parameters
"""

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('create_maintenance_window', cls.create_maintenance_window),
            ('list_active_maintenance_windows', cls.list_active_maintenance_windows),
            ('list_all_maintenance_windows', cls.list_all_maintenance_windows),
            ('list_scheduled_maintenance_windows', cls.list_scheduled_maintenance_windows),
            ('modify_maintenance_window', cls.modify_maintenance_window),
            ('close_maintenance_window', cls.close_maintenance_window),
            ('get_maintenance_templates', cls.get_maintenance_templates),
            ('create_maintenance_window_for_synthetic_tests_by_name', cls.create_maintenance_window_for_synthetic_tests_by_name),
            ('create_maintenance_window_for_synthetic_tests_by_property', cls.create_maintenance_window_for_synthetic_tests_by_property),
        ]