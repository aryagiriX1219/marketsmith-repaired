from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import pandas as pd
import re

class Command(BaseCommand):
help = "Import QuantX participants"

```
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

                roll = str(row["Roll No."]).strip()

                phone = re.sub(
                    r"\\D",
                    "",
                    str(row["Phone Number"])
                )

                if (
                    not roll
                    or roll == "nan"
                    or len(phone) < 4
                ):
                    continue

                username = roll

                clean_name = "".join(
                    name.lower().split()
                )

                password = (
                    clean_name[:4]
                    + phone[-4:]
                )

                email = ""

                if "Email" in row:
                    email = str(
                        row["Email"]
                    ).strip()

                if not User.objects.filter(
                    username=username
                ).exists():

                    User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=name,
                        email=email,
                    )

                    created += 1

            except Exception as e:
                print(e)

    self.stdout.write(
        self.style.SUCCESS(
            f"Created {created} users"
        )
    )
```
