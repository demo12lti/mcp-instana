from typing import Optional

from src.prompts import auto_register_prompt


class ApplicationResourcesPrompts:
    """Class containing application resources related prompts"""

    @auto_register_prompt
    @staticmethod
    def get_application_health_status(application_name: str) -> str:
        """Check whether an application is healthy using application health status, incidents, response time, and error rate. Use this for prompts like 'Is my application healthy?', 'Is application EAL-012471 healthy or not?', 'Show application health', or 'Any issues detected in my application?'"""
        return f"""
        Check application health status for:
        - Application name: {application_name}
        - Default evaluation window: last 24 hours
        - Expected output: concise health summary, not raw incidents list
        """

    @auto_register_prompt
    @staticmethod
    def application_insights_summary(window_size: int, to_time: int, name_filter: Optional[str] = None, application_boundary_scope: Optional[str] = None) -> str:
        """Retrieve a list of services within application perspectives from Instana"""
        return f"""
        Get application insights summary with:
        - Name filter: {name_filter or 'None'}
        - Window size: {window_size or '1 hour'}
        - To time: {to_time or 'now'}
        - Boundary scope: {application_boundary_scope or 'None'}
        """

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('get_application_health_status', cls.get_application_health_status),
            ('application_insights_summary', cls.application_insights_summary),
        ]
