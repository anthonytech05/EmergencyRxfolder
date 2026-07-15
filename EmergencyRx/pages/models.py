from django.conf import settings
from django.db import models


class Testimonial(models.Model):
    RATINGS = (
        (5, '5 — Excellent'),
        (4, '4 — Very Good'),
        (3, '3 — Good'),
        (2, '2 — Fair'),
        (1, '1 — Poor'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='testimonials'
    )
    location = models.CharField(max_length=120, blank=True, help_text='e.g. Lagos, Nigeria')
    quote = models.TextField(max_length=600)
    rating = models.PositiveSmallIntegerField(choices=RATINGS, default=5)
    is_approved = models.BooleanField(default=False, help_text='Only approved testimonials show on the homepage')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Testimonial by {self.user.get_full_name() or self.user.username} ({'approved' if self.is_approved else 'pending'})"

    @property
    def stars(self):
        return range(self.rating)
