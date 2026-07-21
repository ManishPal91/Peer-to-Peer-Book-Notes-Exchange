from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Listing, Wishlist, SwapMatch, PickupSchedule
from .forms import CustomUserCreationForm, ListingForm, PickupScheduleForm
from .utils import create_swap_matches, is_pickup_time_valid

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    my_listings = Listing.objects.filter(owner=request.user)
    my_wishlist = Wishlist.objects.filter(user=request.user)
    
    # Run the matching algorithm whenever the dashboard is loaded to ensure matches are up to date
    create_swap_matches(request.user)
    
    # Get active swap matches where the user is involved
    my_matches = SwapMatch.objects.filter(
        Q(user1=request.user) | Q(user2=request.user) | Q(user3=request.user)
    ).exclude(status__in=['Completed', 'Cancelled']).order_by('-updated_at')
    
    context = {
        'my_listings': my_listings,
        'my_wishlist': my_wishlist,
        'my_matches': my_matches,
    }
    return render(request, 'exchange/dashboard.html', context)

@login_required
def listing_list(request):
    # Show listings not owned by the user and currently available
    listings = Listing.objects.exclude(owner=request.user).filter(status='Available')
    return render(request, 'exchange/listing_list.html', {'listings': listings})

@login_required
def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    in_wishlist = Wishlist.objects.filter(user=request.user, listing=listing).exists()
    return render(request, 'exchange/listing_detail.html', {
        'listing': listing,
        'in_wishlist': in_wishlist
    })

@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            messages.success(request, "Listing created successfully.")
            return redirect('dashboard')
    else:
        form = ListingForm()
    return render(request, 'exchange/listing_form.html', {'form': form})

@login_required
def listing_update(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, "Listing updated successfully.")
            return redirect('dashboard')
    else:
        form = ListingForm(instance=listing)
    return render(request, 'exchange/listing_form.html', {'form': form})

@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, "Listing deleted successfully.")
        return redirect('dashboard')
    return render(request, 'exchange/listing_confirm_delete.html', {'listing': listing})

@login_required
def add_to_wishlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if listing.owner == request.user:
        messages.error(request, "You cannot add your own listing to the wishlist.")
    else:
        Wishlist.objects.get_or_create(user=request.user, listing=listing)
        messages.success(request, f"{listing.title} added to your wishlist.")
        # Trigger matching
        create_swap_matches(request.user)
    return redirect('listing_detail', pk=pk)

@login_required
def remove_from_wishlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    Wishlist.objects.filter(user=request.user, listing=listing).delete()
    messages.success(request, f"{listing.title} removed from your wishlist.")
    return redirect('dashboard')

@login_required
def match_center(request):
    all_matches = SwapMatch.objects.filter(
        Q(user1=request.user) | Q(user2=request.user) | Q(user3=request.user)
    ).order_by('-updated_at')
    
    active_matches = all_matches.exclude(status__in=['Completed', 'Cancelled'])
    past_matches = all_matches.filter(status__in=['Completed', 'Cancelled'])
    
    return render(request, 'exchange/match_center.html', {
        'active_matches': active_matches,
        'past_matches': past_matches
    })

@login_required
def schedule_pickup(request, match_id):
    match = get_object_or_404(SwapMatch, pk=match_id)
    # Ensure user is part of the match
    if request.user not in [match.user1, match.user2, match.user3]:
        messages.error(request, "You do not have permission for this schedule.")
        return redirect('match_center')
        
    try:
        schedule = match.schedule
    except PickupSchedule.DoesNotExist:
        schedule = None
        
    if request.method == 'POST':
        # Accept proposed schedule logic could go here if schedule exists and was proposed by someone else
        if schedule and 'accept' in request.POST:
            schedule.status = 'Accepted'
            schedule.save()
            match.status = 'Scheduled'
            match.save()
            messages.success(request, "Pickup schedule accepted!")
            return redirect('match_center')
            
        form = PickupScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            proposed_time = form.cleaned_data['proposed_time']
            is_valid, msg = is_pickup_time_valid(request.user, proposed_time)
            
            if is_valid:
                new_schedule = form.save(commit=False)
                new_schedule.swap_match = match
                new_schedule.status = 'Proposed'
                new_schedule.save()
                messages.success(request, "Pickup time proposed successfully.")
                return redirect('match_center')
            else:
                messages.error(request, msg)
    else:
        form = PickupScheduleForm(instance=schedule)
        
    return render(request, 'exchange/schedule_pickup.html', {
        'form': form,
        'match': match,
        'schedule': schedule
    })

@login_required
def verify_pickup(request, match_id):
    match = get_object_or_404(SwapMatch, pk=match_id)
    if request.user not in [match.user1, match.user2, match.user3]:
        messages.error(request, "You do not have permission to verify this swap.")
        return redirect('match_center')
        
    if request.method == 'POST':
        if request.user == match.user1:
            match.user1_verified = True
        elif request.user == match.user2:
            match.user2_verified = True
        elif request.user == match.user3:
            match.user3_verified = True
            
        match.save()
        messages.success(request, "You have verified the pickup.")
        
        # Check if all participants verified
        if match.is_circular:
            if match.user1_verified and match.user2_verified and match.user3_verified:
                match.status = 'Completed'
                match.save()
                
                # Mark items as swapped
                match.listing1.status = 'Swapped'
                match.listing1.save()
                match.listing2.status = 'Swapped'
                match.listing2.save()
                match.listing3.status = 'Swapped'
                match.listing3.save()
                
                messages.success(request, "Swap fully completed! All items marked as Swapped.")
        else:
            if match.user1_verified and match.user2_verified:
                match.status = 'Completed'
                match.save()
                
                # Mark items as swapped
                match.listing1.status = 'Swapped'
                match.listing1.save()
                match.listing2.status = 'Swapped'
                match.listing2.save()
                
                messages.success(request, "Swap fully completed! All items marked as Swapped.")
                
    return redirect('match_center')
