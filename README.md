# PictApp – Image Upload
Flask web application for image sharing with authentication, AWS S3 storage, likes, hidden locations and admin IP banning.

## Features
- User registration, login, logout
- Image upload to AWS S3
- Like/Unlike images
- Edit and delete own images
- Optional hidden image location protected by password
- Admin panel:
  - View all users
  - Search users by IP
  - Ban/Unban users by IP

## Architecture Overview
- **Backend:** Flask 3
- **Database:** PostgreSQL (metadata only)
- **ORM:** SQLAlchemy
- **Storage:** AWS S3 (image files)
- **Authentication:** Session-based
- **Password hashing:** Werkzeug security
Images are stored in AWS S3.  
PostgreSQL stores only metadata (no binary image data).

## Database Tables
The application requires the following tables:
- `users`
- `images`
- `likes`
- `banned`
The app fails on startup if required tables are missing.

## Required Environment Variables
You must define:
**FLASK_SECRET_KEY**
**DATABASE_URL**
**AWS_REGION**
**S3_BUCKET_NAME**

### Example
FLASK_SECRET_KEY="supersecret"
DATABASE_URL="postgresql://pictapp_user:password@localhost:5432/pictapp"
AWS_REGION="eu-north-1"
S3_BUCKET_NAME="my-pictapp-bucket"

## Run locally
1. Create and activate a virtual environment
2. Install dependencies from "requirements.txt"
3. Set required environment variables (see above)
4. Run the application:
python run.py
The app will be available at:
http://localhost:5000

## Project Structure
app/
├── templates/
├── init.py
├── admin.py
├── auth.py
├── images.py
├── models.py
├── utils.py
requirements.txt
run.py

## Notes
- The application fails fast on startup if required DB tables are missing.
- In our setup, the DB schema is applied via Jenkins/Ansible from the infrastructure repository (`ansible/roles/db/files/schema.sql`).
- In a deployed environment the app is accessed via load balancer or directly via VM IP
- Passwords are hashed using Werkzeug
- Image location can be hidden with password protection
- Admin can ban users by IP
- Banned IPs are checked before each request  

## Code Quality: Linting and Formatting
Automated checks via GitHub Actions:
- **Markdownlint** - Markdown files
- **Prettier** - Code formatting  
- **CSpell** - Spell checking
- **ESLint** - HTML templates
- **Black & isort** - Python formatting
- **Pylint** - Python linting (fail under 7.5)
- **Gitleaks** - Secret scanning. To enable Gitleaks pre-commit hooks locally, install Gitleaks following [the official installation guide.](https://github.com/gitleaks/gitleaks#installing)

### Workflow Behavior
**Warnings** (don't block): Markdownlint, Prettier, CSpell, Black, isort, ESLint  
**Critical failures** (block merge): Gitleaks, Pylint

Total failed count includes both, but only critical failures prevent merging.

