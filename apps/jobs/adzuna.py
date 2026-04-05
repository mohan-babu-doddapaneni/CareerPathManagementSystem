"""
Adzuna API client.
Free tier: 250 calls/day. Register at https://developer.adzuna.com
"""
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

ADZUNA_BASE = 'https://api.adzuna.com/v1/api/jobs'


class AdzunaClient:
    def __init__(self):
        self.app_id = settings.ADZUNA_APP_ID
        self.app_key = settings.ADZUNA_APP_KEY

    def search(self, what='', where='', country='us', page=1, results=20):
        """Search jobs. Returns list of job dicts."""
        url = f'{ADZUNA_BASE}/{country}/search/{page}'
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'results_per_page': results,
            'content-type': 'application/json',
        }
        if what:
            params['what'] = what
        if where:
            params['where'] = where

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return data.get('results', [])
        except Exception as e:
            logger.error(f'Adzuna search error: {e}')
            return []

    def get_categories(self, country='us'):
        url = f'{ADZUNA_BASE}/{country}/categories'
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json().get('results', [])
        except Exception as e:
            logger.error(f'Adzuna categories error: {e}')
            return []

    def normalize_job(self, raw):
        """Convert Adzuna raw result to our JobListing field dict."""
        salary = raw.get('salary_min') or raw.get('salary_max')
        return {
            'adzuna_id': str(raw.get('id', '')),
            'title': raw.get('title', '')[:300],
            'company': raw.get('company', {}).get('display_name', 'Unknown')[:200],
            'location': raw.get('location', {}).get('display_name', '')[:200],
            'description': raw.get('description', '')[:5000],
            'salary_min': raw.get('salary_min'),
            'salary_max': raw.get('salary_max'),
            'redirect_url': raw.get('redirect_url', ''),
            'category': raw.get('category', {}).get('label', '')[:200],
        }
