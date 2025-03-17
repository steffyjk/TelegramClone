import os
import base64
import qrcode
from io import BytesIO
from django.shortcuts import render
from django.http import JsonResponse
from telethon import TelegramClient
from telethon.sessions import StringSession
from django.conf import settings
from .models import UserSession
from asgiref.sync import sync_to_async

# Telegram API credentials
API_ID = 26593961
API_HASH = 'c973c24001c8655b6fde04783dce2c41'

# Initialize Telethon client
async def init_client(session_string=None):
    return TelegramClient(StringSession(session_string), API_ID, API_HASH)

# Render login page with a unique session ID
def login_view(request):
    session_id = os.urandom(16).hex()
    UserSession.objects.create(session_id=session_id)
    return render(request, 'core/login.html', {'session_id': session_id})

# Generate QR code for login
async def generate_qr_view(request):
    session_id = request.GET.get('session_id')
    session = await sync_to_async(UserSession.objects.get)(session_id=session_id)

    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()

    # Initiate QR Login
    qr_login = await client.qr_login()

    # Generate QR code from the URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(qr_login.url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Save the session string temporarily
    session.session_string = client.session.save()
    await sync_to_async(session.save)()
    
    return JsonResponse({
        'qr_code': qr_code_base64,
        'session_id': session_id
    })

# Check login status
async def check_login_status(request):
    session_id = request.GET.get('session_id')
    session = await sync_to_async(UserSession.objects.get)(session_id=session_id)

    # Reconnect the client using the saved session string
    client = await init_client(session.session_string)
    await client.connect()

    # Check if the client is authorized (logged in)
    if await client.is_user_authorized():
        session.is_logged_in = True
        await sync_to_async(session.save)()
        await client.disconnect()
        return JsonResponse({'status': 'logged_in'})

    await client.disconnect()
    return JsonResponse({'status': 'pending'})

# Logout and clear the session
async def logout_view(request):
    session_id = request.GET.get('session_id')
    session = await sync_to_async(UserSession.objects.get)(session_id=session_id)

    # Remove session and delete from DB
    await sync_to_async(session.delete)()
    return JsonResponse({'status': 'Logged out'})
