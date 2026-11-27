from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_pedido_direccion_pedid_metodo_pago_pedid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120)),
                ('descripcion', models.CharField(blank=True, max_length=255)),
                ('precio', models.DecimalField(decimal_places=2, default=15.0, max_digits=8)),
                ('categoria', models.CharField(choices=[('mangonada', 'Mangonada'), ('boyo', 'Boyo Cremosito')], default='boyo', max_length=20)),
                ('imagen', models.ImageField(upload_to='productos/')),
                ('activo', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
