# Generated by Django 4.1 on 2022-08-15 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingridient_measurement_unit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingridient',
            name='name',
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(db_index=True, max_length=200),
        ),
    ]
