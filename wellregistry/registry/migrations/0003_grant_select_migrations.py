"""
After the registry table is created, this will grant access to the client login
"""
import sys

from django.db import migrations
from django.conf import settings

env = settings.ENVIRONMENT


class Migration(migrations.Migration):
    """
    Django Migration.

    SQL to grant the client access to the registry table.
    """
    initial = False

    # this could truly be dependent on 0000_create_app_users but I do not know if Django allows
    dependencies = [('registry', '0002_grant_client_user')]

    if 'test' in sys.argv:
        operations = []
    else:
        operations = [
            # grant SELECT to app user -- Django seems to want to verify migrations are up to date.
            migrations.RunSQL(
                sql=f"""
                            GRANT SELECT
                            ON public.django_migrations
                            TO {env['APP_CLIENT_USERNAME']}
                        """,
                reverse_sql=f"""
                            REVOKE SELECT
                            ON public.django_migrations
                            FROM {env['APP_CLIENT_USERNAME']}
                        """),
        ]
