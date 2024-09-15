# startproject/firebase_init.py
import firebase_admin
from firebase_admin import credentials
from django.conf import settings

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred)
