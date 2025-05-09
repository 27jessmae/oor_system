from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import AdminProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser and associated admin profile'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Admin username')
        parser.add_argument('--email', required=True, help='Admin email')
        parser.add_argument('--password', required=True, help='Admin password')
        parser.add_argument('--first_name', default='', help='Admin first name')
        parser.add_argument('--last_name', default='', help='Admin last name')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User with username "{username}" already exists'))
            return
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User with email "{email}" already exists'))
            return
        
        # Create the admin user
        admin_user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create the admin profile
        AdminProfile.objects.create(user=admin_user)
        
        self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created successfully'))
        self.stdout.write(self.style.SUCCESS(f'You can now log in with username: {username} and your password'))
        self.stdout.write(self.style.SUCCESS(f'Access the admin dashboard at: /admin-dashboard/'))
