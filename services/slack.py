"""
Slack service for API interactions and file uploads.
"""
import requests
from typing import Tuple, Optional, Dict, Any, List
from config.settings import config


class SlackService:
    """Handles all Slack API operations."""
    
    @staticmethod
    def post_message(channel_id: str, text: Optional[str] = None, 
                    blocks: Optional[List[Dict]] = None) -> Tuple[bool, Any]:
        """
        Post a message to a Slack channel.
        
        Args:
            channel_id: Slack channel ID
            text: Message text (optional)
            blocks: Slack blocks for rich formatting (optional)
            
        Returns:
            Tuple of (success: bool, response: dict or error message)
        """
        if not config.SLACK_BOT_TOKEN:
            return False, "SLACK_BOT_TOKEN not configured"
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.SLACK_BOT_TOKEN}"
        }
        
        payload = {"channel": channel_id}
        if text:
            payload["text"] = text
        if blocks:
            payload["blocks"] = blocks
            
        try:
            response = requests.post(
                f"{config.SLACK_API_BASE}/chat.postMessage",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.ok:
                return True, response.json()
            else:
                print(f"Slack post_message error: {response.text}")
                return False, response.text
                
        except Exception as e:
            print(f"Slack post_message exception: {e}")
            return False, str(e)
    
    @staticmethod
    def upload_file(channel_id: str, file_bytes: bytes, filename: str,
                   title: Optional[str] = None, 
                   initial_comment: Optional[str] = None) -> Tuple[bool, Any]:
        """
        Upload a file to Slack using the external upload flow.
        
        Args:
            channel_id: Slack channel ID
            file_bytes: File content as bytes
            filename: Name for the uploaded file
            title: File title (optional)
            initial_comment: Comment to post with file (optional)
            
        Returns:
            Tuple of (success: bool, response: dict or error message)
        """
        if not config.SLACK_BOT_TOKEN:
            return False, "SLACK_BOT_TOKEN not configured"
            
        try:
            # Step 1: Get upload URL and file ID
            headers = {"Authorization": f"Bearer {config.SLACK_BOT_TOKEN}"}
            
            get_url_response = requests.post(
                f"{config.SLACK_API_BASE}/files.getUploadURLExternal",
                headers=headers,
                data={
                    "filename": filename,
                    "length": len(file_bytes),
                    "token": config.SLACK_BOT_TOKEN,
                },
                timeout=30,
            )
            
            if not get_url_response.ok:
                return False, f"Failed to get upload URL: {get_url_response.text}"
                
            url_data = get_url_response.json()
            if not url_data.get("ok"):
                return False, f"Slack API error: {url_data}"
                
            upload_url = url_data["upload_url"]
            file_id = url_data["file_id"]
            
            # Step 2: Upload file bytes
            upload_response = requests.post(
                upload_url,
                data=file_bytes,
                headers={"Content-Type": "application/octet-stream"},
                timeout=60,
            )
            
            if not upload_response.ok:
                return False, f"File upload failed: {upload_response.text}"
                
            # Step 3: Complete upload and share to channel
            complete_payload = {
                "files": [
                    {
                        "id": file_id,
                        "title": title or filename,
                    }
                ],
                "channel_id": channel_id,
            }
            
            if initial_comment:
                complete_payload["initial_comment"] = initial_comment
                
            complete_response = requests.post(
                f"{config.SLACK_API_BASE}/files.completeUploadExternal",
                headers={
                    "Authorization": f"Bearer {config.SLACK_BOT_TOKEN}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                json=complete_payload,
                timeout=30,
            )
            
            if not complete_response.ok:
                return False, f"Failed to complete upload: {complete_response.text}"
                
            complete_data = complete_response.json()
            if not complete_data.get("ok"):
                return False, f"Complete upload error: {complete_data}"
                
            return True, complete_data
            
        except Exception as e:
            print(f"Slack upload_file exception: {e}")
            return False, str(e)