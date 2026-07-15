from django.contrib import admin

from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'location', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('user__username', 'quote', 'location')
    actions = ('approve_testimonials',)

    @admin.action(description='Approve selected testimonials')
    def approve_testimonials(self, request, queryset):
        queryset.update(is_approved=True)
