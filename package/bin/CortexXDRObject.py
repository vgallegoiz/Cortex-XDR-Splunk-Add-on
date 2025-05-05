from datetime import datetime, timezone
import secrets
import string
import hashlib
import requests
import json

class CortexXDR():
    def __init__(self, api_key, api_key_id, tenant_name, region):
        self.api_key = api_key
        self.api_key_id = api_key_id
        self.url = f"https://api-{tenant_name}.xdr.{region}.paloaltonetworks.com"

    def get_audit_management_logs(self, start_time):
        # Create login
        nonce = "".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(64)])
        timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
        auth_key = "%s%s%s" % (self.api_key, nonce, timestamp)
        auth_key = auth_key.encode("utf-8")
        api_key_hash = hashlib.sha256(auth_key).hexdigest()

        # Prepare request
        url = f"{self.url}/public_api/v1/audits/management_logs"
        headers = {
            "x-xdr-timestamp": str(timestamp),
            "x-xdr-nonce": nonce,
            "x-xdr-auth-id": str(self.api_key_id),
            "Authorization": api_key_hash
        }
        payload = { "request_data": {
            "filters": [{
                "field": "timestamp",
                "operator": "gte",
                "value": start_time
            }]
        } }
        res = requests.post(url, headers=headers, json=payload, verify=False)
        return res
    
    def get_audit_agent_logs(self, start_time):
        # Create login
        nonce = "".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(64)])
        timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
        auth_key = "%s%s%s" % (self.api_key, nonce, timestamp)
        auth_key = auth_key.encode("utf-8")
        api_key_hash = hashlib.sha256(auth_key).hexdigest()

        # Prepare requests
        url = f"{self.url}/public_api/v1/audits/agents_reports"
        headers = {
            "x-xdr-timestamp": str(timestamp),
            "x-xdr-nonce": nonce,
            "x-xdr-auth-id": str(self.api_key_id),
            "Authorization": api_key_hash
        }
        payload = { "request_data": {
            "filters": [{
                "field": "timestamp",
                "operator": "gte",
                "value": start_time
            }]
        } }
        res = requests.post(url, headers=headers, json=payload, verify=False)
        return res