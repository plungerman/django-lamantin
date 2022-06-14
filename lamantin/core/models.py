# -*- coding: utf-8 -*-

"""Data models."""

from django.db import models

from taggit.managers import TaggableManager


class GenericChoice(models.Model):
    """Choices for model and form fields that accept for multiple values."""

    name = models.CharField(max_length=255)
    value = models.CharField(unique=True, max_length=255)
    rank = models.IntegerField(
        verbose_name="Ranking",
        null=True,
        blank=True,
        default=0,
        help_text="A number that determines this object's position in a list.",
    )
    active = models.BooleanField(
        help_text="""
            Do you want the field to be visable on the public submission form?
        """,
        verbose_name="Is active?",
        default=True,
    )
    admin = models.BooleanField(
        verbose_name="Administrative only", default=False,
    )
    tags = TaggableManager(blank=True)

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['rank']

    def __str__(self):
        """Default data for display."""
        return self.name
