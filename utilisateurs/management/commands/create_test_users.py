"""
Management command pou create test users ak simulate login sessions
Itilizasyon: python manage.py create_test_users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from utilisateurs.models import UserSession
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users with simulated login sessions'

    def handle(self, *args, **options):
        test_users = [
            {'username': 'admin_test', 'email': 'admin@test.com', 'role': 'admin', 'password': 'Test123!@#'},
            {'username': 'directeur_test', 'email': 'directeur@test.com', 'role': 'directeur', 'password': 'Test123!@#'},
            {'username': 'secretaire_test', 'email': 'secretaire@test.com', 'role': 'secretaire', 'password': 'Test123!@#'},
            {'username': 'archives_test', 'email': 'archives@test.com', 'role': 'archives', 'password': 'Test123!@#'},
        ]

        created_count = 0
        session_count = 0

        for user_data in test_users:
            try:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'role': user_data['role'],
                        'is_active': True,
                        'first_name': user_data['role'].capitalize(),
                        'last_name': 'Test',
                    }
                )

                if created:
                    user.set_password(user_data['password'])
                    user.save()
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Created user: {user.username} ({user.role})")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  User already exists: {user.username}")
                    )

                # Create simulated login session
                import hashlib
                session_key = hashlib.md5(f"test_{user.id}_{timezone.now()}".encode()).hexdigest()[:32]
                session, session_created = UserSession.objects.get_or_create(
                    session_key=session_key,
                    defaults={
                        'user': user,
                        'ip_address': '127.0.0.1',
                        'user_agent': 'Mozilla/5.0 (Test User)',
                        'login_time': timezone.now() - timedelta(minutes=5),
                        'is_active': True,
                    }
                )
                
                if session_created or not session.is_active:
                    session.is_active = True
                    session.logout_time = None
                    session.save()
                    session_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ Created session for: {user.username}")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error creating user {user_data['username']}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Summary: Created {created_count} users and {session_count} sessions"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Visit: http://127.0.0.1:8000/utilisateurs/active-users/ to see all active users"
            )
        )
