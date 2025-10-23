from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.http import JsonResponse
from django.core import serializers
from .models import Venue, Booking
from .forms import BookingForm
import json
import csv
import os


def load_venues_from_csv():
    """
    Helper function to load venues from CSV file if database is empty.
    Returns all venues from database.
    """
    venues = Venue.objects.all()
    if not venues.exists():
        # Load from CSV if no venues in database (limit to 50 venues for demo)
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Football Stadiums.csv')
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            max_venues = 50  # Limit to 50 venues for better UX
            for row in reader:
                # Skip if not UEFA or AFC (football venues)
                if row['Confederation'] not in ['UEFA', 'AFC']:
                    continue

                # Stop after reaching the limit
                if count >= max_venues:
                    break

                # Create venue with appropriate data
                venue, created = Venue.objects.get_or_create(
                    name=row['Stadium'],
                    defaults={
                        'location': f"{row['City']}, {row['Country']}",
                        'capacity': int(row['Capacity']) if row['Capacity'].isdigit() else 10000,
                        'description': f"Football stadium in {row['City']}, {row['Country']}. Home to: {row['HomeTeams']}",
                        'price_per_hour': 100.00  # Default price
                    }
                )
                if created:
                    count += 1
        venues = Venue.objects.all()
    return venues


def main_page(request):
    """
    Halaman utama menampilkan daftar venue (stadion) yang bisa dipesan.
    """
    venues = load_venues_from_csv()
    return render(request, 'booking_venue/main_page.html', {'venues': venues})


@login_required
def book_venue(request, venue_id):
    """
    View untuk melakukan booking stadion tertentu.
    - Menolak booking jika waktu sudah terpakai.
    - Menyimpan booking baru jika valid.
    """
    venue = get_object_or_404(Venue, id=venue_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']

            # Create booking manually
            booking = Booking(
                user=request.user,
                venue=venue,
                date=date,
                time=time,
                status='pending'
            )

            try:
                booking.save()
                messages.success(request, f'Booking stadion {venue.name} berhasil!')
                return redirect('booking_success')
            except Exception as e:
                messages.error(request, f'Error saving booking: {e}')
    else:
        form = BookingForm()

    return render(request, 'booking_venue/book_venue.html', {'form': form, 'venue': venue})


@login_required
def booking_success(request):
    """
    Halaman konfirmasi setelah booking berhasil.
    """
    return render(request, 'booking_venue/booking_success.html')


@login_required
def my_bookings(request):
    """
    Menampilkan daftar booking milik user yang sedang login.
    """
    bookings = Booking.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'booking_venue/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    """
    Menghapus booking jika milik user tersebut.
    """
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.delete()
        messages.success(request, 'Booking telah dibatalkan.')
    return redirect('booking_venue:my_bookings')

def api_venues(request):
    """
    API endpoint to get venues data for frontend.
    If no venues in database, load a limited number of venues from CSV file.
    """
    venues = load_venues_from_csv()

    venues_data = []
    for venue in venues:
        venues_data.append({
            'id': str(venue.id),
            'name': venue.name,
            'location': venue.location,
            'sport_type': venue.sport_type,
            'capacity': venue.capacity,
            'description': venue.description,
            'price_per_hour': float(venue.price_per_hour),
        })

    return JsonResponse({'venues': venues_data})



