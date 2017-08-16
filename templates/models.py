from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Template(models.Model):
    """(Template description)"""
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    TEMPLATE_NAME = models.CharField(blank=False, max_length=100)

    class Admin:
        list_display = ("USER", "TEMPLATE_NAME")
        search_fields = ("USER", "TEMPLATE_NAME")

    def __str__(self):
        return "Template (name = %s, created by %s)" % (
            self.USER, self.TEMPLATE_NAME
        )


class Page(models.Model):
    """(Page description)"""
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    TEMPLATE = models.ForeignKey(Template, on_delete=models.CASCADE)
    PAGE_NAME = models.CharField(blank=False, max_length=100)

    class Admin:
        list_display = ("USER", "TEMPLATE", "PAGE_NAME")
        search_fields = ("USER", "TEMPLATE", "PAGE_NAME")

    def __str__(self):
        return "Page (name = %s, template = %s, created by = %s)" % (
            self.PAGE_NAME, self.TEMPLATE, self.USER
        )
