from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Note(models.Model):
    # Link each note to a specific user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # The main content of the note
    content = models.TextField(blank=True)
    # Automatically records when the note is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # This helps identify the note in the admin area
        return f'Note by {self.user.username} - {self.content[:30]}'

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        ('Happy', 'Happy'),
        ('Sad', 'Sad'),
        ('Angry', 'Angry'),
        ('Neutral', 'Neutral'), # Added a default/neutral option
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES, default='Neutral')
    journal_entry = models.TextField(blank=True)
    entry_date = models.DateField(default=timezone.now)

    class Meta:
        # Ensures a user can only have one entry per day
        unique_together = ('user', 'entry_date')

    def __str__(self):
        return f'{self.user.username}\'s mood on {self.entry_date}: {self.mood}'

