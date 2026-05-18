from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    CREATE TABLE IF NOT EXISTS "user_emailverificationcode" (
                        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        "email" varchar(254) NOT NULL,
                        "code" varchar(6) NOT NULL,
                        "is_used" bool NOT NULL,
                        "created_at" datetime NOT NULL,
                        "user_id" bigint NOT NULL REFERENCES "user_user" ("id") DEFERRABLE INITIALLY DEFERRED
                    );
                    CREATE INDEX IF NOT EXISTS "user_emailverificationcode_user_id_idx"
                        ON "user_emailverificationcode" ("user_id");
                    """,
                    reverse_sql='DROP TABLE IF EXISTS "user_emailverificationcode";',
                )
            ],
            state_operations=[
                migrations.CreateModel(
                    name="EmailVerificationCode",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        ("email", models.EmailField(max_length=254)),
                        ("code", models.CharField(max_length=6)),
                        ("is_used", models.BooleanField(default=False)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        (
                            "user",
                            models.ForeignKey(
                                on_delete=models.deletion.CASCADE,
                                related_name="email_verification_codes",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "ordering": ("-created_at",),
                    },
                ),
            ],
        ),
    ]
