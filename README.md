# 📖 NAHB - Not Another Hero's Book

**A Choose Your Own Adventure Web Application**

Interactive storytelling platform built with Flask & Django - Final Project for Python for Web Applications

**Team Size:** 2 students  
**Grade Level Target:** 18-20/20  
**Deadline:** February 14, 2026, 11:55 PM

---

## 🎯 Project Overview

NAHB is a full-stack web application that brings Choose Your Own Adventure stories to life. Authors create branching narratives with multiple endings, while readers play through stories by making choices that determine their path. The application features user authentication, role-based permissions, community features, and advanced gameplay mechanics including dice rolls and path visualization.

### **Key Features:**
- 🎮 Interactive story gameplay with branching paths
- ✍️ Author tools for story creation and management
- 🎲 Dice roll mechanics for random events
- 📊 Statistics and ending distribution tracking
- ⭐ Community ratings and reviews
- 🛡️ Admin moderation system
- 🗺️ Complete player journey visualization
- 💾 Auto-save functionality
- 🔐 Role-based access control

---

## 🏗️ Architecture

### **Two-Application Design:**

```
┌─────────────────┐         REST API          ┌──────────────────┐
│   Flask API     │◄─────────────────────────►│   Django Web     │
│  (Port 5000)    │     JSON Responses        │   (Port 8000)    │
│                 │                            │                  │
│  Story Storage  │                            │  Game Engine     │
│  Content DB     │                            │  User Data       │
└─────────────────┘                            └──────────────────┘
```

### **Flask API** - Story Storage
- **Purpose:** Centralized story content management
- **Database:** SQLite (stories.db)
- **Models:** Story, Page, Choice
- **API:** 15 REST endpoints (6 public, 9 protected)
- **Security:** API key authentication on write operations

### **Django Web App** - Game Engine & UI
- **Purpose:** User interface, gameplay, and user management
- **Database:** SQLite (db.sqlite3)
- **Models:** Play, PlaySession, UserProfile, Rating, Report, PlayerPath
- **Features:** Authentication, permissions, gameplay, statistics
- **Integration:** Consumes Flask API via custom client wrapper

---

## 📋 Requirements Implemented

### ✅ **Level 10/20 - MVP**
- [x] Flask REST API with story/page/choice CRUD
- [x] Django consumes Flask API
- [x] Public story browsing
- [x] Interactive gameplay (choices → pages → endings)
- [x] Anonymous play tracking
- [x] Basic statistics (plays per story, ending distribution)

### ✅ **Level 13/20 - Advanced Gameplay**
- [x] Search and filter published stories
- [x] Named endings with labels
- [x] Path statistics with percentages
- [x] Auto-save progression (anonymous & authenticated)
- [x] Resume saved games
- [x] Draft vs Published enforcement
- [x] Improved UI with confirmations

### ✅ **Level 16/20 - Security & Permissions**
- [x] User registration + login/logout
- [x] Three roles: Reader, Author, Admin
- [x] Protected author tools (login required)
- [x] Story ownership validation
- [x] Flask API key protection (X-API-KEY header)
- [x] Admin can suspend/unsuspend stories
- [x] Plays linked to authenticated users

### ✅ **Level 18-20/20 - Quality & Community**
- [x] **Community Features:**
  - [x] Star ratings (1-5) with comments
  - [x] Average rating display
  - [x] Report system with reasons
  - [x] Admin dashboard for moderation
- [x] **Quality Features:**
  - [x] Story tree visualization
  - [x] Player path visualization
  - [x] Illustration support (static URLs)
  - [x] Random events (dice rolls)

### ✅ **Bonus Features**
- [x] Docker & docker-compose setup
- [x] Comprehensive documentation
- [x] Sample data generator (3 complete stories)

---

## 🚀 Quick Start

### **Prerequisites:**
- Python 3.9+
- pip
- (Optional) Docker & Docker Compose

### **Option 1: Docker (Recommended)**

```bash
# Clone the repository
git https://github.com/Msaadjaved/Not_Another_Hero-s_Book.git
cd Not_Another_Hero-s_Book

# Start both services
docker-compose up

# Access the application
# Django Web App: http://localhost:8000
# Flask API: http://localhost:5000
```

### **Option 2: Manual Setup**

**Terminal 1 - Flask API:**
```bash
cd flask-api
pip install -r requirements.txt
python run.py
# Server running on http://localhost:5000
```

**Terminal 2 - Django App:**
```bash
cd django-app
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Create admin account
python manage.py runserver 8000
# Server running on http://localhost:8000
```

**Terminal 3 - Sample Data (Optional):**
```bash
pip install requests
python create_sample_stories.py
# Creates 3 demo stories with 23 pages and 12 endings
```

---

