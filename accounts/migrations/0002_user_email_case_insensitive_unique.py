from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'CREATE UNIQUE INDEX "auth_user_email_ci_unique" '
                'ON "auth_user" (LOWER("email")) WHERE "email" <> \'\';'
            ),
            reverse_sql='DROP INDEX IF EXISTS "auth_user_email_ci_unique";',
        ),
    ]
