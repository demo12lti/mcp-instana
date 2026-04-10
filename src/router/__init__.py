"""
Router Module

This module contains smart router tools that provide unified interfaces
for different Instana resource types.
"""

from src.router.application_smart_router_tool import SmartRouterMCPTool
from src.router.automation_smart_router_tool import AutomationSmartRouterMCPTool
from src.router.custom_dashboard_smart_router_tool import CustomDashboardSmartRouterMCPTool
from src.router.events_smart_router_tool import SmartRouterEventsMCPTool
from src.router.maintenance_window_smart_router import MaintenanceWindowSmartRouterMCPTool
from src.router.synthetic_smart_router import SmartRouterSyntheticMCPTool
from src.router.website_smart_router import SmartRouterWebsiteMCPTool

__all__ = [
    "SmartRouterMCPTool",
    "AutomationSmartRouterMCPTool",
    "CustomDashboardSmartRouterMCPTool",
    "SmartRouterEventsMCPTool",
    "MaintenanceWindowSmartRouterMCPTool",
    "SmartRouterSyntheticMCPTool",
    "SmartRouterWebsiteMCPTool",
]

# Made with Bob
