# 🚀 NAHB - Quick Start Guide

**Get running in 5 minutes!**

---

## ⚡ Fastest Way to Run (Docker)

```bash
# 1. Navigate to project
cd Not_Another_Hero-s_Book

# 2. Start everything
docker-compose up

# 3. Open browser
# http://localhost:8000 - Django App
# http://localhost:5000 - Flask API

# That's it! ✅
```

---

## 🔧 Manual Setup (Without Docker)

### **Prerequisites:**
- Python 3.9+
- pip

### **Step 1: Start Flask API**

Open **Terminal 1:**
```bash
cd flask-api
pip install -r requirements.txt
python run.py
```
✅ Flask running on http://localhost:5000

### **Step 2: Start Django App**

Open **Terminal 2:**
```bash
cd django-app
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Username: admin, Password: admin123
python manage.py runserver 8000
```
✅ Django running on http://localhost:8000

### **Step 3: Add Sample Data (Optional)**

Open **Terminal 3:**
```bash
pip install requests
python create_sample_stories.py
```
✅ 3 stories with 23 pages created!

---

## 🎮 First Time Using

### **1. Visit the Homepage**
Go to: http://localhost:8000

You should see:
- ✅ "Welcome to NAHB" header
- ✅ Search bar
- ✅ Story cards (if you ran sample data)
- ✅ Navigation: Browse Stories, Statistics

### **2. Create Test Accounts**

**Register as Reader:**
1. Click "Register"
2. Username: `reader`, Password: `password123`
3. Select role: "Read Stories"
4. Submit

**Register as Author:**
1. Click "Register" 
2. Username: `author`, Password: `password123`
3. Select role: "Write Stories"
4. Submit

**Use Admin Account:**
- Login with the superuser you created
- Has all permissions

### **3. Try Each Role**

**As Reader:**
- Browse and play stories
- Rate stories (1-5 stars)
- Report inappropriate content
- View your play history

**As Author:**
- Click "Author Dashboard"
- Create a new story
- Add pages and choices
- Publish it

**As Admin:**
- Click "Admin Panel"
- View reports
- Suspend stories
- Moderate content

---

## 📖 Play a Story

1. Go to homepage
2. Click "Play Now" on any story
3. Read the page
4. Choose an option
5. If dice required, click "Roll Dice"
6. Continue until reaching an ending
7. View your complete journey path!

---

## ✍️ Create a Story (As Author)

1. Login as author
2. Go to "Author Dashboard"
3. Click "Create New Story"
4. Fill in title and description
5. Click "Create Story"

**Add Pages:**
1. Click "Add Page"
2. Enter page text
3. Check "Is Ending" if this is an ending page
4. Add ending label if it's an ending
5. Save

**Add Choices:**
1. Click "Add Choice" on a page
2. Enter choice text
3. Select which page it leads to
4. (Optional) Set dice requirement (1-6)
5. Save

**Publish:**
1. Edit story
2. Change status to "Published"
3. Now visible to all users!

---

## 🎲 Using Dice Mechanics

When playing a story with dice requirements:

1. Reach a choice with dice icon 🎲
2. Click "Roll Dice"
3. See your roll result (1-6)
4. If roll ≥ requirement: Choice unlocked ✅
5. If roll < requirement: Choice locked ❌
6. Roll again or choose different option

---

## 📊 View Statistics

**Global Stats:**
- Go to "Statistics" in navbar
- See total plays, stories, users
- Top played stories
- Recent ratings

**Your Stats:**
- Go to "Profile"
- See your play history
- Click "View Path" to see journey
- View your ratings

---

## 🛠️ Common Issues

### **"Connection refused" error**
- Make sure Flask is running on port 5000
- Check that Django FLASK_API_URL points to http://localhost:5000

### **"No stories found"**
- Run `python create_sample_stories.py` to add sample data
- Or create stories manually as author

### **"Permission denied" on author pages**
- Make sure you're logged in
- Register with "Write Stories" role
- Admin accounts automatically have author access

### **Database errors**
```bash
# Reset Django database
rm django-app/db.sqlite3
cd django-app
python manage.py migrate
python manage.py createsuperuser

# Reset Flask database
rm -rf flask-api/instance/
cd flask-api
python run.py  # Will recreate database
```

### **"UserProfile not found"**
```bash
cd django-app
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

## 🧪 Test Accounts

Create these for testing:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from gameplay.models import UserProfile

# Reader
reader = User.objects.create_user('reader', 'reader@test.com', 'password123')
UserProfile.objects.create(user=reader, role='reader')

# Author
author = User.objects.create_user('author', 'author@test.com', 'password123')
UserProfile.objects.create(user=author, role='author')

# Admin
admin = User.objects.create_user('admin', 'admin@test.com', 'password123')
admin.is_staff = True
admin.save()
UserProfile.objects.create(user=admin, role='admin')

print("Test accounts created!")
```

---

## 📱 URLs Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Django Home | http://localhost:8000 | Main application |
| Django Admin | http://localhost:8000/admin | Database admin |
| Flask API | http://localhost:5000 | REST API |
| Flask Health | http://localhost:5000/health | API status |

---

## 🔑 API Testing

Test the Flask API with curl:

```bash
# Get all stories (public)
curl http://localhost:5000/stories

# Get specific story (public)
curl http://localhost:5000/stories/1

# Create story (protected - needs API key)
curl -X POST http://localhost:5000/stories \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-secret-api-key-2024" \
  -d '{"title":"Test Story","description":"A test","status":"draft","author_id":1}'
```

---

## 📸 Taking Screenshots

For submission, capture these screens:

1. **Homepage** - Story cards and search
2. **Story Detail** - Ratings and stats
3. **Playing** - Making a choice
4. **Ending** - Ending label and stats
5. **Author Dashboard** - Story management
6. **Create Story** - Story creation form
7. **Admin Dashboard** - Reports list
8. **Story Tree** - Visualization
9. **Search** - Search results
10. **Player Path** - Journey visualization

Save in `screenshots/` folder (add to .gitignore)

---

## ⏱️ 5-Minute Test Run

```bash
# 1. Start services (30 seconds)
docker-compose up -d

# 2. Add sample data (20 seconds)
python create_sample_stories.py

# 3. Open browser (10 seconds)
# Go to http://localhost:8000

# 4. Create account (60 seconds)
# Register as author

# 5. Play a story (120 seconds)
# Click "Play Now" and complete a story

# 6. View your path (30 seconds)
# Go to Profile → Click "View Path"

# Total: 4.5 minutes! ✅
```

---

## 🎯 Success Checklist

After setup, verify:
- [ ] Can access homepage
- [ ] Can register and login
- [ ] Can browse stories
- [ ] Can play a story
- [ ] Can reach an ending
- [ ] Can view player path
- [ ] Author can create stories
- [ ] Admin can see reports
- [ ] Dice mechanics work
- [ ] Statistics page loads

**All checked? You're ready! 🎉**

---

## 📞 Need More Help?

- **Full documentation:** See README.md
- **Architecture details:** See PROJECT_SUMMARY.md
- **File structure:** See TREE_STRUCTURE.md

---

**Happy storytelling! 📖✨**