## 📚 Sample Data

The `create_sample_stories.py` script generates three complete interactive stories:

1. **The Enchanted Forest** (Fantasy)
   - 9 pages, 9 choices, 4 endings
   - Magic streams, mysterious cottages, forest guardians
   - Dice mechanic: Drinking magic water requires roll ≥4

2. **Crisis on Space Station Alpha** (Sci-Fi)
   - 7 pages, 6 choices, 4 endings
   - Reactor meltdowns, engineering decisions
   - Dice mechanic: Manual venting requires roll ≥5

3. **The Midnight Detective** (Mystery Noir)
   - 7 pages, 8 choices, 4 endings
   - Missing billionaire, AI conspiracy
   - Dice mechanic: Confronting AI requires roll ≥3

**Total:** 23 pages, 23 choices, 12 unique endings

---

## 🔐 User Roles

### **Reader (Default)**
- Browse and play published stories
- Rate and comment on stories
- Report inappropriate content
- View own play history

### **Author**
- All Reader permissions
- Create and manage stories
- Add pages and choices
- Publish/unpublish stories
- Preview drafts

### **Admin**
- All Author permissions
- View moderation dashboard
- Suspend/unsuspend stories
- Review and dismiss reports
- Access Django admin panel

---

## 🎮 How to Use

### **For Readers:**
1. Visit http://localhost:8000
2. Browse published stories
3. Click "Play Now" to start
4. Make choices to progress through the story
5. Roll dice when required for certain choices
6. Reach one of multiple endings
7. Rate and review stories you've played

### **For Authors:**
1. Register with "Write Stories" role
2. Go to Author Dashboard
3. Click "Create New Story"
4. Add pages with text and ending labels
5. Connect pages with choices
6. Set dice requirements for challenging choices
7. Publish when ready

### **For Admins:**
1. Login as staff/admin user
2. Go to Admin Dashboard
3. Review pending reports
4. Suspend inappropriate stories
5. Dismiss false reports
6. Monitor community health

---

## 🔌 API Documentation

### **Base URL:** `http://localhost:5000`

### **Public Endpoints (No Authentication Required):**

```http
GET /stories?status=published
# Returns list of published stories

GET /stories/<id>
# Returns story details with pages and choices

GET /stories/<id>/start
# Returns the starting page of a story

GET /pages/<id>
# Returns page details with available choices

GET /stories/<id>/tree
# Returns story structure (nodes and edges)

GET /health
# Health check endpoint
```

### **Protected Endpoints (Require X-API-KEY Header):**

```http
POST /stories
Body: {
  "title": "Story Title",
  "description": "Story description",
  "status": "draft",
  "author_id": 1
}
# Creates a new story

PUT /stories/<id>
Body: {"status": "published"}
# Updates story

DELETE /stories/<id>
# Deletes story

POST /stories/<id>/pages
Body: {
  "text": "Page text",
  "is_ending": false
}
# Creates page

POST /pages/<id>/choices
Body: {
  "text": "Choice text",
  "next_page_id": 2,
  "dice_requirement": 4
}
# Creates choice
```

**Authentication Header:**
```http
X-API-KEY: your-secret-api-key-2024
```

---

## 🗄️ Database Schema

### **Flask Database (stories.db)**

**stories**
- id, title, description, status (draft/published/suspended)
- start_page_id, author_id, illustration_url
- created_at, updated_at

**pages**
- id, story_id, text, is_ending, ending_label
- illustration_url, created_at

**choices**
- id, page_id, text, next_page_id
- dice_requirement (1-6 or NULL), created_at

### **Django Database (db.sqlite3)**

**gameplay_userprofile**
- user (OneToOne with auth_user)
- role (reader/author/admin)
- bio, created_at

**gameplay_play**
- story_id, ending_page_id, user
- created_at

**gameplay_playsession**
- session_key, story_id, current_page_id, user
- created_at, updated_at

**gameplay_rating**
- story_id, user, stars (1-5), comment
- created_at, updated_at

**gameplay_report**
- story_id, user, reason, description, status
- resolved_by, resolved_at, created_at

**gameplay_playerpath**
- play, page_id, choice_id, sequence
- dice_roll, timestamp

---

## 🧪 Testing

### **Test User Accounts**
After running migrations, create test users:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from gameplay.models import UserProfile

# Create reader
reader = User.objects.create_user('reader', 'reader@test.com', 'password123')
UserProfile.objects.create(user=reader, role='reader')

# Create author
author = User.objects.create_user('author', 'author@test.com', 'password123')
UserProfile.objects.create(user=author, role='author')

