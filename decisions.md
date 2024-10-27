# Python version

Python 3.12.7 will be used for this project. Python 3.13.0 has been released recently, but might not yet be supported by the libraries we use, and we want to avoid any issues due to the time constraints.

Pyenv will be used to manage the Python version.

# Package manager

We will use Poetry to manage the dependencies of the project. 

# Pre-commit hooks

We will use pre-commit to mantain PEP8 compliance and autoformat the code.

# FastAPI

We will use FastAPI to develop the API. Its high performance, easy to use and the auto-generated OpenAPI spec is very useful and matches the challenge requirements.
The application will be served by Uvicorn. A lightweight and well performing ASGI server.

# Database

PostgreSQL will be used as the database. It provides a robust, reliable and easy to use open source database.
We will use SQLModel to define the models and the database session. Since its build on top of SQLAlchemy, it will allow us to use the ORM capabilities of the latter if we need to optimize for performance.

# Docker

Docker will be used to containerize the application and the database. It will allow us to easily run the application locally and deploy it to the cloud.

# Environment variables

We will use Pydantic Settings to manage the environment variables. It provides a way to manage the environment variables and the configuration of the application.
For simplicity and ease of use, the environment variables will be stored in a .env file and will be loaded automatically by the application. For the production environment, the environment variables MUST be stored securely in the cloud and will be loaded automatically by the application.
