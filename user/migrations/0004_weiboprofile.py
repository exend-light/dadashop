# Generated by Django 3.2.13 on 2024-02-27 03:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_userpassword'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeiboProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wuid', models.CharField(db_index=True, max_length=10, unique=True, verbose_name='微博uid')),
                ('access_token', models.CharField(max_length=32, verbose_name='授权令牌')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('user_profile', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.userprofile')),
            ],
            options={
                'db_table': 'users_weibo_profile',
            },
        ),
    ]
