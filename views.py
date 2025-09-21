# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Note 
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Note, MoodEntry
from django.utils import timezone

# --- Public Views ---
# These pages can be seen by anyone.

def home(request):
    return render(request, 'home.html')
def home1(request):
    return render(request, 'home1.html')

def about_us(request):
    return render(request, 'aboutus.html')

# --- Authentication Views ---
# These pages handle login and registration.

def login_view(request):
    # If the user is already logged in, redirect them to the sanctuary
    if request.user.is_authenticated:
        return redirect('home1')
    return render(request, 'login.html')

def signup_view(request):
    # If the user is already logged in, redirect them to the sanctuary
    if request.user.is_authenticated:
        return redirect('home1')
    return render(request, 'signup.html')


# --- Protected Views ---
# The @login_required decorator automatically redirects non-logged-in users.

@login_required
def sanctuary(request):
    """Displays the main notes page, fetching notes for the current user."""
    notes = Note.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notes.html', {'notes': notes})

@login_required
def add_note(request):
    """Handles the creation of a new, blank note."""
    if request.method == 'POST':
        Note.objects.create(user=request.user, content='')
    return redirect('sanctuary')

@login_required
def update_note(request, note_id):
    """Handles auto-saving the content of a note via JavaScript."""
    if request.method == 'POST':
        try:
            note = Note.objects.get(id=note_id, user=request.user)
            data = json.loads(request.body)
            note.content = data.get('content', '')
            note.save()
            return JsonResponse({'status': 'success', 'message': 'Note saved!'})
        except Note.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Note not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def delete_note(request, note_id):
    """Handles the deletion of a specific note."""
    if request.method == 'POST':
        try:
            note = Note.objects.get(id=note_id, user=request.user)
            note.delete()
        except Note.DoesNotExist:
            # If the note doesn't exist, we don't need to do anything.
            pass
    return redirect('sanctuary')


@login_required
def mindmate(request):
    # This view serves your chatbot page (chat.html)
    return render(request, 'chat.html')

@login_required
def morning(request):
    """
    Displays the morning sanctuary page.
    Fetches today's mood entry and all past entries for the user.
    """
    today = timezone.now().date()
    
    today_entry, created = MoodEntry.objects.get_or_create(
        user=request.user, 
        entry_date=today
    )

    past_entries = MoodEntry.objects.filter(user=request.user).exclude(entry_date=today).order_by('-entry_date')

    context = {
        'today_entry': today_entry,
        'past_entries': past_entries
    }
    return render(request, 'morning.html', context)


@login_required
def save_mood_entry(request):
    """
    Handles creating or updating a mood entry for the current day via AJAX.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mood = data.get('mood')
            journal_entry = data.get('journal_entry')
            today = timezone.now().date()

            entry, created = MoodEntry.objects.update_or_create(
                user=request.user,
                entry_date=today,
                defaults={'mood': mood, 'journal_entry': journal_entry}
            )
            return JsonResponse({'status': 'success', 'message': 'Entry saved!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

from django.contrib.auth import login
from django.contrib.auth.models import User

def demo_login_view(request):
    """
    Finds or creates a user with the username 'demo', logs them in,
    and redirects to the main application page ('sanctuary').
    """
    # Use get_or_create to avoid creating a new user every time.
    # It returns the user object and a boolean 'created' which is True if a new user was made.
    user, created = User.objects.get_or_create(username='demo')

    # If the user was just created, we should set a default password for them.
    # This is good practice, even if we log them in directly here.
    if created:
        user.set_password('a_secure_demo_password') # You can set any password here
        user.save()
    
    # Log the user in to the current session.
    login(request, user)
    
    # Redirect to the 'sanctuary' page.
    return redirect('home1.html')


