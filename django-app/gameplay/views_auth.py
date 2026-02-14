from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Count, Avg
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Play, UserProfile, Rating, Report
from .flask_client import flask_api

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or (hasattr(user, 'profile') and user.profile.is_admin())


# ========== LEVEL 16: Authentication ==========

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'reader')
        
        # Validation
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'registration/register.html')
        
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'registration/register.html')
        
         # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Update the auto-created profile with selected role
        # (Signal already created it with 'reader' role)
        if role in ['reader', 'author']:
            user.profile.role = role
            user.profile.save()
        
        # Log the user in
        login(request, user)
        messages.success(request, f'Welcome, {username}! Your account has been created.')
        return redirect('home')
    
    return render(request, 'registration/register.html')


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    """User profile page"""
    # Get user's play history
    plays = Play.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Enrich with story information
    play_data = []
    for play in plays:
        story = flask_api.get_story(play.story_id)
        ending_page = flask_api.get_page(play.ending_page_id)
        if story:
            play_data.append({
                'play': play,
                'story': story,
                'ending_page': ending_page,
            })
    
    # Get user's ratings
    ratings = Rating.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'play_data': play_data,
        'ratings': ratings,
    }
    return render(request, 'registration/profile.html', context)


# ========== LEVEL 18: Ratings and Comments ==========

@login_required
@require_POST
def rate_story(request, story_id):
    """Rate and comment on a story"""
    stars = request.POST.get('stars')
    comment = request.POST.get('comment', '')
    
    if not stars or not stars.isdigit() or not (1 <= int(stars) <= 5):
        messages.error(request, 'Please provide a rating between 1 and 5 stars.')
        return redirect('story_detail', story_id=story_id)
    
    # Update or create rating
    rating, created = Rating.objects.update_or_create(
        story_id=story_id,
        user=request.user,
        defaults={
            'stars': int(stars),
            'comment': comment,
        }
    )
    
    if created:
        messages.success(request, 'Thank you for rating this story!')
    else:
        messages.success(request, 'Your rating has been updated.')
    
    return redirect('story_detail', story_id=story_id)


@login_required
@require_POST
def delete_rating(request, rating_id):
    """Delete a user's rating"""
    rating = get_object_or_404(Rating, id=rating_id, user=request.user)
    story_id = rating.story_id
    rating.delete()
    messages.success(request, 'Your rating has been deleted.')
    return redirect('story_detail', story_id=story_id)


# ========== LEVEL 18: Reports ==========

@login_required
@require_POST
def report_story(request, story_id):
    """Report a story for moderation"""
    reason = request.POST.get('reason')
    description = request.POST.get('description', '')
    
    if not reason:
        messages.error(request, 'Please select a reason for reporting.')
        return redirect('story_detail', story_id=story_id)
    
    # Check if user already reported this story
    existing_report = Report.objects.filter(
        story_id=story_id,
        user=request.user,
        status__in=['pending', 'reviewed']
    ).first()
    
    if existing_report:
        messages.warning(request, 'You have already reported this story.')
        return redirect('story_detail', story_id=story_id)
    
    Report.objects.create(
        story_id=story_id,
        user=request.user,
        reason=reason,
        description=description
    )
    
    messages.success(request, 'Thank you for your report. Our moderators will review it.')
    return redirect('story_detail', story_id=story_id)


