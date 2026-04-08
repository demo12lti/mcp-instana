from typing import Optional

from src.prompts import auto_register_prompt


class SyntheticMonitoringPrompts:
    """Class containing synthetic monitoring related prompts"""

    @auto_register_prompt
    @staticmethod
    def get_synthetic_tests() -> str:
        """Retrieve all synthetic monitoring tests configured in Instana"""
        return """
        Get all synthetic tests to discover configured synthetic monitoring tests.
        Supports filtering by application, location, and credentials.
        """

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('get_synthetic_tests', cls.get_synthetic_tests),
        ]

# Made with Bob
