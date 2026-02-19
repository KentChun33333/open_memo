# OpenMemo — Root-level Dockerfile for GCP Cloud Run
# Delegates to webapp/ subdirectory

# Step 1: Build the React Frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY webapp/frontend/package*.json ./
RUN npm install
COPY webapp/frontend/ .
RUN npm run build

# Step 2: Setup the Python Backend
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY webapp/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code, content, and compiled frontend
COPY webapp/backend/ ./backend/
COPY webapp/content/ ./content/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Production settings
ENV PORT=8080
ENV OPENMEMO_SECRET_KEY=change-me-in-production
EXPOSE 8080

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
