# Asynchronous Background Job Processor

## Overview

This project is a backend system that processes jobs asynchronously using a database-backed queue.

It supports safe retries, idempotent job creation, and controlled execution using row-level locking.

---

## Features

* Background job processing using PostgreSQL
* Idempotent job creation to prevent duplicates
* Retry mechanism with backoff
* Job status tracking (pending, processing, completed, failed)
* Row-level locking using FOR UPDATE SKIP LOCKED
* Failure handling with retry limits

---

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* psycopg

---

## Setup Instructions

### 1. Clone repository

git clone <your-repo-url>

### 2. Navigate to project

cd async-job-processor

### 3. Create virtual environment

python -m venv venv

### 4. Activate environment

venv\Scripts\activate

### 5. Install dependencies

pip install -r requirements.txt

### 6. Run server

uvicorn app.main:app --reload

---

## API Endpoints

POST /jobs
POST /jobs/process

---

## Key Concepts Implemented

* Idempotent job creation using unique keys
* Safe concurrent processing using database locks
* Retry logic with backoff and attempt limits
* Failure handling in distributed systems

---

## Notes

This project demonstrates backend system design concepts such as reliability, concurrency control, and safe retries.
