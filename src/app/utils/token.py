import os

import httpx
from fastapi import status


async def check_user_credentials(token: str):
    URL = os.getenv("CREDENTIALS_URL")
    async with httpx.AsyncClient() as client:
        result = await client.post(url=URL, headers={"access-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImpvaG5Eb2UiLCJpZCI6OCwiZXhwIjoxNjE3MTM4NDE3fQ.5cSrMrDwTWLjxssQ9lf4iThlnDjKVR8u1ZKJqMNi0JQ"})
        if result.status_code == status.HTTP_200_OK:
            return result.json()
        return False