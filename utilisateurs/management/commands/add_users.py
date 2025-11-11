"""
Management command para ajoute utilisateur nan sistem
Itilizasyon: python manage.py add_users --role admin --count 2
             python manage.py add_users --role directeur --count 3
             python manage.py add_users  (load from CSV or interactive)
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from utilisateurs.models import UserSession
from django.utils import timezone
import csv
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Add new users to the system professionally'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='CSV file with user data (username,email,first_name,last_name,role,password)'
        )
        parser.add_argument(
            '--role',
            type=str,
            choices=['admin', 'directeur', 'secretaire', 'archives'],
            help='Add users with this role'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of users to create with the specified role'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Interactive mode - add users one by one'
        )

    def handle(self, *args, **options):
        if options['file']:
            self.add_from_csv(options['file'])
        elif options['interactive']:
            self.interactive_mode()
        elif options['role']:
            self.add_with_role(options['role'], options['count'])
        else:
            self.stdout.write(self.style.WARNING(
                'Usage: python manage.py add_users --file users.csv\n'
                '       python manage.py add_users --role admin --count 2\n'
                '       python manage.py add_users --interactive'
            ))

    def add_from_csv(self, filepath):
        """Add users from CSV file"""
        if not os.path.exists(filepath):
            self.stdout.write(self.style.ERROR(f'File not found: {filepath}'))
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                created_count = 0
                skipped_count = 0

                for row in reader:
                    try:
                        user, created = User.objects.get_or_create(
                            username=row['username'],
                            defaults={
                                'email': row.get('email', ''),
                                'first_name': row.get('first_name', ''),
                                'last_name': row.get('last_name', ''),
                                'role': row.get('role', 'archives'),
                                'is_active': True,
                            }
                        )

                        if created:
                            user.set_password(row.get('password', 'DefaultPass123!@#'))
                            user.save()
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"[+] Created: {user.username} ({user.role})")
                            )
                        else:
                            skipped_count += 1
                            self.stdout.write(
                                self.style.WARNING(f"[!] Exists: {user.username}")
                            )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"[-] Error: {str(e)}")
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n[SUCCESS] Summary: Created {created_count}, Skipped {skipped_count}"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"CSV Error: {str(e)}"))

    def add_with_role(self, role, count):
        """Generate and add users with specified role"""
        role_display = {
            'admin': 'Administrateur',
            'directeur': 'Directeur',
            'secretaire': 'Secrétaire',
            'archives': 'Archives',
        }

        created_count = 0
        existing_count = 0

        for i in range(1, count + 1):
            # Generate username
            base_name = role.lower()
            # Find next available number
            counter = 1
            while User.objects.filter(username=f'{base_name}_{counter:03d}').exists():
                counter += 1

            username = f'{base_name}_{counter:03d}'
            email = f'{username}@imjf.local'

            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': role_display.get(role, role),
                        'last_name': f'User {counter}',
                        'role': role,
                        'is_active': True,
                    }
                )

                if created:
                    user.set_password('Temp123!@#')  # Temporary password
                    user.save()
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[+] Created: {user.username} ({user.role})\n"
                            f"   Email: {user.email}\n"
                            f"   Temp Password: Temp123!@#"
                        )
                    )
                else:
                    existing_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"[!] Already exists: {user.username}")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"[-] Error creating {username}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'='*60}\n"
                f"Summary for role '{role}':\n"
                f"  Created: {created_count}\n"
                f"  Existing: {existing_count}\n"
                f"  Temp Password: Temp123!@#\n"
                f"{'='*60}"
            )
        )

    def interactive_mode(self):
        """Interactive mode to add users one by one"""
        self.stdout.write(
            self.style.WARNING("\n=== INTERACTIVE MODE - Add Users ===\n")
        )

        while True:
            self.stdout.write("Enter user details (or 'q' to quit):\n")

            username = input("Username: ").strip()
            if username.lower() == 'q':
                break

            # Check if exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.ERROR(f"User '{username}' already exists!"))
                continue

            email = input("Email: ").strip()
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()

            self.stdout.write("Role options: admin, directeur, secretaire, archives")
            role = input("Role: ").strip().lower()
            if role not in ['admin', 'directeur', 'secretaire', 'archives']:
                self.stdout.write(self.style.ERROR("Invalid role!"))
                continue

            password = input("Password (or press Enter for default): ").strip()
            if not password:
                password = 'TempPass123!@#'

            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    role=role,
                    is_active=True,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"[+] Created: {user.username} ({user.role})")
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"[-] Error: {str(e)}")
                )

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Done! Exiting interactive mode."))
