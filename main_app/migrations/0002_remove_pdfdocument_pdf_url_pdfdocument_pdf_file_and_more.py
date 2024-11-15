# Generated by Django 5.1 on 2024-10-30 16:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main_app", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pdfdocument",
            name="pdf_url",
        ),
        migrations.AddField(
            model_name="pdfdocument",
            name="pdf_file",
            field=models.FileField(blank=True, null=True, upload_to="paper_file/"),
        ),
        migrations.AlterField(
            model_name="pdfdocument",
            name="num_pages",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="pdfdocument",
            name="summary",
            field=models.TextField(blank=True),
        ),
    ]
