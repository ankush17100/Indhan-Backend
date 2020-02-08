# Generated by Django 3.0.2 on 2020-02-08 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_auto_20200207_2332'),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=500)),
            ],
        ),
        migrations.AddField(
            model_name='useraccount',
            name='manufacture_year',
            field=models.CharField(default=2010, max_length=20),
            preserve_default=False,
        ),
    ]
