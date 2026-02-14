from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import UserProfile
from .flask_client import flask_api


# ========== LEVEL 10/13: Story Creation (Author Tools) ==========

@login_required  # ← REQUIRED!
def author_dashboard(request):
    """Dashboard for authors to manage their stories - Level 16 requires login"""
    # Level 16: Require authentication and author role
    if not (hasattr(request.user, 'profile') and request.user.profile.is_author()):
        if not request.user.is_staff:
            messages.error(request, 'You need author privileges to access this page.')
            return redirect('home')
    
    # Get all stories (at Level 10/13, show all; at Level 16+, filter by author)
    all_stories = flask_api.get_stories()
    
    # Level 16: Filter by author
    if request.user.is_authenticated and not request.user.is_staff:
        my_stories = [s for s in all_stories if s.get('author_id') == request.user.id]
    else:
        my_stories = all_stories
    
    # Separate by status
    drafts = [s for s in my_stories if s.get('status') == 'draft']
    published = [s for s in my_stories if s.get('status') == 'published']
    suspended = [s for s in my_stories if s.get('status') == 'suspended']
    
    context = {
        'drafts': drafts,
        'published': published,
        'suspended': suspended,
    }
    return render(request, 'gameplay/author_dashboard.html', context)


@login_required  # ← REQUIRED!
def create_story(request):
    """Create a new story - Level 16 requires login"""
    # Level 16: Require authentication and author role
    if not (hasattr(request.user, 'profile') and request.user.profile.is_author()):
        if not request.user.is_staff:
            messages.error(request, 'You need author privileges to create stories.')
            return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        status = request.POST.get('status', 'draft')
        illustration_url = request.POST.get('illustration_url', '')
        
        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'gameplay/create_story.html')
        
        # Level 16: Add author_id
        author_id = request.user.id if request.user.is_authenticated else None
        
        story = flask_api.create_story(
            title=title,
            description=description,
            status=status,
            author_id=author_id,
            illustration_url=illustration_url if illustration_url else None
        )
        
        if story:
            messages.success(request, f'Story "{title}" created successfully!')
            return redirect('edit_story', story_id=story['id'])
        else:
            messages.error(request, 'Failed to create story. Please try again.')
    
    return render(request, 'gameplay/create_story.html')


