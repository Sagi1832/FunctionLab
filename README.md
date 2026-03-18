# FunctionLab API

The FunctionLab API is the backend gateway of the FunctionLab platform.

It handles authentication, user management, request validation, and communication with the computation engine through Kafka.

## Core Responsibilities

- expose HTTP routes for client applications
- manage user registration and login
- authenticate users with JWT
- store user credentials in PostgreSQL
- validate incoming requests
- forward analysis requests to the engine through Kafka

## Authentication

The API uses JWT-based authentication to protect restricted routes and manage user sessions in a stateless way.

After a successful login, the server issues a token that the client can use to access protected endpoints.

## Database

PostgreSQL is used to store user account data, including usernames and passwords as part of the authentication workflow.

## Route-to-Engine Flow

The API serves as the entry point for analysis requests.

Instead of performing symbolic computation directly, it sends computation requests through Kafka to the FunctionLab Engine, which handles the mathematical processing and returns the result through the system flow.

## Tech Stack

- Python 3
- FastAPI
- PostgreSQL
- JWT
- Kafka

## Purpose

This repository separates application and user-management concerns from the mathematical engine, making the overall system easier to maintain, scale, and extend.
