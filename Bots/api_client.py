import requests
import json
import time
from typing import Dict, Any, Optional
from uuid import uuid4

class APIClient:
    def __init__(self, base_url: str = None):
        self.user_agent = "Mozilla/5.0 (Linux; Android 9; SM-N950F Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.111 Mobile Safari/537.36"
        self.base_url = base_url or self._get_api_url()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': self.user_agent,
            'X-APP-VERSION': '3.0.11',
            'X-CHANNEL': 'WEB'
        })

    def _get_api_url(self) -> str:
        url = "https://prezaofree.com.br/main.dart.js"
        headers = {
            'User-Agent': self.user_agent,
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'X-Requested-With': 'com.cookiegames.smartcookie'
        }

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        import re
        match = re.search(r'B\.a0u=new A\.aFt\("(https:\/\/api\.prezaofree\.com\.br\/[^"]+)"', response.text)
        if match:
            return match.group(1)
        raise Exception("Não foi possível obter a URL da API")

    def _make_request(self, method: str, endpoint: str, headers: Optional[Dict[str, str]] = None, 
                     data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/{endpoint}"
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)

            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                json=data,
                params=params,
                verify=False,
                timeout=30
            )
            response.raise_for_status()

            try:
                response_data = response.json()
            except ValueError:
                response_data = {}

            return {
                'success': response.status_code == 200,
                'code': response.status_code,
                'headers': dict(response.headers),
                'body': response_data
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def guest_login(self) -> Dict[str, Any]:
        guest_uuid = f"guest_{uuid4()}"
        response = self._make_request(
            'POST',
            'auth/anms',
            headers={
                'X-USER-ID': guest_uuid,
                'X-APP-VERSION': '3.0.11',
                'X-CHANNEL': 'WEB'
            }
        )
        
        if response.get('success'):
            return {
                'success': True,
                'data': {
                    'authorization': response['headers'].get('X-Authorization'),
                    'transaction_id': response['headers'].get('X-TRANSACTION-ID'),
                    'user_id': response['body'].get('id'),
                    'type': 'plus',
                    'guest': True
                }
            }
        return {'success': False, 'error': 'Falha no login Plus'}

    def request_pin(self, phone: str) -> Dict[str, Any]:
        if not phone.isdigit() or len(phone) != 11:
            return {'success': False, 'error': 'Número de telefone inválido'}

        response = self._make_request(
            'POST',
            'pnde',
            headers={
                'X-USER-ID': phone,
                'X-APP-VERSION': '3.0.11',
                'X-CHANNEL': 'WEB'
            },
            data={'msisdn': phone}
        )
        
        return {'success': response.get('code') == 200}

    def verify_pin(self, phone: str, pin: str) -> Dict[str, Any]:
        if not pin.isdigit() or len(pin) != 6:
            return {'success': False, 'error': 'PIN inválido'}

        response = self._make_request(
            'POST',
            'vapi',
            headers={
                'X-USER-ID': phone,
                'X-PINCODE': pin,
                'X-APP-VERSION': '3.0.11',
                'X-CHANNEL': 'WEB'
            },
            data={'token': pin}
        )
        
        if response.get('code') == 200:
            return {
                'success': True,
                'data': {
                    'authorization': response['headers'].get('X-Authorization'),
                    'transaction_id': response['headers'].get('X-TRANSACTION-ID'),
                    'user_id': response['body'].get('id'),
                    'phone': phone
                }
            }
        return {'success': False, 'error': 'PIN inválido'}

    def get_balance(self, authorization: str) -> Dict[str, Any]:
        response = self._make_request(
            'GET',
            'hmld',
            headers={'X-AUTHORIZATION': authorization}
        )
        
        if response.get('code') == 200 and 'wallet' in response.get('body', {}):
            return {
                'success': True,
                'balance': response['body']['wallet'].get('balance')
            }
        return {'success': False, 'error': 'Erro ao obter saldo'}

    def get_packages(self, authorization: str) -> Dict[str, Any]:
        response = self._make_request(
            'GET',
            'przl',
            headers={'X-AUTHORIZATION': authorization}
        )
        
        if response.get('code') == 200 and 'packages' in response.get('body', {}):
            return {
                'success': True,
                'packages': response['body']['packages']
            }
        return {'success': False, 'error': 'Erro ao obter pacotes'}

    def redeem_package(self, authorization: str, package_id: str) -> Dict[str, Any]:
        response = self._make_request(
            'POST',
            'wtdr',
            headers={'X-AUTHORIZATION': authorization},
            data={'packageId': package_id, 'destinationMsisdn': None}
        )
        
        return {'success': response.get('code') == 200}

    def get_campaigns(self, authorization: str, user_id: str, campaign_id: str = '2b25a088-84ea-11ef-9082-0e639a16be05') -> Dict[str, Any]:
        response = self._make_request(
            'POST',
            f'adserver/campaign/v3/{campaign_id}',
            headers={
                'X-AUTHORIZATION': authorization,
                'X-ARTEMIS-CHANNEL-UUID': 'cfree-b22d-4079-bca5-96359b6b1f57',
                'x-access-token': '4e82abb4-2718-4d65-bcd4-c4e147c3404f'
            },
            data={
                'userId': user_id,
                'contextInfo': {
                    'os': 'WEB',
                    'brand': self.user_agent,
                    'manufacturer': 'Linux aarch64',
                    'osVersion': 'Linux aarch64',
                    'eventDate': int(time.time() * 1000),
                    'battery': '87',
                    'lat': 'Unknown',
                    'long': 'Unknown'
                }
            },
            params={'size': '100'}
        )
        
        if response.get('code') == 200:
            return {
                'success': True,
                'campaigns': response['body'].get('campaigns', [])
            }
        return {'success': False, 'error': 'Erro ao obter campanhas'}

    def track_campaign(self, authorization: str, event: str, campaign_uuid: str,
                      user_id: str, request_id: str, media_uuid: str) -> Dict[str, Any]:
        response = self._make_request(
            'POST',
            'adserver/tracker',
            headers={'X-AUTHORIZATION': authorization},
            params={
                'e': event,
                'c': campaign_uuid,
                'u': user_id,
                'requestId': request_id,
                'm': media_uuid
            }
        )
        
        return {'success': response.get('code') == 200}

    def link_guest_account(self, authorization: str, phone: str) -> Dict[str, Any]:
        response = self._make_request(
            'POST',
            'auth/anms/actv',
            headers={
                'X-AUTHORIZATION': authorization,
                'X-MSISDN': phone,
                'X-CONNECTIVITY': 'true'
            },
            data={'msisdn': phone}
        )
        
        return {'success': response.get('code') == 200}

    def verify_guest_link(self, authorization: str, phone: str, pin: str) -> Dict[str, Any]:
        response = self._make_request(
            'POST',
            'auth/anms/vldt',
            headers={
                'X-AUTHORIZATION': authorization,
                'X-MSISDN': phone,
                'X-PINCODE': pin,
                'X-CONNECTIVITY': 'true'
            },
            data={'token': pin}
        )
        
        if response.get('code') == 200:
            return {
                'success': True,
                'data': {
                    'authorization': response['headers'].get('X-Authorization'),
                    'transaction_id': response['headers'].get('X-TRANSACTION-ID'),
                    'user_id': response['body'].get('id'),
                    'phone': phone
                }
            }
        return {'success': False, 'error': 'Erro ao verificar PIN'}
