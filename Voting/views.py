from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Healthcheckcard, Vote, Session
from django.utils import timezone
from django.contrib import messages

# Voting Dashboard

def votingDashboard(request):
    # Get all health check cards
    health_cards = Healthcheckcard.objects.all()
    
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
        cardid__in=health_cards
    )
    
    # Calculate progress
    current_session_date = timezone.now().date()
    votes_completed = Vote.objects.filter(
        userid=user,
        votingdate=current_session_date
    ).values('cardid').distinct().count()
    total_cards = health_cards.count()
    progress_percentage = min(
            (votes_completed / total_cards * 100) if total_cards > 0 else 0,
            100
        )
    # Add this: Get the first card as current_card if no card is selected
    current_card = health_cards.first() if health_cards.exists() else None
    
    context = {
        'user': user,
        'health_check_cards': health_cards,
        'active_session': active_session,
        'votes_completed': votes_completed,
        'total_cards': total_cards,
        'progress_percentage': progress_percentage,
        'current_card': current_card  ,
        'active_page': 'health_cards'
    }
    
    return render(request, 'votingDashboard.html', context)

# Vote for a specific card

def vote_card(request, card_id):
    
    
    # Get current user
    user = User.objects.get(userID=request.session['user_id'])
    
    # Get the current card
    current_card = get_object_or_404(Healthcheckcard, cardid=card_id)
    
    # Get all health check cards
    health_cards = Healthcheckcard.objects.all()
    
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
        cardid__in=health_cards
        
    )
    
    # Calculate progress
    current_session_date = timezone.now().date()
    votes_completed = Vote.objects.filter(
        userid=user,
        votingdate=current_session_date
    ).values('cardid').distinct().count()
    total_cards = health_cards.count()
    progress_percentage = min(
            (votes_completed / total_cards * 100) if total_cards > 0 else 0,
            100
        )
    
    # Get existing vote for this card if it exists
    existing_vote = Vote.objects.filter(
        userid=user.userID,
        cardid=current_card
    ).order_by('-votingdate').first()  # Show most recent vote
    
    # Find previous and next cards for navigation
    card_ids = list(health_cards.values_list('cardid', flat=True))
    current_index = card_ids.index(current_card.cardid) if current_card.cardid in card_ids else 0
    
    previous_card = None
    if current_index > 0:
        previous_card = health_cards.get(cardid=card_ids[current_index - 1])
    
    next_card = None
    if current_index < len(card_ids) - 1:
        next_card = health_cards.get(cardid=card_ids[current_index + 1])
    
    context = {
        'user': user,
        'current_card': current_card,
        'health_check_cards': health_cards,
        'existing_vote': existing_vote,
        'votes_completed': votes_completed,
        'total_cards': total_cards,
        'progress_percentage': progress_percentage,
        'has_previous': previous_card is not None,
        'previous_card': previous_card,
        'has_next': next_card is not None,
        'next_card': next_card,
        'active_session': active_session,
        'active_page': 'voting'
    }
    
    return render(request, 'vote_card.html', context)

# Submit a vote

def submit_vote(request, card_id):
    # if not request.user.is_authenticated or request.method != 'POST':
    #     return redirect('login')
    
    # Get current user and card

    # Get current user and card
    user = User.objects.get(userID=request.session['user_id'])
    current_card = get_object_or_404(Healthcheckcard, cardid=card_id)
    
    # Get form data
    vote_value = request.POST.get('voteValue')
    progress_status = request.POST.get('progressStatus')
    solutions = request.POST.get('solutions', '')
    comments = request.POST.get('comments', '')
    feedback = request.POST.get('feedback', '')
    
    # Create new vote 
    try:
        Vote.objects.create(
            userid=user,
            cardid=current_card,
            votevalue=vote_value,
            progressstatus=progress_status,
            comments=comments,
            votingdate=timezone.now().date(),
            # solutions=solutions,
            # feedback=feedback
        )
        messages.success(request, "Vote submitted successfully!")
    except Exception as e:
        messages.error(request, f"Error submitting vote: {str(e)}")
        return redirect('vote_card', card_id=card_id)
    
    # Handle navigation
    action = request.POST.get('action')
    health_check_cards = Healthcheckcard.objects.all()
    card_ids = list(health_check_cards.values_list('cardid', flat=True))
    current_index = card_ids.index(current_card.cardid) if current_card.cardid in card_ids else 0
    
    if action == 'next' and current_index < len(card_ids) - 1:
        next_card = health_check_cards.get(cardid=card_ids[current_index + 1])
        return redirect('vote_card', card_id=next_card.cardid)
    
    return redirect('votingDashboard')
def start_new_session(request):
    # End current active session
    Session.objects.filter(is_active=True).update(is_active=False)
    
    # Create new session
    new_session = Session.objects.create(
        description=f"Voting Session - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
        is_active=True
    )
    messages.success(request, "New voting session started!")
    return redirect('engineer_dashboard')

def end_current_session(request):
    Session.objects.filter(is_active=True).update(is_active=False)
    messages.success(request, "Current voting session ended!")
    return redirect('engineer_dashboard')