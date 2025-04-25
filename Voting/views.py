from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Healthcheckcard, Vote, Session
from django.utils import timezone
from django.contrib import messages

# Voting Dashboard

def votingDashboard(request):
    # Get all health check cards
    health_check_cards = Healthcheckcard.objects.all()
    
    # Get current user
    user = User.objects.get(userID=request.session['user_id'])
    
    # Get active session
    active_session, created = Session.objects.get_or_create(
        sessiondate=timezone.now().date(),
        defaults={
            'description': f"Health Check Session - {timezone.now().strftime('%B %Y')}"
        }
    )
    
    # Get user's votes for this session
    user_votes = Vote.objects.filter(
        userid=user.userID,
        cardid__in=health_check_cards
    )
    
    # Calculate progress
    total_cards = health_check_cards.count()
    votes_completed = user_votes.count()
    progress_percentage = (votes_completed / total_cards) * 100 if total_cards > 0 else 0
    
    # Add this: Get the first card as current_card if no card is selected
    current_card = health_check_cards.first() if health_check_cards.exists() else None
    
    context = {
        'user': user,
        'health_check_cards': health_check_cards,
        'active_session': active_session,
        'votes_completed': votes_completed,
        'total_cards': total_cards,
        'progress_percentage': progress_percentage,
        'current_card': current_card  # Add this line
    }
    
    return render(request, 'votingDashboard.html', context)

# Vote for a specific card

def vote_card(request, card_id):
    
    
    # Get current user
    user = User.objects.get(userID=request.session['user_id'])
    
    # Get the current card
    current_card = get_object_or_404(Healthcheckcard, cardid=card_id)
    
    # Get all health check cards
    health_check_cards = Healthcheckcard.objects.all()
    
    # Get active session
    active_session, created = Session.objects.get_or_create(
        sessiondate=timezone.now().date(),
        defaults={
            'description': f"Health Check Session - {timezone.now().strftime('%B %Y')}"
        }
    )
    
    # Get user's votes for this session
    user_votes = Vote.objects.filter(
        userid=user.userID,
        cardid__in=health_check_cards
    )
    
    # Calculate progress
    total_cards = health_check_cards.count()
    votes_completed = user_votes.count()
    progress_percentage = (votes_completed / total_cards) * 100 if total_cards > 0 else 0
    
    # Get existing vote for this card if it exists
    existing_vote = Vote.objects.filter(
        userid=user.userID,
        cardid=current_card
    ).first()
    
    # Find previous and next cards for navigation
    card_ids = list(health_check_cards.values_list('cardid', flat=True))
    current_index = card_ids.index(current_card.cardid) if current_card.cardid in card_ids else 0
    
    previous_card = None
    if current_index > 0:
        previous_card = health_check_cards.get(cardid=card_ids[current_index - 1])
    
    next_card = None
    if current_index < len(card_ids) - 1:
        next_card = health_check_cards.get(cardid=card_ids[current_index + 1])
    
    context = {
        'user': user,
        'current_card': current_card,
        'health_check_cards': health_check_cards,
        'existing_vote': existing_vote,
        'votes_completed': votes_completed,
        'total_cards': total_cards,
        'progress_percentage': progress_percentage,
        'has_previous': previous_card is not None,
        'previous_card': previous_card,
        'has_next': next_card is not None,
        'next_card': next_card
    }
    
    return render(request, 'vote_card.html', context)

# Submit a vote

def submit_vote(request, card_id):
    # if not request.user.is_authenticated or request.method != 'POST':
    #     return redirect('login')
    
    # Get current user and card
    user = User.objects.get(userID=request.session['user_id'])
    current_card = get_object_or_404(Healthcheckcard, cardid=card_id)
    
    # Get form data
    vote_value = request.POST.get('voteValue')
    progress_status = request.POST.get('progressStatus')
    solutions = request.POST.get('solutions', '')
    comments = request.POST.get('comments', '')
    feedback = request.POST.get('feedback', '')
    
    # Get all form data for saving to additional tables if needed
    form_data = {
        'solutions': solutions,
        'comments': comments,
        'feedback': feedback
    }
    
    # Create or update vote
    vote, created = Vote.objects.update_or_create(
        userid=user,
        cardid=current_card,
        defaults={
            'votevalue': vote_value,
            'progressstatus': progress_status,
            'comments': comments
            
        }
    )
    
    # Get action (next or submit)
    action = request.POST.get('action')
    
    # Get all health check cards
    health_check_cards = Healthcheckcard.objects.all()
    card_ids = list(health_check_cards.values_list('cardid', flat=True))
    current_index = card_ids.index(current_card.cardid) if current_card.cardid in card_ids else 0
    
    if action == 'next' and current_index < len(card_ids) - 1:
        next_card = health_check_cards.get(cardid=card_ids[current_index + 1])
        messages.success(request, f"Vote for '{current_card.cardname}' saved successfully!")
        return redirect('vote_card', card_id=next_card.cardid)
    else:
        messages.success(request, "All votes submitted successfully!")
        return redirect('votingDashboard')