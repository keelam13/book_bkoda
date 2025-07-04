# Generated by Django 5.2.1 on 2025-06-23 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_alter_booking_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingpolicy',
            name='offline_payment_cutoff_hours_before_departure',
            field=models.PositiveIntegerField(default=6, help_text='Hours before trip departure after which only instant payment methods (e.g., Card) are allowed.'),
        ),
    ]
