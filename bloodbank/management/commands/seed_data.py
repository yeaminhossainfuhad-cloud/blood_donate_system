import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from bloodbank.models import BLOOD_GROUP_CHOICES, BloodRequest, DonorProfile

LOCATIONS = ['Dhaka', 'Chattogram', 'Feni', 'Sylhet', 'Khulna', 'Rajshahi', 'Barishal']
FIRST_NAMES = ['Rahim', 'Karim', 'Fatima', 'Ayesha', 'Sabbir', 'Nusrat', 'Tanvir', 'Mim', 'Jahid', 'Rifat']
LAST_NAMES = ['Ahmed', 'Hossain', 'Islam', 'Chowdhury', 'Rahman', 'Akter', 'Khan']


class Command(BaseCommand):
    help = "Seed the database with sample donors and blood requests for demo purposes."

    def add_arguments(self, parser):
        parser.add_argument('--donors', type=int, default=12)
        parser.add_argument('--requests', type=int, default=8)

    def handle(self, *args, **options):
        donor_count = options['donors']
        request_count = options['requests']

        created_users = []
        for i in range(donor_count):
            username = f'donor{i + 1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'},
            )
            if created:
                user.set_password('password123')
                user.save()
            full_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            profile, _ = DonorProfile.objects.get_or_create(user=user)
            profile.full_name = full_name
            profile.blood_group = random.choice(BLOOD_GROUP_CHOICES)[0]
            profile.phone = f'01{random.randint(100000000, 999999999)}'
            profile.location = random.choice(LOCATIONS)
            profile.is_available = random.choice([True, True, False])
            profile.last_donation_date = date.today() - timedelta(days=random.randint(10, 400))
            profile.description = "Happy to help when I can."
            profile.save()
            created_users.append(user)
            self.stdout.write(f"Donor ready: {username} / password123")

        for i in range(request_count):
            requester = random.choice(created_users)
            BloodRequest.objects.create(
                requester=requester,
                patient_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                blood_group=random.choice(BLOOD_GROUP_CHOICES)[0],
                hospital_name=f"{random.choice(LOCATIONS)} General Hospital",
                location=random.choice(LOCATIONS),
                required_date=date.today() + timedelta(days=random.randint(1, 20)),
                bags_required=random.randint(1, 4),
                contact_number=f'01{random.randint(100000000, 999999999)}',
                description="Needed urgently, please contact if available.",
                status=random.choice([BloodRequest.STATUS_PENDING, BloodRequest.STATUS_PENDING, BloodRequest.STATUS_FULFILLED]),
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {donor_count} donors and {request_count} blood requests."
        ))
