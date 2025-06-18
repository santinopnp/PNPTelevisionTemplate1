# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in .env file")

# Parse ADMIN_IDS
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = []
if admin_ids_str:
    try:
        ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip().isdigit()]
    except ValueError as e:
        print(f"Warning: Error parsing ADMIN_IDS: {e}")

# Payment settings
BOLD_IDENTITY_KEY = os.getenv("BOLD_IDENTITY_KEY", "LgANsB3U4Qsr1hWWG3dBFXdxPZd4VheS-bvuk2Vzi7E")

PLAN_LINK_IDS = {
    "Trial Trip": "LNK_O7C5LTPYFP",
    "Monthly Adventure": "LNK_52ZQ7A0I9I",
    "Frequent Flyer": "LNK_468D3W49LB",
    "Half-Year Escape": "LNK_EMVGMPYMGJ",
    "Full Year Experience": "LNK_253P067SB1",
    "Lifetime Access": "LNK_PNM53KLD99"
}

def generate_bold_link(link_id: str, user_id: int, plan_id: str) -> str:
    """Generate a Bold.co payment URL including the plan identifier."""

    return (
        f"https://checkout.bold.co/payment/{link_id}"
        f"?identity_key={BOLD_IDENTITY_KEY}"
        f"&metadata[user_id]={user_id}"
        f"&metadata[plan_id]={plan_id}"
    )

# Channel settings
CHANNELS = {
    "channel_1":-1002068120499
}

ALL_CHANNEL_IDS = list(CHANNELS.values())

# Plan configurations
# Plan configurations with multilingual descriptions
PLAN_DESCRIPTIONS = {
    "en": "Access to **2 exclusive channels** featuring explicit PNP videos – **Latino men smoking and slamming**.\n• **200+ clips**, each averaging around **10 minutes** of intense action.\n• **Invitation to our virtual slam & smoke parties** – join the vibe, live and uncensored.\n• **Bonus:** Early access to our **upcoming web app** – launching soon!",
    "es": "Acceso a **2 canales exclusivos** con videos explícitos PNP – **Hombres latinos fumando y slamming**.\n• **200+ clips**, cada uno promedio de **10 minutos** de acción intensa.\n• **Invitación a nuestras fiestas virtuales de slam & smoke** – únete al ambiente, en vivo y sin censura.\n• **Bonus:** Acceso anticipado a nuestra **próxima aplicación web** – ¡próximamente!"
}

PLANS = {
    "trial": {
        "name": "Trial Trip",
        "price": "$14.99",
        "duration_days": 7,
        "link_id": "LNK_O7C5LTPYFP"
    },
    "monthly": {
        "name": "Monthly Adventure", 
        "price": "$24.99",
        "duration_days": 30,
        "link_id": "LNK_52ZQ7A0I9I"
    },
    "vip": {
        "name": "Frequent Flyer",

        "price": "$49.99",
        "duration_days": 90,
        "link_id": "LNK_468D3W49LB"
    },
    "halfyear": {
        "name": "Half-Year Escape",
        "price": "$79.99",
        "duration_days": 180,
        "link_id": "LNK_EMVGMPYMGJ"
    },
    "yearly": {
        "name": "Full Year Experience",
        "price": "$99.99",
        "duration_days": 365,
        "link_id": "LNK_253P067SB1"
    },
    "lifetime": {
        "name": "Lifetime Access",
        "price": "$249.99",
        "duration_days": 3650,
        "link_id": "LNK_PNM53KLD99"
    }
}

# Admin panel settings
ADMIN_PORT = int(os.getenv("ADMIN_PORT", 8080))
ADMIN_HOST = os.getenv("ADMIN_HOST", "0.0.0.0")

# Database settings
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json")
DATABASE_URL = os.getenv("DATABASE_URL")
