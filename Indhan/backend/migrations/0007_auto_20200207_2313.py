# Generated by Django 2.2.4 on 2020-02-07 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_auto_20200207_2149'),
    ]

    operations = [
        migrations.RenameField(
            model_name='petrolpump',
            old_name='behavior',
            new_name='air',
        ),
        migrations.AddField(
            model_name='petrolpump',
            name='foodrating',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='petrolpump',
            name='bathroom',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='petrolpump',
            name='cashless',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='petrolpump',
            name='food',
            field=models.FloatField(default=0),
        ),
    ]
