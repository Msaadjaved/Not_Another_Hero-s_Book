from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Story, Page, Choice
from functools import wraps

api_bp = Blueprint('api', __name__)


# Level 16: API Key authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key != current_app.config['API_KEY']:
            return jsonify({'error': 'Unauthorized - Invalid API Key'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ============ READING ENDPOINTS (Public) ============

@api_bp.route('/stories', methods=['GET'])
def get_stories():
    """Get all stories, optionally filtered by status"""
    status = request.args.get('status')
    
    query = Story.query
    if status:
        query = query.filter_by(status=status)
    
    stories = query.all()
    return jsonify([story.to_dict() for story in stories])


@api_bp.route('/stories/<int:story_id>', methods=['GET'])
def get_story(story_id):
    """Get a single story by ID"""
    story = Story.query.get_or_404(story_id)
    return jsonify(story.to_dict(include_pages=True))


@api_bp.route('/stories/<int:story_id>/start', methods=['GET'])
def get_story_start(story_id):
    """Get the starting page of a story"""
    story = Story.query.get_or_404(story_id)
    
    if not story.start_page_id:
        return jsonify({'error': 'Story has no start page'}), 400
    
    start_page = Page.query.get(story.start_page_id)
    if not start_page:
        return jsonify({'error': 'Start page not found'}), 404
    
    return jsonify(start_page.to_dict())


@api_bp.route('/pages/<int:page_id>', methods=['GET'])
def get_page(page_id):
    """Get a page with its choices"""
    page = Page.query.get_or_404(page_id)
    return jsonify(page.to_dict())


# Level 18: Get story tree for visualization
@api_bp.route('/stories/<int:story_id>/tree', methods=['GET'])
def get_story_tree(story_id):
    """Get the full story tree structure for visualization"""
    story = Story.query.get_or_404(story_id)
    
    pages = Page.query.filter_by(story_id=story_id).all()
    
    # Build nodes and edges for graph visualization
    nodes = []
    edges = []
    
    for page in pages:
        nodes.append({
            'id': page.id,
            'text': page.text[:50] + '...' if len(page.text) > 50 else page.text,
            'is_ending': page.is_ending,
            'ending_label': page.ending_label,
            'is_start': page.id == story.start_page_id
        })
        
        for choice in page.choices:
            edges.append({
                'from': page.id,
                'to': choice.next_page_id,
                'label': choice.text[:30] + '...' if len(choice.text) > 30 else choice.text
            })
    
    return jsonify({
        'story_id': story_id,
        'title': story.title,
        'nodes': nodes,
        'edges': edges
    })


# ============ WRITING ENDPOINTS (Protected at Level 16) ============

@api_bp.route('/stories', methods=['POST'])
@require_api_key
def create_story():
    """Create a new story"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    story = Story(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'draft'),
        author_id=data.get('author_id'),
        illustration_url=data.get('illustration_url')
    )
    
    db.session.add(story)
    db.session.commit()
    
    return jsonify(story.to_dict()), 201


@api_bp.route('/stories/<int:story_id>', methods=['PUT'])
@require_api_key
def update_story(story_id):
    """Update an existing story"""
    story = Story.query.get_or_404(story_id)
    data = request.get_json()
    
    if 'title' in data:
        story.title = data['title']
    if 'description' in data:
        story.description = data['description']
    if 'status' in data:
        story.status = data['status']
    if 'start_page_id' in data:
        story.start_page_id = data['start_page_id']
    if 'illustration_url' in data:
        story.illustration_url = data['illustration_url']
    
    db.session.commit()
    
    return jsonify(story.to_dict())


@api_bp.route('/stories/<int:story_id>', methods=['DELETE'])
@require_api_key
def delete_story(story_id):
    """Delete a story and all its pages and choices"""
    story = Story.query.get_or_404(story_id)
    
    # Delete all choices first
    for page in story.pages:
        Choice.query.filter_by(page_id=page.id).delete()
    
    # Delete all pages
    Page.query.filter_by(story_id=story_id).delete()
    
    # Delete the story
    db.session.delete(story)
    db.session.commit()
    
    return jsonify({'message': 'Story deleted successfully'}), 200


@api_bp.route('/stories/<int:story_id>/pages', methods=['POST'])
@require_api_key
def create_page(story_id):
    """Create a new page for a story"""
    story = Story.query.get_or_404(story_id)
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Text is required'}), 400
    
    page = Page(
        story_id=story_id,
        text=data['text'],
        is_ending=data.get('is_ending', False),
        ending_label=data.get('ending_label'),
        illustration_url=data.get('illustration_url')
    )
    
    db.session.add(page)
    db.session.commit()
    
    # If this is the first page and no start page is set, set it as start
    if not story.start_page_id:
        story.start_page_id = page.id
        db.session.commit()
    
    return jsonify(page.to_dict()), 201


@api_bp.route('/pages/<int:page_id>', methods=['PUT'])
@require_api_key
def update_page(page_id):
    """Update an existing page"""
    page = Page.query.get_or_404(page_id)
    data = request.get_json()
    
    if 'text' in data:
        page.text = data['text']
    if 'is_ending' in data:
        page.is_ending = data['is_ending']
    if 'ending_label' in data:
        page.ending_label = data['ending_label']
    if 'illustration_url' in data:
        page.illustration_url = data['illustration_url']
    
    db.session.commit()
    
    return jsonify(page.to_dict())


@api_bp.route('/pages/<int:page_id>', methods=['DELETE'])
@require_api_key
def delete_page(page_id):
    """Delete a page and its choices"""
    page = Page.query.get_or_404(page_id)
    
    # Delete all choices from this page
    Choice.query.filter_by(page_id=page_id).delete()
    
    # Delete all choices pointing to this page
    Choice.query.filter_by(next_page_id=page_id).delete()
    
    db.session.delete(page)
    db.session.commit()
    
    return jsonify({'message': 'Page deleted successfully'}), 200


@api_bp.route('/pages/<int:page_id>/choices', methods=['POST'])
@require_api_key
def create_choice(page_id):
    """Create a new choice for a page"""
    page = Page.query.get_or_404(page_id)
    data = request.get_json()
    
    if not data or 'text' not in data or 'next_page_id' not in data:
        return jsonify({'error': 'Text and next_page_id are required'}), 400
    
    # Verify next page exists and belongs to same story
    next_page = Page.query.get(data['next_page_id'])
    if not next_page or next_page.story_id != page.story_id:
        return jsonify({'error': 'Invalid next_page_id'}), 400
    
    choice = Choice(
        page_id=page_id,
        text=data['text'],
        next_page_id=data['next_page_id'],
        dice_requirement=data.get('dice_requirement')
    )
    
    db.session.add(choice)
    db.session.commit()
    
    return jsonify(choice.to_dict()), 201


@api_bp.route('/choices/<int:choice_id>', methods=['PUT'])
@require_api_key
def update_choice(choice_id):
    """Update an existing choice"""
    choice = Choice.query.get_or_404(choice_id)
    data = request.get_json()
    
    if 'text' in data:
        choice.text = data['text']
    if 'next_page_id' in data:
        choice.next_page_id = data['next_page_id']
    if 'dice_requirement' in data:
        choice.dice_requirement = data['dice_requirement']
    
    db.session.commit()
    
    return jsonify(choice.to_dict())


@api_bp.route('/choices/<int:choice_id>', methods=['DELETE'])
@require_api_key
def delete_choice(choice_id):
    """Delete a choice"""
    choice = Choice.query.get_or_404(choice_id)
    
    db.session.delete(choice)
    db.session.commit()
    
    return jsonify({'message': 'Choice deleted successfully'}), 200


# Health check endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Flask Story API'})
