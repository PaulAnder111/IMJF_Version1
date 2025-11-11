from django.db import migrations


def add_columns(apps, schema_editor):
    from django.db import connection
    table = 'inscriptions_inscription'
    with connection.cursor() as cur:
        # Check if 'email' column exists
        cur.execute("SHOW COLUMNS FROM {} LIKE 'email'".format(table))
        if not cur.fetchone():
            cur.execute("ALTER TABLE {} ADD COLUMN email VARCHAR(254) NULL".format(table))
        # Check if 'telephone' column exists
        cur.execute("SHOW COLUMNS FROM {} LIKE 'telephone'".format(table))
        if not cur.fetchone():
            cur.execute("ALTER TABLE {} ADD COLUMN telephone VARCHAR(20) NULL".format(table))
        # Add unique index for email if not exists
        cur.execute("SELECT COUNT(1) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND INDEX_NAME=%s", [table, 'inscriptions_inscription_email_key'])
        if cur.fetchone()[0] == 0:
            try:
                cur.execute("CREATE UNIQUE INDEX inscriptions_inscription_email_key ON {} (email)".format(table))
            except Exception:
                # ignore if cannot create (e.g., duplicate values)
                pass
        # Add unique index for telephone
        cur.execute("SELECT COUNT(1) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND INDEX_NAME=%s", [table, 'inscriptions_inscription_telephone_key'])
        if cur.fetchone()[0] == 0:
            try:
                cur.execute("CREATE UNIQUE INDEX inscriptions_inscription_telephone_key ON {} (telephone)".format(table))
            except Exception:
                pass


def reverse_func(apps, schema_editor):
    # Do not remove columns on reverse to avoid data loss
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0002_historiqueclasses_delete_historiqueclasse'),
    ]

    operations = [
        migrations.RunPython(add_columns, reverse_func),
    ]
