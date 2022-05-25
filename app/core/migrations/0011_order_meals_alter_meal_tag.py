# Generated by Django 4.0.3 on 2022-05-25 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_meal_menu_menu_meals'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='meals',
            field=models.ManyToManyField(to='core.meal'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tag'),
        ),
    ]
