#!/usr/bin/env python
"""Test email configuration"""
import os
import django
import ssl
from django.core.mail.backends.smtp import EmailBackend

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evidence_collection.settings')
django.setup()

from django.core.mail import send_mail, get_connection
from django.conf import settings

# Create a custom email backend that doesn't verify SSL certificates
class UnverifiedSSLBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        try:
            self.connection = self.connection_class(
                self.host, self.port, timeout=self.timeout
            )
            if self.use_tls:
                # Create unverified SSL context
                context = ssl._create_unverified_context()
                self.connection.starttls(context=context)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if not self.fail_silently:
                raise

try:
    # Use custom backend for testing
    connection = UnverifiedSSLBackend(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        fail_silently=False,
    )
    
    result = send_mail(
        'ComplianceGrid Test Email',
        'This is a test email from ComplianceGrid. If you receive this, your email configuration is working correctly!',
        settings.DEFAULT_FROM_EMAIL,
        ['monisa@dataterrain.com'],
        connection=connection,
        fail_silently=False,
    )
    if result:
        print('[SUCCESS] Test email sent successfully!')
        print(f'  From: {settings.DEFAULT_FROM_EMAIL}')
        print(f'  To: monisa@dataterrain.com')
        print(f'  Check your inbox (and spam folder)')
    else:
        print('[FAILED] Failed to send email')
except Exception as e:
    print(f'[ERROR] Error sending email: {str(e)}')
    print(f'\nEmail settings:')
    print(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
    print(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
    print(f'  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
    print(f'  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
    print(f'  EMAIL_HOST_PASSWORD: {"*" * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else "Not set"}')
