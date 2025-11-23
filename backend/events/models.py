from django.db import models


class Event(models.Model):
    EVENT_TYPES = (
        ('theatre', 'Театр'),
        ('concert', 'Концерт'),
    )

    external_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(null=True, blank=True)
    venue = models.CharField(max_length=255, blank=True)
    price = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    source_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} ({self.date})"