# Create admin
admin = User.objects.create_user('admin', 'admin@test.com', 'password123')
admin.is_staff = True
admin.save()
UserProfile.objects.create(user=admin, role='admin')
```

### **Manual Testing Checklist:**

**Level 10:**
- [ ] Browse stories on homepage
- [ ] Play a story and reach an ending
- [ ] View statistics showing plays and endings

**Level 13:**
- [ ] Search for stories by title
- [ ] See named ending labels
- [ ] Close browser mid-game and resume later

**Level 16:**
- [ ] Register and login
- [ ] Access author dashboard (authors only)
- [ ] Admin can suspend stories

**Level 18:**
- [ ] Rate a story with stars and comment
- [ ] Report a story
- [ ] Admin sees reports and can dismiss them
- [ ] View story tree visualization
- [ ] View player path after completing a story
- [ ] Roll dice for chance-based choices

---

## 📁 Project Structure

```
Not_Another_Hero-s_Book/
├── flask-api/              # Flask REST API
│   ├── app/
│   │   ├── __init__.py     # App factory
│   │   ├── models.py       # Story, Page, Choice
│   │   └── routes.py       # 15 API endpoints
│   ├── requirements.txt
│   ├── run.py
│   └── Dockerfile
│
├── django-app/             # Django Web App
│   ├── gameplay/
│   │   ├── models.py       # 6 models
│   │   ├── views.py        # Core views
│   │   ├── views_author.py # Author tools
│   │   ├── views_auth.py   # Auth & admin
│   │   ├── urls.py         # 44 URL patterns
│   │   └── flask_client.py # API wrapper
│   ├── templates/          # 17 HTML templates
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── create_sample_stories.py
└── README.md
```

---

## 🔧 Configuration

### **Flask API (.env)**
```bash
SECRET_KEY=your-secret-key-2024
API_KEY=your-secret-api-key-2024
DATABASE_URL=sqlite:///instance/stories.db
```

### **Django (settings.py)**
```python
SECRET_KEY = 'your-django-secret-key-2024'
FLASK_API_URL = 'http://localhost:5000'
FLASK_API_KEY = 'your-secret-api-key-2024'
```

---

## 🐛 Troubleshooting

### **Port Already in Use**
```bash
# Change Flask port
python run.py --port 5001

# Change Django port
python manage.py runserver 8001
```

### **API Connection Failed**
- Ensure Flask is running on port 5000
- Check FLASK_API_URL in Django settings
- Verify API_KEY matches in both applications

### **Database Issues**
```bash
# Reset Django database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser

# Reset Flask database
rm -rf flask-api/instance/
python flask-api/run.py  # Will recreate
```

### **Missing UserProfile Error**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from gameplay.models import UserProfile

for user in User.objects.all():
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user, role='reader')
```

---

## 🌟 Features Showcase

### **Player Path Visualization**
After completing a story, players can view their complete journey:
- Every page visited
- Every choice made
- Dice rolls (if any)
- Sequence order
- Time spent

### **Story Tree Visualization**
Authors and readers can see the complete story structure:
- All pages as nodes
- All choices as edges
- Starting point marked
- Endings highlighted

### **Dice Roll Mechanics**
Add excitement with chance-based choices:
- Set dice requirement (1-6) on any choice
- Players must roll to attempt
- Visual dice roll interface
- Failed rolls block the choice

### **Auto-Save System**
Never lose progress:
- Saves current page automatically
- Works for anonymous and authenticated users
- Resume from any device (authenticated only)
- Separate saves per story

---

## 👥 Authors

- **Student 1:** Muhammad Saad Javed - Backend
- **Student 2:** Hassan - Frontend

---

## 📄 License

This project is submitted as coursework for EPITA's Python for Web Applications course.

---

## 🙏 Acknowledgments

- Flask documentation
- Django documentation
- AI-generated sample story content (as permitted by assignment guidelines)
- Course instructors and teaching assistants

---

## 📞 Support

For questions or issues:
- Check QUICKSTART.md for common setup problems
- Review PROJECT_SUMMARY.md for feature details
- Contact: muhammadsaadjaved5@gmail.com, chhassanraza2001@gmail.com

---

## 🎓 Academic Context

**Course:** Python for Web Applications  
**Institution:** EPITA  
**Semester:** Third Semester  
**Submission Date:** February 14, 2026, 11:55 PM

**Grade Levels:**
- 10/20 - MVP (Basic functionality)
- 13/20 - Advanced gameplay features
- 16/20 - Security and permissions
- 18-20/20 - Quality features and community tools

**This project demonstrates:**
- Full-stack development (Flask + Django)
- RESTful API design
- Database modeling and relationships
- User authentication and authorization
- Role-based access control
- Clean code architecture
- Professional documentation

---

**Built with ❤️ for interactive storytelling**

*Ready to embark on an adventure? Start playing at http://localhost:8000*
