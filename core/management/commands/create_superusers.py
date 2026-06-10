from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create 6 superusers (a, b, c, d, e, f) with password 1'

    def handle(self, *args, **options):
        usernames = ['a', 'b', 'c', 'd', 'e', 'f']
        password = '1'

        for username in usernames:
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Superuser {username} already exists')
                )
            else:
                User.objects.create_superuser(
                    username=username,
                    email=f'{username}@example.com',
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser {username}')
                )
