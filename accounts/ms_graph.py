"""
Microsoft Graph API Client
Uses Client Credentials flow (app-only access) to interact with Microsoft Graph API.
All credentials are loaded from environment variables via Django settings.
"""

import requests
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MicrosoftGraphClient:
    """
    Client for Microsoft Graph API using Client Credentials flow.
    
    This client obtains an access token using app-only authentication
    and provides methods to interact with Microsoft Graph API endpoints.
    """
    
    def __init__(self):
        """Initialize the Graph client with credentials from settings."""
        self.tenant_id = settings.MS_GRAPH_TENANT_ID
        self.client_id = settings.MS_GRAPH_CLIENT_ID
        self.client_secret = settings.MS_GRAPH_CLIENT_SECRET
        self.scope = settings.MS_GRAPH_SCOPE
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.access_token = None
        
        # Validate credentials
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing Microsoft Graph credentials. Please set TENANT_ID, "
                "CLIENT_ID, and CLIENT_SECRET in your .env file."
            )
    
    def get_access_token(self) -> str:
        """
        Obtain an access token using Client Credentials flow.
        
        Returns:
            str: Access token for Microsoft Graph API
            
        Raises:
            Exception: If token acquisition fails
        """
        try:
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': self.scope
            }
            
            response = requests.post(self.token_url, data=payload)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            if not self.access_token:
                raise ValueError("No access token received from Microsoft")
            
            logger.info("Successfully obtained Microsoft Graph access token")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to obtain access token: {str(e)}")
            raise Exception(f"Failed to obtain Microsoft Graph access token: {str(e)}")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with authorization token.
        
        Returns:
            dict: Headers with Bearer token
        """
        if not self.access_token:
            self.get_access_token()
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_users(self, top: Optional[int] = None, select: Optional[List[str]] = None) -> Dict:
        """
        Fetch users from Microsoft Graph API.
        
        Args:
            top (int, optional): Limit number of users returned (default: all)
            select (list, optional): List of user properties to return
                                    (e.g., ['displayName', 'mail', 'id'])
        
        Returns:
            dict: Response containing user data with structure:
                {
                    'value': [list of users],
                    '@odata.context': str,
                    '@odata.nextLink': str (if pagination exists)
                }
        
        Raises:
            Exception: If API request fails
        """
        try:
            endpoint = settings.MS_GRAPH_ENDPOINT_USERS
            headers = self._get_headers()
            
            # Build query parameters
            params = {}
            if top:
                params['$top'] = top
            if select:
                params['$select'] = ','.join(select)
            
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            
            users_data = response.json()
            logger.info(f"Successfully fetched {len(users_data.get('value', []))} users from Microsoft Graph")
            
            return users_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch users: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Failed to fetch users from Microsoft Graph: {str(e)}")
    
    def get_user_by_id(self, user_id: str, select: Optional[List[str]] = None) -> Dict:
        """
        Fetch a specific user by ID from Microsoft Graph API.
        
        Args:
            user_id (str): User ID or userPrincipalName
            select (list, optional): List of user properties to return
        
        Returns:
            dict: User data
        
        Raises:
            Exception: If API request fails
        """
        try:
            endpoint = f"{settings.MS_GRAPH_ENDPOINT_USERS}/{user_id}"
            headers = self._get_headers()
            
            params = {}
            if select:
                params['$select'] = ','.join(select)
            
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            
            user_data = response.json()
            logger.info(f"Successfully fetched user: {user_id}")
            
            return user_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch user {user_id}: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Failed to fetch user from Microsoft Graph: {str(e)}")
