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

# Celery

Celery will be used to schedule the fetch events task. It will allow us to run the task periodically and to retry it in case of failure.

# Redis

Redis will be used to store the Celery tasks results.


# Business logic

### Fetch events

The fetch events task will be scheduled to run periodically and will fetch the events from the provider and will store them in the database.
If the task fails, it will be retried with exponential backoff.


### Upsert events

The upsert events task will be used to store the events in the database. We will retain all events that were at some time available with sell_mode=online, even if they are no longer available.

Once an event is fetched it will be stored in our database indefinitely, if it reappears with sell_mode=online it will be updated with the new data.

There is a con to this strategy: if an event is fetched with sell_mode=online but then never reappears, it will be stored in our database indefinitely, we might need to add a mechanism to delete those events after a certain period of time in the future.


### Event Retention Strategy

Future Considerations: We may need to implement a data archiving or deletion mechanism in the future to manage database size and query performance. This could involve:
   - Implementing a "soft delete" flag for events that haven't been updated in a long time.
   - Creating an archiving process to move old events to a separate storage solution.
   - Developing a policy for permanent deletion of events after a certain period of inactivity.

Query Optimization: As the database grows, we may need to optimize our queries to ensure efficient retrieval of only relevant (current or recent) events for user-facing operations.

This strategy provides a good balance between data completeness and system simplicity for our current needs, while leaving room for future optimizations as the system scales.

