from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0006_producto'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='imagen_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='productos/'),
        ),
    ]
