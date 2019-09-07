# Generated by Django 2.0.4 on 2018-04-11 21:12
import logging

from django.db import migrations, models

logger = logging.getLogger(__name__)

SUFFIX = ":unsafe"


def invalidate_unencrypted_data(apps, schema_editor):
    Account = apps.get_model("accounts.Account")
    for account in Account.objects.all():
        account.user.username = f"{account.user.username}{SUFFIX}"

        if account.user.email:
            account.user.email = f"{account.user.email}{SUFFIX}"

        account.user.save()


def revalidate_unencrypted_data(apps, schema_editor):
    Account = apps.get_model("accounts.Account")
    for account in Account.objects.all():
        account.user.username = account.user.username.rstrip(SUFFIX)

        if account.user.email:
            account.user.email = account.user.email.rstrip(SUFFIX)

        account.user.save()


class Migration(migrations.Migration):

    dependencies = [("accounts", "0004_encrypt_user_data")]

    operations = [
        migrations.RunPython(
            invalidate_unencrypted_data, reverse_code=revalidate_unencrypted_data
        )
    ]