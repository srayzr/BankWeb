# Generated by Django 4.2.4 on 2023-08-30 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('closhbank', '0002_alter_bankaccount_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='system_balance',
            field=models.DecimalField(decimal_places=2, max_digits=15, null=True),
        ),
    ]
