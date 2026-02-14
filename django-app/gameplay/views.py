import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Play, PlaySession, UserProfile, Rating, Report, PlayerPath
from .flask_client import flask_api


# ========== LEVEL 10/13: Story Browsing ==========

def home(request):
    """Homepage with list of published stories"""
    # Level 13: Search and filter
    search_query = request.GET.get('search', '')
    
    # Get published stories from Flask API
    stories = flask_api.get_stories(status='published')
    
    # Level 13: Filter by search query
    if search_query and stories:
        stories = [
            s for s in stories 
            if search_query.lower() in s.get('title', '').lower() or 
               search_query.lower() in s.get('description', '').lower()
        ]
    
    # Level 18: Add rating information
    if stories:
        for story in stories:
            story_ratings = Rating.objects.filter(story_id=story['id'])
            if story_ratings.exists():
                avg_rating = sum(r.stars for r in story_ratings) / len(story_ratings)
                story['avg_rating'] = round(avg_rating, 1)
                story['rating_count'] = len(story_ratings)
            else:
                story['avg_rating'] = None
                story['rating_count'] = 0
    
    context = {
        'stories': stories,
        'search_query': search_query,
    }
    return render(request, 'gameplay/home.html', context)


def story_detail(request, story_id):
    """View story details and statistics"""
    story = flask_api.get_story(story_id)
    
    if not story:
        messages.error(request, 'Story not found.')
        return redirect('home')
    
    # Level 13: Calculate ending statistics
    plays = Play.objects.filter(story_id=story_id)
    total_plays = plays.count()
    
    ending_stats = {}
    if total_plays > 0:
        ending_counts = plays.values('ending_page_id').annotate(count=Count('id'))
        for item in ending_counts:
            page = flask_api.get_page(item['ending_page_id'])
            if page:
                ending_label = page.get('ending_label') or f"Ending {item['ending_page_id']}"
                ending_stats[ending_label] = {
                    'count': item['count'],
                    'percentage': round((item['count'] / total_plays) * 100, 1)
                }
    
    # Level 18: Get ratings and comments
    ratings = Rating.objects.filter(story_id=story_id).select_related('user').order_by('-created_at')
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()
    
    avg_rating = None
    if ratings.exists():
        avg_rating = round(sum(r.stars for r in ratings) / len(ratings), 1)
    
    # Check if user can edit (Level 16)
    can_edit = False
    if request.user.is_authenticated:
        if request.user.is_staff:
            can_edit = True
        elif hasattr(request.user, 'profile') and request.user.profile.is_author():
            if story.get('author_id') == request.user.id:
                can_edit = True
    
    # Level 13: Check for saved session
    has_saved_session = False
    if not request.user.is_authenticated:
        session_key = request.session.session_key
        if session_key:
            has_saved_session = PlaySession.objects.filter(
                session_key=session_key,
                story_id=story_id
            ).exists()
    else:
        has_saved_session = PlaySession.objects.filter(
            user=request.user,
            story_id=story_id
        ).exists()
    
    context = {
        'story': story,
        'total_plays': total_plays,
        'ending_stats': ending_stats,
        'can_edit': can_edit,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'user_rating': user_rating,
        'has_saved_session': has_saved_session,
    }
    return render(request, 'gameplay/story_detail.html', context)


# ========== LEVEL 10/13: Playing Stories ==========

def play_story(request, story_id):
    """Start or resume playing a story"""
    story = flask_api.get_story(story_id)
    
    if not story:
        messages.error(request, 'Story not found.')
        return redirect('home')
    
    # Level 16: Check if story is suspended
    if story.get('status') == 'suspended':
        messages.error(request, 'This story has been suspended by moderators.')
        return redirect('home')
    
    # Level 13: Check for saved session
    saved_session = None
    if not request.user.is_authenticated:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        saved_session = PlaySession.objects.filter(
            session_key=session_key,
            story_id=story_id
        ).first()
    else:
        saved_session = PlaySession.objects.filter(
            user=request.user,
            story_id=story_id
        ).first()
    
    # Resume or start new
    if saved_session:
        page = flask_api.get_page(saved_session.current_page_id)
    else:
        page = flask_api.get_story_start(story_id)
    
    if not page:
        messages.error(request, 'Could not load story page.')
        return redirect('home')
    
    # Level 13: Save initial session
    if not saved_session:
        if not request.user.is_authenticated:
            if not request.session.session_key:
                request.session.create()
            PlaySession.objects.create(
                session_key=request.session.session_key,
                story_id=story_id,
                current_page_id=page['id']
            )
        else:
            PlaySession.objects.create(
                user=request.user,
                session_key=request.session.session_key or '',
                story_id=story_id,
                current_page_id=page['id']
            )
    
    # Level 18: Filter choices by dice requirements
    available_choices = page.get('choices', [])
    if request.method == 'POST' and 'roll_dice' in request.POST:
        dice_roll = random.randint(1, 6)
        request.session['last_dice_roll'] = dice_roll
        messages.info(request, f'You rolled a {dice_roll}!')
    
    if not saved_session:
        # This is a new game, track the starting page
        path_key = f'path_{story_id}'
        request.session[path_key] = [{
            'page_id': page['id'],
            'choice_id': None,  # No choice led here, it's the start
            'dice_roll': None
        }]
        request.session.modified = True
    
    dice_roll = request.session.get('last_dice_roll')
    
    context = {
        'story': story,
        'page': page,
        'available_choices': available_choices,
        'dice_roll': dice_roll,
    }
    return render(request, 'gameplay/play.html', context)