# ========== LEVEL 16/18: Admin Functions ==========

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or (hasattr(user, 'profile') and user.profile.is_admin())


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with moderation tools"""
    # Get reports
    pending_reports = Report.objects.filter(status='pending').select_related('user')
    reviewed_reports = Report.objects.filter(status='reviewed').select_related('user')
    
    # Get statistics
    total_stories = len(flask_api.get_stories())
    total_plays = Play.objects.count()
    total_users = User.objects.count()
    
    context = {
        'pending_reports': pending_reports,
        'reviewed_reports': reviewed_reports,
        'total_stories': total_stories,
        'total_plays': total_plays,
        'total_users': total_users,
    }
    return render(request, 'gameplay/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def suspend_story(request, story_id):
    """Suspend a story (admin only)"""
    story = flask_api.get_story(story_id)
    
    if not story:
        messages.error(request, 'Story not found.')
        return redirect('admin_dashboard')
    
    # Update story status to suspended
    updated = flask_api.update_story(story_id, status='suspended')
    
    if updated:
        messages.success(request, f'Story "{story["title"]}" has been suspended.')
    else:
        messages.error(request, 'Failed to suspend story.')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
@require_POST
def unsuspend_story(request, story_id):
    """Unsuspend a story (admin only)"""
    story = flask_api.get_story(story_id)
    
    if not story:
        messages.error(request, 'Story not found.')
        return redirect('admin_dashboard')
    
    # Update story status back to published
    updated = flask_api.update_story(story_id, status='published')
    
    if updated:
        messages.success(request, f'Story "{story["title"]}" has been unsuspended.')
    else:
        messages.error(request, 'Failed to unsuspend story.')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
@require_POST
def update_report_status(request, report_id):
    """Update a report's status"""
    report = get_object_or_404(Report, id=report_id)
    new_status = request.POST.get('status')
    
    if new_status in ['pending', 'reviewed', 'resolved', 'dismissed']:
        report.status = new_status
        if new_status in ['resolved', 'dismissed']:
            report.resolved_at = timezone.now()
            report.resolved_by = request.user
        report.save()
        messages.success(request, 'Report status updated.')
    else:
        messages.error(request, 'Invalid status.')
    
    return redirect('admin_dashboard')


# ========== LEVEL 18: Visualizations ==========

@login_required
def story_tree_view(request, story_id):
    """View story tree visualization"""
    story = flask_api.get_story(story_id)
    
    if not story:
        messages.error(request, 'Story not found.')
        return redirect('home')
    
    # Check permissions (Level 16)
    can_view = False
    if request.user.is_staff:
        can_view = True
    elif hasattr(request.user, 'profile') and request.user.profile.is_author():
        if story.get('author_id') == request.user.id:
            can_view = True
    
    # For published stories, anyone can view
    if story.get('status') == 'published':
        can_view = True
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this story tree.')
        return redirect('home')
    
    # Get tree data from Flask API
    tree_data = flask_api.get_story_tree(story_id)
    
    context = {
        'story': story,
        'tree_data': tree_data,
    }
    return render(request, 'gameplay/story_tree.html', context)


@login_required
def player_path_view(request, play_id):
    """View the path a player took through a story"""
    play = get_object_or_404(Play, id=play_id)
    
    # Check permissions
    if play.user != request.user and not is_admin(request.user):
        messages.error(request, 'You can only view your own play paths.')
        return redirect('profile')
    
    story = flask_api.get_story(play.story_id)
    
    # Get path nodes
    path_nodes = play.path_nodes.all().order_by('sequence')
    
    # Enrich with page data
    path_data = []
    for node in path_nodes:
        page = flask_api.get_page(node.page_id)
        path_data.append({
            'node': node,
            'page': page,
        })
    
    context = {
        'play': play,
        'story': story,
        'path_data': path_data,
    }
    return render(request, 'gameplay/player_path.html', context)


# ========== Statistics Page ==========

def statistics(request):
    """Global statistics page"""
    # Overall stats
    total_plays = Play.objects.count()
    total_stories = len(flask_api.get_stories(status='published'))
    total_users = User.objects.count()
    
    # Top stories by plays
    story_play_counts = Play.objects.values('story_id').annotate(
        play_count=Count('id')
    ).order_by('-play_count')[:10]
    
    top_stories = []
    for item in story_play_counts:
        story = flask_api.get_story(item['story_id'])
        if story:
            top_stories.append({
                'story': story,
                'play_count': item['play_count']
            })
    
    # Recent ratings (Level 18)
    recent_ratings = Rating.objects.select_related('user').order_by('-created_at')[:10]
    rating_data = []
    for rating in recent_ratings:
        story = flask_api.get_story(rating.story_id)
        if story:
            rating_data.append({
                'rating': rating,
                'story': story,
            })
    
    context = {
        'total_plays': total_plays,
        'total_stories': total_stories,
        'total_users': total_users,
        'top_stories': top_stories,
        'rating_data': rating_data,
    }
    return render(request, 'gameplay/statistics.html', context)
