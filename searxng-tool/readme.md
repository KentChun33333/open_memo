# SearxNG Agent Tool Setup

This directory contains the required files to run a private SearxNG instance natively with Docker Compose, tailored for agent web-searching.

## How to Launch and Connect

From within this directory, simply run:

```bash
docker-compose up -d
```

This will start:

- A `redis` instance for caching
- The `searxng` service accessible at `http://localhost:8085`

You can then test the setup using the browser or with curl:

```bash
curl "http://localhost:8085/search?q=test&format=json"
```

To stop the services, run:

```bash
docker-compose down
```
