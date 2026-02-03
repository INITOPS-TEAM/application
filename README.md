# PictApp – Image Upload

Simple Flask web application with user authentication and image upload functionality.

## Features
- User registration, login, logout
- Upload images for authenticated users
- List and delete user images
- Image files are stored on disk (synced folder)
- PostgreSQL stores image metadata only (no binary data)

## Storage
Uploaded images are stored on disk under a shared directory:

/var/lib/pictapp/uploads/

Each user has a separate subdirectory.
The same path is used on all application VMs.

## Database
PostgreSQL stores metadata only:
- user_id
- original filename
- stored filename
- file path
- creation timestamp
