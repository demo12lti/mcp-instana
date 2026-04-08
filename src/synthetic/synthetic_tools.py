"""
Synthetic Monitoring Tools Module

This module provides tools for creating and managing synthetic API monitors in Instana.
"""

import json
import logging
from typing import Any, Dict, List, Optional

# Import the necessary classes from the SDK
try:
    from instana_client.api.synthetic_settings_api import SyntheticSettingsApi  # type: ignore[import-untyped]
    from instana_client.models.synthetic_test import SyntheticTest  # type: ignore[import-untyped]
    from instana_client.models.http_action_configuration import HttpActionConfiguration  # type: ignore[import-untyped]
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Error importing Instana SDK: {e}", exc_info=True)
    raise

from mcp.types import ToolAnnotations  # type: ignore[import-untyped]

from src.core.utils import BaseInstanaClient, register_as_tool, with_header_auth

# Configure logger for this module
logger = logging.getLogger(__name__)

DEFAULT_CHARSET = 'utf-8'


def _decode_response(response) -> str:
    """
    Safely decode response data using the response's charset or UTF-8 as fallback.

    Args:
        response: The HTTP response object

    Returns:
        Decoded response text
    """
    from email.message import Message
    
    charset = DEFAULT_CHARSET
    
    if hasattr(response, 'headers') and response.headers:
        content_type = response.headers.get('Content-Type', '')
        if content_type:
            msg = Message()
            msg['content-type'] = content_type
            parsed_charset = msg.get_content_charset()
            if parsed_charset:
                charset = parsed_charset
    
    try:
        return response.data.decode(charset)
    except (UnicodeDecodeError, LookupError):
        return response.data.decode(DEFAULT_CHARSET, errors='replace')


