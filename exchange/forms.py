from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Listing, PickupSchedule

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'major', 'phone_number')

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'major', 'phone_number')

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'author_creator', 'subject_course', 'item_type', 'condition', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class PickupScheduleForm(forms.ModelForm):
    proposed_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="Format: YYYY-MM-DD HH:MM"
    )
    
    class Meta:
        model = PickupSchedule
        fields = ['proposed_time']