@login_required  # ← REQUIRED!
def edit_story(request, story_id):
    """Edit story metadata and manage pages - Level 16 requires ownership"""
    story = flask_api.get_story(story_id)
    
    if not story:
        messages.error(request, 'Story not found.')
        return redirect('author_dashboard')
    
    # Level 16: Check ownership
    if not request.user.is_staff:
        if story.get('author_id') != request.user.id:
            messages.error(request, 'You can only edit your own stories.')
            return redirect('author_dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        status = request.POST.get('status')
        illustration_url = request.POST.get('illustration_url', '')
        
        update_data = {}
        if title:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if status:
            update_data['status'] = status
        if illustration_url:
            update_data['illustration_url'] = illustration_url
        
        updated_story = flask_api.update_story(story_id, **update_data)
        
        if updated_story:
            messages.success(request, 'Story updated successfully!')
            return redirect('edit_story', story_id=story_id)
        else:
            messages.error(request, 'Failed to update story.')
    
    context = {
        'story': story,
    }
    return render(request, 'gameplay/edit_story.html', context)


@login_required  # ← REQUIRED!
@require_POST
def delete_story(request, story_id):
    """Delete a story - Level 16 requires ownership"""
    story = flask_api.get_story(story_id)
    
    if not story:
        messages.error(request, 'Story not found.')
        return redirect('author_dashboard')
    
    # Level 16: Check ownership
    if not request.user.is_staff:
        if story.get('author_id') != request.user.id:
            messages.error(request, 'You can only delete your own stories.')
            return redirect('author_dashboard')
    
    if flask_api.delete_story(story_id):
        messages.success(request, 'Story deleted successfully!')
    else:
        messages.error(request, 'Failed to delete story.')
    
    return redirect('author_dashboard')


@login_required  # ← REQUIRED!
def create_page(request, story_id):
    """Create a new page for a story"""
    story = flask_api.get_story(story_id)
    
    if not story:
        messages.error(request, 'Story not found.')
        return redirect('author_dashboard')
    
    # Level 16: Check ownership
    if not request.user.is_staff:
        if story.get('author_id') != request.user.id:
            messages.error(request, 'You can only edit your own stories.')
            return redirect('author_dashboard')
    
    if request.method == 'POST':
        text = request.POST.get('text')
        is_ending = request.POST.get('is_ending') == 'on'
        ending_label = request.POST.get('ending_label', '')
        illustration_url = request.POST.get('illustration_url', '')
        
        if not text:
            messages.error(request, 'Page text is required.')
            return render(request, 'gameplay/create_page.html', {'story': story})
        
        page = flask_api.create_page(
            story_id=story_id,
            text=text,
            is_ending=is_ending,
            ending_label=ending_label if ending_label else None,
            illustration_url=illustration_url if illustration_url else None
        )
        
        if page:
            messages.success(request, 'Page created successfully!')
            return redirect('edit_story', story_id=story_id)
        else:
            messages.error(request, 'Failed to create page.')
    
    context = {
        'story': story,
    }
    return render(request, 'gameplay/create_page.html', context)


@login_required  # ← REQUIRED!
def edit_page(request, page_id):
    """Edit a page"""
    page = flask_api.get_page(page_id)
    
    if not page:
        messages.error(request, 'Page not found.')
        return redirect('author_dashboard')
    
    story = flask_api.get_story(page['story_id'])
    
    # Level 16: Check ownership
    if not request.user.is_staff:
        if story.get('author_id') != request.user.id:
            messages.error(request, 'You can only edit your own stories.')
            return redirect('author_dashboard')
    
    if request.method == 'POST':
        text = request.POST.get('text')
        is_ending = request.POST.get('is_ending') == 'on'
        ending_label = request.POST.get('ending_label', '')
        illustration_url = request.POST.get('illustration_url', '')
        
        update_data = {}
        if text:
            update_data['text'] = text
        update_data['is_ending'] = is_ending
        if ending_label:
            update_data['ending_label'] = ending_label
        if illustration_url:
            update_data['illustration_url'] = illustration_url
        
        updated_page = flask_api.update_page(page_id, **update_data)
        
        if updated_page:
            messages.success(request, 'Page updated successfully!')
            return redirect('edit_story', story_id=page['story_id'])
        else:
            messages.error(request, 'Failed to update page.')
    
    context = {
        'story': story,
        'page': page,
    }
    return render(request, 'gameplay/edit_page.html', context)


@login_required  # ← REQUIRED!
@require_POST
def delete_page(request, page_id):
    """Delete a page"""
    page = flask_api.get_page(page_id)
    
    if not page:
        messages.error(request, 'Page not found.')
        return redirect('author_dashboard')
    
    story_id = page['story_id']
    story = flask_api.get_story(story_id)
    
    # Level 16: Check ownership
    if not request.user.is_staff:
        if story.get('author_id') != request.user.id:
            messages.error(request, 'You can only edit your own stories.')
            return redirect('author_dashboard')
    
    if flask_api.delete_page(page_id):
        messages.success(request, 'Page deleted successfully!')
    else:
        messages.error(request, 'Failed to delete page.')
    
    return redirect('edit_story', story_id=story_id)


@login_required  # ← REQUIRED!
def create_choice(request, page_id):
    """Create a choice for a page"""
    page = flask_api.get_page(page_id)
    
    if not page:
        messages.error(request, 'Page not found.')
        return redirect('author_dashboard')
    
    story = flask_api.get_story(page['story_id'])
    
    # Level 16: Check ownership
    if not request.user.is_staff:
        if story.get('author_id') != request.user.id:
            messages.error(request, 'You can only edit your own stories.')
            return redirect('author_dashboard')
    
    if request.method == 'POST':
        text = request.POST.get('text')
        next_page_id = request.POST.get('next_page_id')
        dice_requirement = request.POST.get('dice_requirement', '')
        
        if not text or not next_page_id:
            messages.error(request, 'Choice text and next page are required.')
            return render(request, 'gameplay/create_choice.html', {
                'story': story,
                'page': page,
            })
        
        dice_req = int(dice_requirement) if dice_requirement and dice_requirement.isdigit() else None
        
        choice = flask_api.create_choice(
            page_id=page_id,
            text=text,
            next_page_id=int(next_page_id),
            dice_requirement=dice_req
        )
        
        if choice:
            messages.success(request, 'Choice created successfully!')
            return redirect('edit_story', story_id=page['story_id'])
        else:
            messages.error(request, 'Failed to create choice. Make sure the next page exists in this story.')
    
    # Get all pages for this story (for next_page dropdown)
    all_pages = story.get('pages', [])
    
    context = {
        'story': story,
        'page': page,
        'all_pages': all_pages,
    }
    return render(request, 'gameplay/create_choice.html', context)


@login_required  # ← REQUIRED!
@require_POST
def delete_choice(request, choice_id):
    """Delete a choice"""
    # We need to get page info first to redirect properly
    page_id = request.POST.get('page_id')
    story_id = request.POST.get('story_id')
    
    if flask_api.delete_choice(choice_id):
        messages.success(request, 'Choice deleted successfully!')
    else:
        messages.error(request, 'Failed to delete choice.')
    
    if story_id:
        return redirect('edit_story', story_id=story_id)
    else:
        return redirect('author_dashboard')