class SyntheticMonitoringTools(BaseInstanaClient):
    """Tools for creating and managing synthetic API monitors in Instana."""

    def __init__(self, read_token: str, base_url: str):
        """Initialize the Synthetic Monitoring tools client."""
        super().__init__(read_token=read_token, base_url=base_url)

    @with_header_auth(SyntheticSettingsApi)
    async def create_api_synthetic_monitor(
        self,
        label: str,
        url: str,
        locations: str,  # Changed to string - will parse internally
        imap: str,  # NEW: Flat IMAP parameter
        env: str,  # NEW: Flat environment parameter
        test_frequency: str = "15",  # Changed to string
        method: str = "GET",
        headers: Optional[str] = None,  # Changed to string (JSON)
        body: Optional[str] = None,
        timeout: str = "10000",  # Changed to string
        follow_redirects: str = "true",  # Changed to string
        allow_insecure: str = "false",  # Changed to string
        expect_status: str = "200",  # Changed to string
        expect_json: Optional[str] = None,
        expect_match: Optional[str] = None,
        description: Optional[str] = None,
        application_id: Optional[str] = None,
        active: str = "true",  # Changed to string
        ctx=None,
        api_client=None
    ) -> Dict[str, Any]:
        """
        Create a new API synthetic monitor in Instana.

        ALL PARAMETERS ARE STRINGS - Objects constructed internally for Watson Orchestrate compatibility.

        This creates an HTTP/HTTPS synthetic test that monitors API endpoints.
        The test will run at the specified frequency from the given locations.

        Args:
            label: Name/label for the synthetic test (required, must start with IMAP)
            url: The API endpoint URL to monitor (required)
            locations: Location IDs as comma-separated string or JSON array (required, e.g., "loc1,loc2" or '["loc1","loc2"]')
            imap: IMAP identifier (required, e.g., "EAL-012471")
            env: Environment (required, e.g., "dev", "prod", "test")
            test_frequency: Test frequency in minutes as string (default: "15")
            method: HTTP method (default: "GET")
            headers: HTTP headers as JSON string (optional, e.g., '{"Content-Type": "application/json"}')
            body: Request body for POST/PUT/PATCH requests (optional)
            timeout: Request timeout in milliseconds as string (default: "10000")
            follow_redirects: Whether to follow HTTP redirects as string (default: "true")
            allow_insecure: Allow insecure SSL certificates as string (default: "false")
            expect_status: Expected HTTP status code as string (default: "200")
            expect_json: JSONPath expression to validate response (optional)
            expect_match: Regex pattern to match in response body (optional)
            description: Description of the synthetic test (optional)
            application_id: Associate test with an application (optional)
            active: Whether the test is active as string (default: "true")
            ctx: The MCP context (optional)

        Returns:
            Dictionary containing the created synthetic test details including ID and URL

        Example (All Strings):
            {
                "label": "EAL-012471_MyAPI",
                "url": "https://api.example.com/health",
                "locations": "loc1,loc2",
                "imap": "EAL-012471",
                "env": "dev",
                "test_frequency": "5",
                "timeout": "15000"
            }
        """
        try:
            logger.debug(f"[create_api_synthetic_monitor] Creating monitor: {label}")

            # Parse string parameters to proper types
            # 1. Parse locations (can be comma-separated string or JSON array)
            try:
                if locations.startswith('['):
                    # JSON array format
                    locations_list = json.loads(locations)
                else:
                    # Comma-separated format
                    locations_list = [loc.strip() for loc in locations.split(',') if loc.strip()]
            except Exception as e:
                return {
                    "error": f"Invalid locations format: {e}",
                    "hint": "Provide locations as comma-separated string (e.g., 'loc1,loc2') or JSON array (e.g., '[\"loc1\",\"loc2\"]')"
                }

            # 2. Parse test_frequency to int
            try:
                test_frequency_int = int(test_frequency)
            except ValueError:
                return {"error": f"Invalid test_frequency: '{test_frequency}' must be a number"}

            # 3. Parse timeout to int
            try:
                timeout_int = int(timeout)
            except ValueError:
                return {"error": f"Invalid timeout: '{timeout}' must be a number"}

            # 4. Parse expect_status to int
            try:
                expect_status_int = int(expect_status)
            except ValueError:
                return {"error": f"Invalid expect_status: '{expect_status}' must be a number"}

            # 5. Parse boolean strings
            follow_redirects_bool = follow_redirects.lower() in ['true', '1', 'yes']
            allow_insecure_bool = allow_insecure.lower() in ['true', '1', 'yes']
            active_bool = active.lower() in ['true', '1', 'yes']

            # 6. Parse headers if provided (JSON string to dict)
            headers_dict = None
            if headers:
                try:
                    headers_dict = json.loads(headers)
                except Exception as e:
                    return {
                        "error": f"Invalid headers format: {e}",
                        "hint": "Provide headers as JSON string (e.g., '{\"Content-Type\": \"application/json\"}')"
                    }

            # 7. Build custom_properties from flat imap and env parameters
            custom_properties_dict = {"imap": imap, "env": env}

            # Validate required parameters
            if not label:
                return {"error": "Parameter 'label' is required"}
            if not url:
                return {"error": "Parameter 'url' is required"}
            if not locations_list or len(locations_list) == 0:
                return {"error": "Parameter 'locations' is required and must contain at least one location ID"}
            if not imap:
                return {"error": "Parameter 'imap' is required"}
            if not env:
                return {"error": "Parameter 'env' is required"}

            # Validate that label starts with imap value (case insensitive)
            if not label.lower().startswith(imap.lower()):
                return {
                    "error": f"Label must start with imap value '{imap}' (case insensitive)",
                    "hint": f"Current label: '{label}', should start with: '{imap}'",
                    "example": f"{imap}_{label}" if not label.lower().startswith(imap.lower()) else label
                }

            # Validate test frequency
            valid_frequencies = [1, 5, 10, 15, 30, 60, 120, 240, 720, 1440]
            if test_frequency_int not in valid_frequencies:
                return {
                    "error": f"Invalid test_frequency: {test_frequency_int}",
                    "valid_frequencies": valid_frequencies
                }

            # Validate HTTP method
            valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
            method_upper = method.upper()
            if method_upper not in valid_methods:
                return {
                    "error": f"Invalid HTTP method: {method}",
                    "valid_methods": valid_methods
                }

            # Build the configuration object for HTTPAction using the proper model
            # Timeout must be string with unit suffix (ms, s, or m)
            timeout_str = f"{timeout_int}ms"
            
            config_dict = {
                "synthetic_type": "HTTPAction",
                "url": url,
                "operation": method_upper,
                "timeout": timeout_str,
                "follow_redirect": follow_redirects_bool,
                "allow_insecure": allow_insecure_bool,
                "expect_status": expect_status_int,
                "mark_synthetic_call": True
            }

            # Add optional headers (use parsed dict)
            if headers_dict:
                config_dict["headers"] = headers_dict

            # Add optional body for POST/PUT/PATCH
            if body and method_upper in ["POST", "PUT", "PATCH"]:
                config_dict["body"] = body

            # Add validation rules
            validation_rules = []
            if expect_json:
                validation_rules.append({
                    "type": "json",
                    "path": expect_json
                })
            if expect_match:
                validation_rules.append({
                    "type": "regex",
                    "pattern": expect_match
                })
            if validation_rules:
                config_dict["validation_rules"] = validation_rules
            
            # Create the HttpActionConfiguration object
            configuration = HttpActionConfiguration(**config_dict)

            # Build the synthetic test object with snake_case field names (use parsed values)
            test_data = {
                "label": label,
                "active": active_bool,
                "test_frequency": test_frequency_int,
                "locations": locations_list,
                "configuration": configuration,
                "custom_properties": custom_properties_dict  # Always include (built from imap + env)
            }

            # Add optional fields
            if description:
                test_data["description"] = description
            if application_id:
                test_data["application_id"] = application_id

            logger.info(f"[create_api_synthetic_monitor] Creating synthetic test: {label}")
            print(f"\n{'='*80}")
            print(f"DEBUG: Creating synthetic test with label: {label}")
            print(f"{'='*80}\n")

            # Create the synthetic test using the SyntheticTest model
            # The API expects a SyntheticTest object, not a plain dict
            synthetic_test_obj = SyntheticTest(**test_data)
            
            response = api_client.create_synthetic_test_without_preload_content(
                synthetic_test=synthetic_test_obj
            )

            # Check response status
            if response.status not in [200, 201]:
                error_message = f"Failed to create synthetic monitor: HTTP {response.status}"
                logger.error(f"[create_api_synthetic_monitor] {error_message}")
                
                try:
                    error_body = _decode_response(response)
                    logger.error(f"[create_api_synthetic_monitor] API Error Response: {error_body}")
                    return {
                        "error": error_message,
                        "details": error_body,
                        "status_code": response.status
                    }
                except Exception:
                    return {"error": error_message, "status_code": response.status}

            # Parse response
            response_text = _decode_response(response)
            created_test = json.loads(response_text)

            logger.info(f"[create_api_synthetic_monitor] Successfully created monitor: {created_test.get('id')}")

            # Build the Instana UI URL for the created test
            test_url = self._build_synthetic_test_url(created_test)

            return {
                "success": True,
                "message": f"Successfully created API synthetic monitor: {label}",
                "test": {
                    "id": created_test.get("id"),
                    "label": created_test.get("label"),
                    "url": test_url,
                    "api_endpoint": url,
                    "method": method_upper,
                    "frequency_minutes": test_frequency_int,
                    "locations": locations_list,
                    "active": created_test.get("active", True),
                    "custom_properties": custom_properties_dict
                }
            }

        except Exception as e:
            logger.error(f"[create_api_synthetic_monitor] Error: {e}", exc_info=True)
            return {"error": f"Failed to create API synthetic monitor: {e!s}"}

    def _build_synthetic_test_url(self, test: Dict[str, Any]) -> str:
        """
        Build Instana UI URL for a synthetic test.
        
        Args:
            test: Test object containing id, label, type, and locations
            
        Returns:
            Full URL to the test in Instana UI
        """
        try:
            import urllib.parse
            
            # Extract test information
            test_id = test.get('id', '')
            test_label = test.get('label', '')
            test_type = test.get('configuration', {}).get('syntheticType', 'HTTPAction')
            
            # Get location IDs (direct array of strings)
            location_ids = test.get('locations', [])
            location_ids_str = ','.join(location_ids) if location_ids else ''
            
            # Get location display labels (direct array of strings)
            location_display_labels = test.get('locationDisplayLabels', [])
            location_labels_str = ','.join(location_display_labels) if location_display_labels else ''
            
            # URL encode the components that need encoding
            encoded_label = urllib.parse.quote(test_label)
            encoded_location_labels = urllib.parse.quote(location_labels_str)
            encoded_location_ids = urllib.parse.quote(location_ids_str)
            
            # Build the full URL (remove trailing slash from base_url if present)
            base = self.base_url.rstrip('/')
            url = (
                f"{base}/#/synthetic;"
                f"testId={test_id};"
                f"testLabel={encoded_label};"
                f"type={test_type};"
                f"locationDisplayLabels={encoded_location_labels};"
                f"locationIds={encoded_location_ids};"
                f"runType=Scheduled;"
                f"executionType=Scheduled/summary"
                f"?timeline.ws=43200000&timeline.to&timeline.fm&timeline.ar=true"
            )
            
            return url
        except Exception as e:
            logger.warning(f"Failed to build URL for test {test.get('id', 'unknown')}: {e}")
            return f"{self.base_url.rstrip('/')}/#/synthetic"

# Made with Bob