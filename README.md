# Book Collection API

This is a backend RESTful API for managing a personal book collection. It supports user authentication and CRUD operations for books.

## Features

- User registration and login (JWT authentication)
- Add, update, delete, and retrieve books
- Each book is linked to a specific user
- Clean separation of models, and database logic
- Built with FastAPI

## Tech Stack

- *Framework:* FastAPI
- *Database:*  PostgreSQL
- *ORM:* SQLAlchemy
- *Authentication:* JWT (JSON Web Tokens)
- *Validation:* Pydantic

## API Endpoints

### Auth Routes
- POST /signup – Register a new user
- POST /login – Login and get JWT token
