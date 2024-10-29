# Decisions and architectural overview

# Table of Contents

1. [Overview](#overview)
2. [Technology choices](#technology-choices)
   - [Python version](#python-version)
   - [Package manager](#package-manager) 
   - [Web framework](#web-framework)
   - [Database](#database)
   - [Task Scheduler](#task-scheduler)
   - [Caching and message broker](#caching-and-message-broker)
   - [Containerization](#containerization)


# Overview

This document outlines the decisions made during the development of the Events Provider Integration project. The goal was to build a scalable, maintainable and high performant microservice that not only meets the requirements but is also prepared for future growth and feature additions.

The API performs in the order of dozens or even single digit milliseconds, well below the required hundreds of milliseconds magnitude order. Given this excellent performance, caching has not been implemented as I was constrained by time and wanted to focus on other aspects of the project, still redis is already integrated and ready to be easily be used for future optimizations.

I approached this challenge as if it were a long term project, emphasizing code quality, scalability and maintainability. Each technology and architectural choice was made to ensure the system can handle increased load and be easily extende while remaining robust over time. Some of the choices might seem overkill for a simple test project, but I like to think of this as a foundation for a system that will grow and evolve over time.


# Technology choices

## Python version

Python 3.12.7 will be used for this project. Python 3.13.0 has been released recently, but might not yet be supported by the libraries we use, and we want to avoid any issues due to the time constraints.

Pyenv will be used to manage the Python version locally.

## Package manager

We will use Poetry to manage the dependencies of the project. It is a robust and well established package manager that will allow us to easily manage the dependencies of the project.


## Web framework

We will use FastAPI to develop the API. Its known for its high performance leveraging asynchronous capabilities to handle a large number of concurrent requests efficiently. Its auto-generated OpenAPI spec is very useful and matches the challenge requirements.
The application will be served by Uvicorn. A lightweight and well performing ASGI server.

## Database

PostgreSQL will be used as the primary database. It provides a robust, reliable and easy to use open source database that also enables ACID transactions.
We will use SQLAlchemy as ORM. Its advanced capabilities will allow us to optimize for performance using more advanced queries.

## Task Scheduler

Celery will be used to schedule the fetch events task. It allows to run scheduled asynchronous tasks outside the main application process and can also scale horizontally so its a good fit for this use case since we expect to run the fetch events task periodically and want to set the foundation for future scalability needs.


## Caching and message broker

Redis will be used to support Celery, acting as a message broker and a task result backend, simplifying the architecture and improving the performance of the system. 

It also provides the foundation for implementing caching strategies to improve API response times under high load once the project grows.


## Containerization

Docker will be used to containerize the application. It will allow us to easily run the application locally and set the project close to a production ready environment facilitating the deployment process and scalability needs in the future in a container orchestration system like Kubernetes.

Docker compose will be used to define the services and their dependencies and to run them locally.

## Environment management

We will use Pydantic Settings to manage the environment variables. It provides a way to manage the environment variables and the configuration of the application.
For simplicity of the evaluation of the test project, the environment variables will be stored in a .env file publicly pushed to the repository, for a production environment they should be stored securely in the cloud or a secrets manager.


## Code quality

We will use pre-commit to mantain PEP8 compliance and autoformat the code with professional tools. black, isort and flake8 will be added to help during the development of the test project. A more solid setup with ruff, mypy and others would be optimal for a production setup.


# Business logic and data retention strategy

### Fetch events

The fetch events task runs on a configurable schedule managed by Celery Beat. It processes events with sell_mode=online, calculating min/max prices from zone data, and efficiently stores them using bulk upsert operations to maintain data consistency. Failed tasks are automatically retried with exponential backoff to ensure reliability.

The task is idempotent, meaning that if it is run multiple times, it will not duplicate the events, but it will update the existing ones with the new data.

It is configured to run every 5 minutes, I have assumed this is a safe window to allow for outdated data retrieved from the API endpoint. But in a professional setup this would have been discussed with the business stakeholders and a better strategy in case that this is not acceptable would have been implemented.


### Event Retention Strategy

Once an event is fetched it will be stored in our database indefinitely.

There is a con to this strategy and we might need to add a mechanism to delete those events after a certain period of time in the future.

Future Considerations: We may need to implement a data archiving or deletion mechanism in the future to manage database size and query performance. This could involve:
   - Implementing a "soft delete" flag for events that haven't been updated in a long time.
   - Creating an archiving process to move old events to a separate storage solution.
   - Developing a policy for permanent deletion of events after a certain period of inactivity.

Query Optimization: As the database grows, we may need to optimize our queries to ensure efficient retrieval of only relevant (current or recent) events for user-facing operations. The current implementation uses basic date range filtering which may need to be enhanced with additional indexes or partitioning strategies.

This strategy provides a good balance between data completeness and system simplicity for our current needs, while leaving room for future optimizations as the system scales.

