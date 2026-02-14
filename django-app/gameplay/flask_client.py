import requests
from django.conf import settings


class FlaskAPIClient:
    """Client for communicating with the Flask Story API"""
    
    def __init__(self):
        self.base_url = settings.FLASK_API_URL
        self.api_key = settings.FLASK_API_KEY
    
    def _get_headers(self, authenticated=False):
        """Get request headers, optionally with API key"""
        headers = {'Content-Type': 'application/json'}
        if authenticated:
            headers['X-API-KEY'] = self.api_key
        return headers
    
    # ========== READ OPERATIONS (Public) ==========
    
    def get_stories(self, status=None):
        """Get all stories, optionally filtered by status"""
        url = f"{self.base_url}/stories"
        params = {'status': status} if status else {}
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching stories: {e}")
            return []
    
    def get_story(self, story_id):
        """Get a single story by ID"""
        url = f"{self.base_url}/stories/{story_id}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching story {story_id}: {e}")
            return None
    
    def get_story_start(self, story_id):
        """Get the starting page of a story"""
        url = f"{self.base_url}/stories/{story_id}/start"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching story start {story_id}: {e}")
            return None
    
    def get_page(self, page_id):
        """Get a page with its choices"""
        url = f"{self.base_url}/pages/{page_id}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching page {page_id}: {e}")
            return None
    
    def get_story_tree(self, story_id):
        """Get the story tree for visualization (Level 18)"""
        url = f"{self.base_url}/stories/{story_id}/tree"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching story tree {story_id}: {e}")
            return None
    
    # ========== WRITE OPERATIONS (Authenticated) ==========
    
    def create_story(self, title, description='', status='draft', author_id=None, illustration_url=None):
        """Create a new story"""
        url = f"{self.base_url}/stories"
        data = {
            'title': title,
            'description': description,
            'status': status,
            'author_id': author_id,
            'illustration_url': illustration_url
        }
        try:
            response = requests.post(
                url, 
                json=data, 
                headers=self._get_headers(authenticated=True),
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating story: {e}")
            return None
    
    def update_story(self, story_id, **kwargs):
        """Update a story"""
        url = f"{self.base_url}/stories/{story_id}"
        try:
            response = requests.put(
                url, 
                json=kwargs, 
                headers=self._get_headers(authenticated=True),
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error updating story {story_id}: {e}")
            return None
    
    def delete_story(self, story_id):
        """Delete a story"""
        url = f"{self.base_url}/stories/{story_id}"
        try:
            response = requests.delete(
                url, 
                headers=self._get_headers(authenticated=True),
                timeout=5
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error deleting story {story_id}: {e}")
            return False
    
    def create_page(self, story_id, text, is_ending=False, ending_label=None, illustration_url=None):
        """Create a new page"""
        url = f"{self.base_url}/stories/{story_id}/pages"
        data = {
            'text': text,
            'is_ending': is_ending,
            'ending_label': ending_label,
            'illustration_url': illustration_url
        }
        try:
            response = requests.post(
                url, 
                json=data, 
                headers=self._get_headers(authenticated=True),
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating page: {e}")
            return None
    
    def update_page(self, page_id, **kwargs):
        """Update a page"""
        url = f"{self.base_url}/pages/{page_id}"
        try:
            response = requests.put(
                url, 
                json=kwargs, 
                headers=self._get_headers(authenticated=True),
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error updating page {page_id}: {e}")
            return None
    
    def delete_page(self, page_id):
        """Delete a page"""
        url = f"{self.base_url}/pages/{page_id}"
        try:
            response = requests.delete(
                url, 
                headers=self._get_headers(authenticated=True),
                timeout=5
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error deleting page {page_id}: {e}")
            return False
    
    def create_choice(self, page_id, text, next_page_id, dice_requirement=None):
        """Create a new choice"""
        url = f"{self.base_url}/pages/{page_id}/choices"
        data = {
            'text': text,
            'next_page_id': next_page_id,
            'dice_requirement': dice_requirement
        }
        try:
            response = requests.post(
                url, 
                json=data, 
                headers=self._get_headers(authenticated=True),
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating choice: {e}")
            return None
    
    def update_choice(self, choice_id, **kwargs):
        """Update a choice"""
        url = f"{self.base_url}/choices/{choice_id}"
        try:
            response = requests.put(
                url, 
                json=kwargs, 
                headers=self._get_headers(authenticated=True),
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error updating choice {choice_id}: {e}")
            return None
    
    def delete_choice(self, choice_id):
        """Delete a choice"""
        url = f"{self.base_url}/choices/{choice_id}"
        try:
            response = requests.delete(
                url, 
                headers=self._get_headers(authenticated=True),
                timeout=5
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error deleting choice {choice_id}: {e}")
            return False


# Global instance
flask_api = FlaskAPIClient()