def make_choice(request, story_id, choice_id):
    """Process a choice and navigate to next page"""
    if request.method != 'POST':
        return redirect('play_story', story_id=story_id)
    
    story = flask_api.get_story(story_id)
    if not story:
        messages.error(request, 'Story not found.')
        return redirect('home')
    
    # Get the choice to find next page
    current_page_id = request.POST.get('current_page_id')
    current_page = flask_api.get_page(current_page_id)
    
    if not current_page:
        messages.error(request, 'Invalid page.')
        return redirect('play_story', story_id=story_id)
    
    # Find the choice
    choice = None
    for c in current_page.get('choices', []):
        if c['id'] == int(choice_id):
            choice = c
            break
    
    if not choice:
        messages.error(request, 'Invalid choice.')
        return redirect('play_story', story_id=story_id)
    
    # Level 18: Check dice requirement
    dice_roll = None
    if choice.get('dice_requirement'):
        dice_roll = request.session.get('last_dice_roll', 0)
        if dice_roll < choice['dice_requirement']:
            messages.warning(
                request, 
                f'You need to roll at least {choice["dice_requirement"]} to choose this option!'
            )
            return redirect('play_story', story_id=story_id)
    
    # Clear dice roll after use
    if 'last_dice_roll' in request.session:
        del request.session['last_dice_roll']
    
    # Get next page
    next_page = flask_api.get_page(choice['next_page_id'])
    
    if not next_page:
        messages.error(request, 'Could not load next page.')
        return redirect('play_story', story_id=story_id)
    
    # Level 13: Update saved session
    if not request.user.is_authenticated:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        PlaySession.objects.update_or_create(
            session_key=session_key,
            story_id=story_id,
            defaults={'current_page_id': next_page['id']}
        )
    else:
        PlaySession.objects.update_or_create(
            user=request.user,
            story_id=story_id,
            defaults={'current_page_id': next_page['id']}
        )
    
    # Check if ending
    if next_page.get('is_ending'):
        # Record the play
        play = Play.objects.create(
            story_id=story_id,
            ending_page_id=next_page['id'],
            user=request.user if request.user.is_authenticated else None
        )
        
        # *** LEVEL 18: Record the player path ***
        # Get the path from session
        path_sequence = request.session.get(f'path_{story_id}', [])
        # Add the final page
        path_sequence.append({
            'page_id': next_page['id'],
            'choice_id': choice_id,
            'dice_roll': dice_roll
        })
        
        # Save path to database
        for idx, step in enumerate(path_sequence):
            PlayerPath.objects.create(
                play=play,
                page_id=step['page_id'],
                choice_id=step.get('choice_id'),
                sequence=idx + 1,
                dice_roll=step.get('dice_roll')
            )
        
        # Clear the path from session
        if f'path_{story_id}' in request.session:
            del request.session[f'path_{story_id}']
        
        # Clear the play session
        if not request.user.is_authenticated:
            PlaySession.objects.filter(
                session_key=request.session.session_key,
                story_id=story_id
            ).delete()
        else:
            PlaySession.objects.filter(
                user=request.user,
                story_id=story_id
            ).delete()
        
        return redirect('story_ending', story_id=story_id, ending_page_id=next_page['id'])
    
    # *** LEVEL 18: Track the path in session ***
    path_key = f'path_{story_id}'
    if path_key not in request.session:
        request.session[path_key] = []
    
    request.session[path_key].append({
        'page_id': current_page['id'],
        'choice_id': choice_id,
        'dice_roll': dice_roll
    })
    request.session.modified = True
    
    # Navigate to the page (reload play view)
    return redirect('play_story', story_id=story_id)


def story_ending(request, story_id, ending_page_id):
    """Display the ending page"""
    story = flask_api.get_story(story_id)
    ending_page = flask_api.get_page(ending_page_id)
    
    if not story or not ending_page:
        messages.error(request, 'Story or ending not found.')
        return redirect('home')
    
    # Level 13: Get ending statistics
    plays_with_ending = Play.objects.filter(
        story_id=story_id,
        ending_page_id=ending_page_id
    ).count()
    
    total_plays = Play.objects.filter(story_id=story_id).count()
    
    percentage = 0
    if total_plays > 0:
        percentage = round((plays_with_ending / total_plays) * 100, 1)
    
    # *** LEVEL 18: Get the current play (most recent for this user/story) ***
    play_id = None
    if request.user.is_authenticated:
        latest_play = Play.objects.filter(
            user=request.user,
            story_id=story_id,
            ending_page_id=ending_page_id
        ).order_by('-created_at').first()
        
        if latest_play:
            play_id = latest_play.id
    
    context = {
        'story': story,
        'ending_page': ending_page,
        'plays_with_ending': plays_with_ending,
        'total_plays': total_plays,
        'percentage': percentage,
        'play_id': play_id,  # ← NEW: Pass play_id to template
    }
    return render(request, 'gameplay/ending.html', context)
