# FastAPI Social Media API

A simple social media backend built with **FastAPI**, **FastAPI Users**, **Async SQLAlchemy**, and **ImageKit**.

Users can register, authenticate using JWT, upload images/videos, and view a feed of posts.

---

## Features

* User Registration
* JWT Authentication
* Password Reset
* Email Verification Support
* Upload Images & Videos
* Feed Endpoint
* Delete Own Posts
* Async Database Operations
* ImageKit Cloud Storage
* FastAPI Automatic Documentation

---

## Tech Stack

* Python
* FastAPI
* FastAPI Users
* SQLAlchemy (Async)
* SQLite
* ImageKit
* Uvicorn
* uv

---

## Installation

### Clone Repository

```bash
git clone https://github.com/krishna-01108/fastapi-simple-social-media.git
cd fastapi-simple-social-media
```

### Create Virtual Environment

```bash
uv venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
uv sync
```

### Run Server

```bash
uv run uvicorn app:app --reload
```

Server starts at:

```
http://127.0.0.1:8000
```

---

## API Documentation

Swagger UI:

```
http://127.0.0.1:8000/docs
```

ReDoc:

```
http://127.0.0.1:8000/redoc
```

---

## Authentication Routes

| Method | Endpoint                     |
| ------ | ---------------------------- |
| POST   | `/auth/register`             |
| POST   | `/auth/jwt/login`            |
| POST   | `/auth/forgot-password`      |
| POST   | `/auth/request-verify-token` |
| GET    | `/users/{id}`                |

---

## Post Routes

### Upload Media

```http
POST /upload
```

Form fields:

* `file`
* `caption`

Authentication required.

Supported files:

* Images
* Videos (`.mp4`, `.mkv`)

---

### Get Feed

```http
GET /feed
```

Returns posts ordered by newest first.

---

### Delete Post

```http
DELETE /post/{id}
```

Only the owner of the post can delete it.

---

## Dependencies

* fastapi
* fastapi-users
* aiosqlite
* imagekitio
* python-dotenv
* uvicorn

---

## Project Structure

```text
.
├── app/
│   ├── db.py
│   ├── schema.py
│   ├── users.py
│   ├── images.py
│   └── ...
├── app.py
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## Future Improvements

* Likes and Comments
* Follow System
* User Profile Images
* Search Users
* Pagination
* Cloud Database Deployment

---

## Author

**Krishna Yadav**

GitHub: https://github.com/krishna-01108

---

⭐ If you found this project useful, consider giving it a star.
