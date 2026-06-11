from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import pandas as pd
import re


class Command(BaseCommand):
    help = "Import QuantX participants"

    def handle(self, *args, **kwargs):

        files = [
            "participants1.xlsx",
            "participants2.xlsx",
        ]

        created = 0

        for file in files:

            df = pd.read_excel(file)

            for _, row in df.iterrows():

                try:
                    name = str(row["Name"]).strip()

                    email = str(row["Email"]).strip().lower()

                    phone = re.sub(
                        r"\D",
                        "",
                        str(row["Phone Number"])
                    )

                    if (
                        not email
                        or email == "nan"
                        or len(phone) < 4
                    ):
                        continue

                    username = email

                    clean_name = "".join(
                        name.lower().split()
                    )

                    password = (
                        clean_name[:4]
                        + phone[-4:]
                    )

                    if not User.objects.filter(
                        username=username
                    ).exists():

                        User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=name,
                        )

                        created += 1

                        self.stdout.write(
                            f"Created: {email} | Password: {password}"
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(str(e))
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created} users"
            )
        )
