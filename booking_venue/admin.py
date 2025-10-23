from django.contrib import admin
from .models import Venue, Booking

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'price_per_hour')
    search_fields = ('name', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'venue', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'venue__name')
