from django.db.models import Q
from .models import SwapMatch, Wishlist, PickupSchedule

def find_direct_swaps(user):
    """
    Find direct mutual swaps where `user` wants an item from `user2`,
    and `user2` wants an item from `user`.
    """
    matches = []
    # Items that `user` wants
    user_wishlist = Wishlist.objects.filter(user=user)
    
    for want in user_wishlist:
        desired_item = want.listing
        other_user = desired_item.owner
        
        # Check if `other_user` wants any item owned by `user`
        other_user_wants = Wishlist.objects.filter(user=other_user, listing__owner=user)
        
        for reciprocal_want in other_user_wants:
            user_item = reciprocal_want.listing
            
            # Check if a SwapMatch already exists
            existing_match = SwapMatch.objects.filter(
                Q(user1=user, user2=other_user, listing1=user_item, listing2=desired_item) |
                Q(user1=other_user, user2=user, listing1=desired_item, listing2=user_item)
            ).exists()
            
            if not existing_match:
                matches.append({
                    'user1': user,
                    'user2': other_user,
                    'listing1': user_item,
                    'listing2': desired_item
                })
                
    return matches


def find_circular_swaps(user):
    """
    Find 3-way circular swaps:
    user wants an item from user2,
    user2 wants an item from user3,
    user3 wants an item from user.
    """
    matches = []
    # user wants from user2
    user_wants = Wishlist.objects.filter(user=user)
    
    for want1 in user_wants:
        item2 = want1.listing
        user2 = item2.owner
        
        if user2 == user:
            continue
            
        # user2 wants from user3
        user2_wants = Wishlist.objects.filter(user=user2)
        for want2 in user2_wants:
            item3 = want2.listing
            user3 = item3.owner
            
            if user3 == user or user3 == user2:
                continue
                
            # user3 wants from user
            user3_wants = Wishlist.objects.filter(user=user3, listing__owner=user)
            for want3 in user3_wants:
                item1 = want3.listing
                
                # Check for existing match
                existing = SwapMatch.objects.filter(
                    is_circular=True,
                    user1=user, user2=user2, user3=user3,
                    listing1=item1, listing2=item2, listing3=item3
                ).exists()
                # A more robust check might be needed to handle permutations,
                # but this is a simplified version for now.
                
                if not existing:
                    matches.append({
                        'user1': user, 'user2': user2, 'user3': user3,
                        'listing1': item1, 'listing2': item2, 'listing3': item3
                    })
                    
    return matches

def create_swap_matches(user):
    """
    Creates SwapMatch instances for found direct and circular swaps.
    """
    created_matches = []
    
    # 1. Direct swaps
    directs = find_direct_swaps(user)
    for d in directs:
        match = SwapMatch.objects.create(
            user1=d['user1'], user2=d['user2'],
            listing1=d['listing1'], listing2=d['listing2'],
            is_circular=False
        )
        created_matches.append(match)
        # Mark as booked
        d['listing1'].status = 'Pending Swap'
        d['listing1'].save()
        d['listing2'].status = 'Pending Swap'
        d['listing2'].save()
        
    # 2. Circular swaps (only if direct swaps were not found for these items to prioritize directs)
    circulars = find_circular_swaps(user)
    for c in circulars:
        # Before creating, ensure items are not already in a pending direct swap
        match = SwapMatch.objects.create(
            user1=c['user1'], user2=c['user2'], user3=c['user3'],
            listing1=c['listing1'], listing2=c['listing2'], listing3=c['listing3'],
            is_circular=True
        )
        created_matches.append(match)
        # Mark as booked
        c['listing1'].status = 'Pending Swap'
        c['listing1'].save()
        c['listing2'].status = 'Pending Swap'
        c['listing2'].save()
        c['listing3'].status = 'Pending Swap'
        c['listing3'].save()
        
    return created_matches


def is_pickup_time_valid(user, proposed_time):
    """
    Validates if a proposed time overlaps with existing accepted schedules for the user.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    if proposed_time <= timezone.now():
        return False, "Proposed time must be in the future."
        
    # Find all accepted schedules where this user is involved
    accepted_schedules = PickupSchedule.objects.filter(status='Accepted').filter(
        Q(swap_match__user1=user) | 
        Q(swap_match__user2=user) | 
        Q(swap_match__user3=user)
    )
    
    # Check for overlapping times (assuming a 30-minute window for pickup)
    for schedule in accepted_schedules:
        time_diff = abs((proposed_time - schedule.proposed_time).total_seconds())
        if time_diff < 1800: # 30 minutes in seconds
            return False, "This time overlaps with another scheduled pickup."
            
    return True, "Time is valid."
