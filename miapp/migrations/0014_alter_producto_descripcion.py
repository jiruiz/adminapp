# Generated by Django 4.0.6 on 2024-08-25 18:31

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('miapp', '0013_categoria_producto_descripcion_producto_categoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='descripcion',
            field=tinymce.models.HTMLField(blank=True, verbose_name='Descripción'),
        ),
    ]