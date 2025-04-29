from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Healthcheckcard, Vote, Session
from django.utils import timezone
from django.contrib import messages

# Voting Dashboard

from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Healthcheckcard, Vote, Session
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Q 


# Voting Dashboard
def votingDashboard(request):
    # Get all health check cards
    health_cards = Healthcheckcard.objects.all()

    # Get current user
    #
    if 'user_id' not in request.session:
        
         return HttpResponse("User not logged in.", status=401) 

    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         
         return HttpResponse("User not found.", status=404)

    # Get active session
    current_session_date = timezone.now().date()
    active_session, created = Session.objects.get_or_create(
        sessiondate=current_session_date,
        defaults={
            'description': f"Health Check Session - {timezone.now().strftime('%B %Y')}"
        }
    )

    # Get user's votes for current session
    user_votes_current_session = Vote.objects.filter(
        userid=user, # Используем объект user
        votingdate=current_session_date
    )

    # Calculate progress based on user's votes in the current session
    votes_completed = user_votes_current_session.values('cardid').distinct().count()
    total_cards = health_cards.count()
    progress_percentage = min(
        (votes_completed / total_cards * 100) if total_cards > 0 else 0,
        100
    )

    # Get the current card status for each card based on *user's* vote
    # Also calculate *user's* summary stats for the Card Summary section
    for card in health_cards:
        vote = user_votes_current_session.filter(cardid=card).first() 
        if vote:
            card.voted = True
            card.vote_value = vote.votevalue
            card.progress_status = vote.progressstatus
            
            card.green_count = 1 if vote.votevalue == 3 else 0
            card.amber_count = 1 if vote.votevalue == 2 else 0
            card.red_count = 1 if vote.votevalue == 1 else 0
        else:
            card.voted = False
            card.vote_value = None
            card.progress_status = None
            card.green_count = 0
            card.amber_count = 0
            card.red_count = 0

        
        total_user_votes_for_card = card.green_count + card.amber_count + card.red_count
        if total_user_votes_for_card > 0:
             card.green_percentage = (card.green_count / total_user_votes_for_card) * 100
             card.amber_percentage = (card.amber_count / total_user_votes_for_card) * 100
             card.red_percentage = (card.red_count / total_user_votes_for_card) * 100
        else:
             card.green_percentage = 0
             card.amber_percentage = 0
             card.red_percentage = 0


    
    user_voted_session_dates = Vote.objects.filter(userid=user).values_list('votingdate', flat=True).distinct()
    
    voting_sessions = Session.objects.filter(
        sessiondate__in=user_voted_session_dates
    ).order_by('-sessiondate')[:10] 

  
    for session in voting_sessions:
        session.user_vote_count = Vote.objects.filter(
            userid=user,
            votingdate=session.sessiondate
        ).count()

    # Get the first card as current_card if no card is selected
    current_card = health_cards.first() if health_cards.exists() else None

    context = {
        'user': user,
        'health_check_cards': health_cards,
        'active_session': active_session, 
        'voting_sessions': voting_sessions, 
        'votes_completed': votes_completed,
        'total_cards': total_cards,
        'progress_percentage': progress_percentage,
        'current_card': current_card,
        'active_page': 'health_cards',
        'is_historical': False 
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
    # Create new session
    new_session = Session.objects.create(
        description=f"Health Check Session - {timezone.now().strftime('%B %d, %Y')}",
        sessiondate=timezone.now().date()
    )
    messages.success(request, "New voting session started!")
    return redirect('votingDashboard')


def end_current_session(request):
    Session.objects.filter(is_active=True).update(is_active=False)
    messages.success(request, "Current voting session ended!")
    return redirect('engineer_dashboard')

def view_session(request, session_id):
    # Get the session
    session = get_object_or_404(Session, sessionid=session_id)

    # Get current user
    if 'user_id' not in request.session:
         return HttpResponse("User not logged in.", status=401)
    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         return HttpResponse("User not found.", status=404)


    # Get all health check cards
    health_cards = Healthcheckcard.objects.all()

    # Get *user's* votes for this specific session
    user_votes_in_session = Vote.objects.filter(
        userid=user,
        votingdate=session.sessiondate
    ).select_related('cardid') 
    # Calculate progress for this user in this session
    votes_completed = user_votes_in_session.values('cardid').distinct().count()
    total_cards = health_cards.count()
    progress_percentage = min(
        (votes_completed / total_cards * 100) if total_cards > 0 else 0,
        100
    )

    # Get the card status for each card based on *user's* vote in this session
    # Also prepare data for the Card Summary section (showing user's vote)
    user_votes_dict = {vote.cardid_id: vote for vote in user_votes_in_session} 

    for card in health_cards:
        vote = user_votes_dict.get(card.cardid) 
        if vote:
            card.voted = True
            card.vote_value = vote.votevalue
            card.progress_status = vote.progressstatus
           
            card.green_count = 1 if vote.votevalue == 3 else 0
            card.amber_count = 1 if vote.votevalue == 2 else 0
            card.red_count = 1 if vote.votevalue == 1 else 0
        else:
            card.voted = False
            card.vote_value = None
            card.progress_status = None
            card.green_count = 0
            card.amber_count = 0
            card.red_count = 0

        total_user_votes_for_card = card.green_count + card.amber_count + card.red_count
        if total_user_votes_for_card > 0:
             card.green_percentage = (card.green_count / total_user_votes_for_card) * 100
             card.amber_percentage = (card.amber_count / total_user_votes_for_card) * 100
             card.red_percentage = (card.red_count / total_user_votes_for_card) * 100
        else:
             card.green_percentage = 0
             card.amber_percentage = 0
             card.red_percentage = 0

    # Get the first card as current_card if no card is selected
    current_card = health_cards.first() if health_cards.exists() else None

    context = {
        'user': user,
        'health_check_cards': health_cards,
        'active_session': session, 
        'user_session_votes': user_votes_in_session, 
        'votes_completed': votes_completed, 
        'total_cards': total_cards,
        'progress_percentage': progress_percentage,
        'current_card': current_card,
        'active_page': 'health_cards', 
        'is_historical': True 
    }

    return render(request, 'votingDashboard.html', context)