from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from threads.models import Thread
from matches.models import Match
from booking_venue.models import Venue
from liveChat.models import Group


@login_required
def home(request):
    """Render comprehensive home page with overview of all features."""
    # Get recent threads
    recent_threads = Thread.objects.all().order_by('-created_at')[:5]

    # Get upcoming matches (using event_date field)
    upcoming_matches = Match.objects.filter(event_date__isnull=False).order_by('event_date')[:5]

    # Get available venues
    available_venues = Venue.objects.all()[:6]

    # Get active chat groups
    active_groups = Group.objects.all()[:3]

    context = {
        'recent_threads': recent_threads,
        'upcoming_matches': upcoming_matches,
        'available_venues': available_venues,
        'active_groups': active_groups,
        'user': request.user,
    }

    return render(request, 'home.html', context)
