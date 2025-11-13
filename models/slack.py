"""
Data models for Slack interactions.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class SlackAction:
    """Represents a Slack button or select action."""
    action_id: str
    value: str
    action_type: str = "button"
    
    @classmethod
    def from_slack_payload(cls, action_data: Dict[str, Any]) -> "SlackAction":
        """Create SlackAction from Slack payload."""
        action_id = action_data.get('action_id') or action_data.get('name', '')
        value = action_data.get('value', '')
        action_type = action_data.get('type', 'button')
        
        # Handle select menus
        if action_type == 'static_select' and 'selected_option' in action_data:
            value = action_data['selected_option'].get('value', '')
        
        return cls(action_id=action_id, value=value, action_type=action_type)


@dataclass
class SlackUser:
    """Represents a Slack user."""
    id: str
    name: str = ""
    
    @classmethod
    def from_slack_payload(cls, user_data: Dict[str, Any]) -> "SlackUser":
        """Create SlackUser from Slack payload."""
        return cls(
            id=user_data.get('id', ''),
            name=user_data.get('name', '')
        )


@dataclass
class SlackChannel:
    """Represents a Slack channel."""
    id: str
    name: str = ""
    
    @classmethod
    def from_slack_payload(cls, channel_data: Dict[str, Any]) -> "SlackChannel":
        """Create SlackChannel from Slack payload."""
        return cls(
            id=channel_data.get('id', ''),
            name=channel_data.get('name', '')
        )


@dataclass
class QueryRequest:
    """Represents a database query request."""
    question: str
    page_number: int = 1
    user_id: str = ""
    channel_id: str = ""
    response_url: str = ""
    
    def __post_init__(self):
        """Validate the query request."""
        if not self.question.strip():
            raise ValueError("Question cannot be empty")
        if self.page_number < 1:
            raise ValueError("Page number must be positive")


@dataclass
class PlotRequest:
    """Represents a plotting request."""
    user_id: str
    x_column: str
    y_column: str
    csv_filepath: str
    channel_id: str = ""
    response_url: str = ""
    
    def __post_init__(self):
        """Validate the plot request."""
        if not all([self.user_id, self.x_column, self.y_column, self.csv_filepath]):
            raise ValueError("All plot parameters are required")


def create_slack_button(action_id: str, text: str, value: str, 
                       style: str = "primary") -> Dict[str, Any]:
    """
    Create a Slack button for legacy attachments.
    
    Args:
        action_id: Action identifier
        text: Button text
        value: Button value
        style: Button style (primary, danger, etc.)
        
    Returns:
        Button dictionary for Slack API
    """
    return {
        "name": action_id,
        "text": text,
        "type": "button",
        "value": value,
        "style": style
    }


def create_slack_attachment_with_buttons(title: str, buttons: List[Dict[str, Any]], 
                                       color: str = "#3AA3E3") -> Dict[str, Any]:
    """
    Create a Slack attachment with action buttons.
    
    Args:
        title: Attachment title
        buttons: List of button dictionaries
        color: Attachment color
        
    Returns:
        Attachment dictionary for Slack API
    """
    return {
        "text": title,
        "fallback": "Actions not available",
        "callback_id": "query_actions",
        "color": color,
        "attachment_type": "default",
        "actions": buttons
    }