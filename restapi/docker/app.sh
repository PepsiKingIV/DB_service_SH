#!/bin/bash
alembic upgrade head
cd src 
gunicorn main:app -w 9 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000