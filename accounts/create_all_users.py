# create all users with temporary passwords and must_change_password flag
import os
from dotenv import load_dotenv
from django.contrib.auth import get_user_model
from accounts.models import Role

load_dotenv()

User = get_user_model()
role = Role.objects.get(name="student")

# collect all USER*_EMAIL and USER*_PASS pairs from the .env
users = []
for x in range(1, 200):
    email = os.getenv(f"USER{x}_EMAIL")
    password = os.getenv(f"USER{x}_PASS")
    if email and password:
        users.append((email, password))

for email, password in users:
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_user(username=email, email=email, password=password, role=role, must_change_password=True)
        print(f"Created: {email}")
    else:
        print(f"User already exists: {email}")
