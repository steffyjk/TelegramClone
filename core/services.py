# core/services.py

from .models import UserSession
from asgiref.sync import sync_to_async

async def confirm_login(session_id, client):
    session = await sync_to_async(UserSession.objects.get)(session_id=session_id)
    session.is_logged_in = True
    session.session_string = client.session.save()
    await sync_to_async(session.save)()
