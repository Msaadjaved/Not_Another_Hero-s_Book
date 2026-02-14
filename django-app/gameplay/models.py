from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Level 10/13: Anonymous and authenticated plays
class Play(models.Model):
    """Records completed story playthroughs"""
    story_id = models.IntegerField()  # Reference to Flask API story
    ending_page_id = models.IntegerField()  # Which ending was reached
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Level 16+
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        user_info = f"User {self.user.username}" if self.user else "Anonymous"
        return f"Play of Story {self.story_id} by {user_info}"


# Level 13: Save progression for anonymous users
class PlaySession(models.Model):
    """Stores in-progress gameplay sessions"""
    session_key = models.CharField(max_length=40, db_index=True)  # Django session key
    story_id = models.IntegerField()
    current_page_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['session_key', 'story_id']
        ordering = ['-updated_at']
    
    def __str__(self):
        user_info = f"User {self.user.username}" if self.user else f"Session {self.session_key[:8]}"
        return f"Session for Story {self.story_id} - {user_info}"


# Level 16: User profiles with roles
class UserProfile(models.Model):
    """Extended user profile with role information"""
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('author', 'Author'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_author(self):
        return self.role == 'author' or self.user.is_staff
    
    def is_admin(self):
        return self.role == 'admin' or self.user.is_staff


# Level 18: Ratings and Comments
class Rating(models.Model):
    """User ratings for stories"""
    story_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['story_id', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} rated Story {self.story_id}: {self.stars} stars"


# Level 18: Reports for moderation
class Report(models.Model):
    """User reports for inappropriate content"""
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('offensive', 'Offensive Language'),
        ('copyright', 'Copyright Violation'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    story_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_reports'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report for Story {self.story_id} by {self.user.username} - {self.get_reason_display()}"


# Level 18: Player path tracking for visualization
class PlayerPath(models.Model):
    """Tracks the path a player took through a story"""
    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name='path_nodes')
    page_id = models.IntegerField()
    choice_id = models.IntegerField(null=True, blank=True)  # Choice that led here
    sequence = models.IntegerField()  # Order in the path
    dice_roll = models.IntegerField(null=True, blank=True)  # Level 18: random events
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['play', 'sequence']
    
    def __str__(self):
        return f"Path node {self.sequence} for Play {self.play.id}"
