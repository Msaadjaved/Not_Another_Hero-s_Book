from app import db
from datetime import datetime

class Story(db.Model):
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, published, suspended
    start_page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=True)
    illustration_url = db.Column(db.String(500), nullable=True)  # Level 18
    author_id = db.Column(db.Integer, nullable=True)  # Level 16+
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pages = db.relationship('Page', backref='story', lazy=True, foreign_keys='Page.story_id')
    
    def to_dict(self, include_pages=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'start_page_id': self.start_page_id,
            'illustration_url': self.illustration_url,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_pages:
            data['pages'] = [page.to_dict(include_choices=True) for page in self.pages]
        return data


class Page(db.Model):
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_ending = db.Column(db.Boolean, default=False)
    ending_label = db.Column(db.String(100), nullable=True)  # Level 13
    illustration_url = db.Column(db.String(500), nullable=True)  # Level 18
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    choices = db.relationship('Choice', backref='page', lazy=True, foreign_keys='Choice.page_id')
    
    def to_dict(self, include_choices=True):
        data = {
            'id': self.id,
            'story_id': self.story_id,
            'text': self.text,
            'is_ending': self.is_ending,
            'ending_label': self.ending_label,
            'illustration_url': self.illustration_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_choices:
            data['choices'] = [choice.to_dict() for choice in self.choices]
        return data


class Choice(db.Model):
    __tablename__ = 'choices'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    next_page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False)
    dice_requirement = db.Column(db.Integer, nullable=True)  # Level 18: random events
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to next page
    next_page = db.relationship('Page', foreign_keys=[next_page_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'text': self.text,
            'next_page_id': self.next_page_id,
            'dice_requirement': self.dice_requirement,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
