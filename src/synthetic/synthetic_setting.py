"""
Synthetic Monitoring MCP Tools Module

This module provides synthetic monitoring-specific MCP tools for Instana.
"""

import json
import logging
from email.message import Message
from typing import Any, Dict, List, Optional

# Import the necessary classes from the SDK
try:
    from instana_client.api.synthetic_settings_api import SyntheticSettingsApi  # type: ignore[import-untyped]
    from instana_client.models.synthetic_test import SyntheticTest  # type: ignore[import-untyped]
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


class SyntheticMonitoringMCPTools(BaseInstanaClient):
    """Tools for synthetic monitoring in Instana MCP."""

    def __init__(self, read_token: str, base_url: str):
        """Initialize the Synthetic Monitoring MCP tools client."""
        super().__init__(read_token=read_token, base_url=base_url)
    
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
    
    def _format_test_summary(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a test object into a simplified summary with ID, name, and URL.
        
        Args:
            test: Full test object from API
            
        Returns:
            Simplified test summary
        """
        return {
            'id': test.get('id', ''),
            'name': test.get('label', ''),
            'url': self._build_synthetic_test_url(test)
        }

    @with_header_auth(SyntheticSettingsApi)
    async def get_synthetic_tests(
        self,
        application_id: Optional[str] = None,
        location_id: Optional[str] = None,
        credential_name: Optional[str] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        ctx=None,
        api_client=None
    ) -> Dict[str, Any]:
        """
        Get all synthetic tests with optional filtering.

        This API endpoint retrieves all synthetic monitoring tests configured in Instana.
        Supports filtering by application, location, credentials, and custom filters.
        Returns all tests without pagination.

        Args:
            application_id: Filter by application ID
            location_id: Filter by location ID
            credential_name: Filter by credential name
            sort: Sort attribute ('+' for ASC, '-' for DESC, e.g., '+label' or '-createdAt')
            filter: Custom filter string (e.g., 'label=MyTest')
            ctx: The MCP context (optional)

        Returns:
            Dictionary containing list of all synthetic tests and count
        """
        try:
            logger.debug(
                f"[get_synthetic_tests] Called with application_id={application_id}, "
                f"location_id={location_id}"
            )

            # Build query parameters - no pagination
            query_params = {}
            
            if application_id:
                query_params["application_id"] = application_id
            if location_id:
                query_params["location_id"] = location_id
            if credential_name:
                query_params["credential_name"] = credential_name
            if sort:
                query_params["sort"] = sort
            if filter:
                query_params["filter"] = filter

            logger.debug(f"[get_synthetic_tests] Query parameters: {query_params}")

            # Call the API without pagination parameters
            response = api_client.get_synthetic_tests_without_preload_content(**query_params)

            # Check response status
            if response.status != 200:
                error_message = f"Failed to get synthetic tests: HTTP {response.status}"
                logger.error(f"[get_synthetic_tests] {error_message}")
                
                try:
                    error_body = _decode_response(response)
                    logger.error(f"[get_synthetic_tests] API Error Response: {error_body}")
                    return {
                        "error": error_message,
                        "details": error_body,
                        "status_code": response.status
                    }
                except Exception:
                    return {"error": error_message, "status_code": response.status}

            # Parse response
            response_text = _decode_response(response)
            result_dict = json.loads(response_text)

            # Get all tests
            tests_list = result_dict if isinstance(result_dict, list) else []
            total_count = len(tests_list)
            
            # Format tests to simplified summary (id, name, url)
            formatted_tests = [self._format_test_summary(test) for test in tests_list]
            
            logger.info(f"[get_synthetic_tests] Successfully retrieved all {total_count} tests")

            return {
                "tests": formatted_tests,
                "count": total_count
            }

        except Exception as e:
            logger.error(f"[get_synthetic_tests] Error: {e}", exc_info=True)
    
    @with_header_auth(SyntheticSettingsApi)
    async def get_locations(
        self,
        ctx=None,
        api_client=None
    ) -> Dict[str, Any]:
        """
        Get all available synthetic monitoring locations.

        This API endpoint retrieves all synthetic monitoring locations configured in Instana.
        Returns location details including ID, display label, and other metadata.

        Args:
            ctx: The MCP context (optional)

        Returns:
            Dictionary containing list of locations and count
        """
        try:
            logger.debug("[get_locations] Fetching synthetic monitoring locations")

            # Call the API to get locations
            response = api_client.get_synthetic_locations_without_preload_content()

            # Check response status
            if response.status != 200:
                error_message = f"Failed to get synthetic locations: HTTP {response.status}"
                logger.error(f"[get_locations] {error_message}")
                
                try:
                    error_body = _decode_response(response)
                    logger.error(f"[get_locations] API Error Response: {error_body}")
                    return {"locations": [], "count": 0, "error": error_message}
                except Exception:
                    return {"locations": [], "count": 0, "error": error_message}

            # Parse response
            response_text = _decode_response(response)
            locations_list = json.loads(response_text)

            if not isinstance(locations_list, list):
                logger.warning(f"[get_locations] Unexpected response format: {type(locations_list)}")
                return {"locations": [], "count": 0, "error": "Unexpected response format"}
            
            logger.info(f"[get_locations] Successfully retrieved {len(locations_list)} locations")
            
            # Return wrapped in dict for MCP compatibility
            return {
                "locations": locations_list,
                "count": len(locations_list)
            }

        except Exception as e:
            logger.error(f"[get_locations] Error: {e}", exc_info=True)
            return {"locations": [], "count": 0, "error": str(e)}
            return {"error": f"Failed to get synthetic tests: {e!s}"}
    @with_header_auth(SyntheticSettingsApi)
    async def filter_tests_by_imap(
        self,
        imap_value: str,
        ctx=None,
        api_client=None
    ) -> Dict[str, Any]:
        """
        Filter synthetic tests by custom properties containing 'imap' key.

        This method retrieves all synthetic tests and filters them based on
        custom properties that have an 'imap' key matching the provided value.
        Returns all matching tests without pagination.

        Args:
            imap_value: The imap value to search for in custom properties
            ctx: The MCP context (optional)

        Returns:
            Dictionary containing all filtered tests that match the imap value
        """
        try:
            logger.debug(f"[filter_tests_by_imap] Searching for imap={imap_value}")

            # Get all synthetic tests without pagination
            response = api_client.get_synthetic_tests_without_preload_content()

            # Check response status
            if response.status != 200:
                error_message = f"Failed to get synthetic tests: HTTP {response.status}"
                logger.error(f"[filter_tests_by_imap] {error_message}")
                
                try:
                    error_body = _decode_response(response)
                    logger.error(f"[filter_tests_by_imap] API Error Response: {error_body}")
                    return {
                        "error": error_message,
                        "details": error_body,
                        "status_code": response.status
                    }
                except Exception:
                    return {"error": error_message, "status_code": response.status}

            # Parse response
            response_text = _decode_response(response)
            all_tests = json.loads(response_text)

            if not isinstance(all_tests, list):
                logger.warning(f"[filter_tests_by_imap] Unexpected response format: {type(all_tests)}")
                return {
                    "error": "Unexpected response format from API",
                    "tests": [],
                    "count": 0
                }

            # Filter tests by imap custom property
            filtered_tests = []
            for test in all_tests:
                # Check if test has customProperties
                custom_properties = test.get('customProperties', {})
                
                # Check if customProperties is a dict and has 'imap' key
                if isinstance(custom_properties, dict) and 'imap' in custom_properties:
                    # Get the imap value from custom properties
                    test_imap_value = custom_properties.get('imap', '')
                    
                    # Check if it matches the search value (case-insensitive)
                    if isinstance(test_imap_value, str) and test_imap_value.lower() == imap_value.lower():
                        filtered_tests.append(test)
                        logger.debug(
                            f"[filter_tests_by_imap] Match found: {test.get('label', 'Unknown')} "
                            f"with imap={test_imap_value}"
                        )

            logger.info(
                f"[filter_tests_by_imap] Found {len(filtered_tests)} tests matching imap={imap_value} "
                f"out of {len(all_tests)} total tests"
            )

            # Format tests to simplified summary (id, name, url)
            formatted_tests = [self._format_test_summary(test) for test in filtered_tests]

            return {
                "tests": formatted_tests,
                "count": len(filtered_tests),
                "search_criteria": {
                    "imap": imap_value
                }
            }

        except Exception as e:
            logger.error(f"[filter_tests_by_imap] Error: {e}", exc_info=True)
            return {"error": f"Failed to filter tests by imap: {e!s}"}

# Made with Bob
