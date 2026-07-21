from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    major = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.username

class Listing(models.Model):
    TYPE_CHOICES = (
        ('Book', 'Book'),
        ('Notes', 'Notes'),
    )
    CONDITION_CHOICES = (
        ('New', 'New'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    )
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Pending Swap', 'Pending Swap'),
        ('Swapped', 'Swapped'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    author_creator = models.CharField(max_length=255)
    subject_course = models.CharField(max_length=100)
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.owner.username}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='wanted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')

    def __str__(self):
        return f"{self.user.username} wants {self.listing.title}"

class SwapMatch(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Matched', 'Matched'),
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_matches_1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_matches_2')
    listing1 = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='swap_listing_1')
    listing2 = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='swap_listing_2')
    
    # Optional fields for 3-way circular swap support
    is_circular = models.BooleanField(default=False)
    user3 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_matches_3', null=True, blank=True)
    listing3 = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='swap_listing_3', null=True, blank=True)
    
    # Verification flags
    user1_verified = models.BooleanField(default=False)
    user2_verified = models.BooleanField(default=False)
    user3_verified = models.BooleanField(default=False)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.is_circular:
            return f"Circular Swap: {self.user1}, {self.user2}, {self.user3}"
        return f"Direct Swap: {self.user1} & {self.user2}"

class PickupSchedule(models.Model):
    swap_match = models.OneToOneField(SwapMatch, on_delete=models.CASCADE, related_name='schedule')
    proposed_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=[('Proposed', 'Proposed'), ('Accepted', 'Accepted')], default='Proposed')
    
    def __str__(self):
        return f"Schedule for {self.swap_match.id} at {self.proposed_time}"
