"""
Prompts for Synthetic Monitoring Tools

This module contains prompts for creating and managing synthetic API monitors.
"""

from typing import Optional

from src.prompts import auto_register_prompt


class SyntheticToolsPrompts:
    """Class containing synthetic monitoring tools related prompts"""

    @auto_register_prompt
    @staticmethod
    def create_api_synthetic_monitor() -> str:
        """Create a new API synthetic monitor in Instana"""
        return """
        Create API synthetic monitor. SIMPLIFIED - just pass flat string parameters!
        
        EXAMPLE:
        User provides:
        - location: bxx9yzjHmKFn1u2oz3Kg
        - IMAP: EAL-012471
        - Environment: dev
        - Label: EAL-012471_MyAPI
        - URL: https://ibm.com
        
        You pass flat params (NO NESTED OBJECTS):
        params={
            "label": "EAL-012471_MyAPI",
            "url": "https://ibm.com",
            "locations": ["bxx9yzjHmKFn1u2oz3Kg"],
            "imap": "EAL-012471",
            "env": "dev"
        }
        
        STEPS:
        1. Get locations: resource_type="settings", operation="get_locations"
        2. Show user location IDs
        3. Ask: "Location ID?" → location_id
        4. Ask: "IMAP identifier?" → imap
        5. Ask: "Environment?" → env
        6. Ask: "Monitor name (must start with IMAP)?" → label
        7. Ask: "URL?" → url
        8. Pass flat params:
           params={
               "label": label,
               "url": url,
               "locations": [location_id],
               "imap": imap,
               "env": env
           }
        9. Call: resource_type="tools", operation="create_api_monitor", params=params
        
        VALIDATION:
        - Label MUST start with IMAP value
        - All parameters are simple strings (except locations which is array)
        - NO nested custom_properties object needed
        """

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('create_api_synthetic_monitor', cls.create_api_synthetic_monitor),
        ]

# Made with Bob