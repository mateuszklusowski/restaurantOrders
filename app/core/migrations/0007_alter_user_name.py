# Generated by Django 4.0.3 on 2022-05-20 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_rename_restaurant_name_menu_restaurant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]