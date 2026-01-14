# -*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User


def get_export_dir(instance, filename):
    return "export/%(user)s/%(export)s/%(filename)s" % {
        'user': instance.export.user.id, 'export': instance.export.pk, 'filename': filename
    }


class Export(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, auto_now_add=True)
    input_file = models.FileField(upload_to=get_export_dir, null=False, max_length=1000)
    output_export = models.FileField(upload_to=get_export_dir, null=False, max_length=1000)

    def delete(self, *args, **kwargs):
        self.content.delete()
        super(Export, self).delete(*args, **kwargs)
