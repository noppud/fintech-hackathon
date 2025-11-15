# Docker Setup for Python Backend

This directory contains Docker configuration files to run the Python backend in a container.

## Files

- `Dockerfile` - Docker image definition
- `docker-compose.yml` - Docker Compose configuration for easier container management
- `.dockerignore` - Files to exclude from the Docker image

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. Make sure you have a `.env` file in the `python_backend` directory with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY and other settings
   ```

2. Build and run the container:
   ```bash
   docker-compose up --build
   ```

3. The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Chat endpoint: `http://localhost:8000/chat`

4. To run in detached mode:
   ```bash
   docker-compose up -d
   ```

5. To stop the container:
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker directly

1. Build the image:
   ```bash
   docker build -t python-backend .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 \
     -e OPENROUTER_API_KEY=your_key_here \
     -e DEFAULT_LLM_MODEL=anthropic/claude-3.5-sonnet \
     python-backend
   ```

   Or use an env file:
   ```bash
   docker run -p 8000:8000 --env-file .env python-backend
   ```

## Configuration

### Environment Variables

The container requires the following environment variables (set in `.env` or passed directly):

**Required:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key

**Optional:**
- `DEFAULT_LLM_MODEL` - Default model to use (default: `anthropic/claude-3.5-sonnet`)
- `OPENROUTER_SITE_URL` - Your site URL for OpenRouter
- `OPENROUTER_SITE_NAME` - Your site name for OpenRouter
- `OPENROUTER_BASE_URL` - Override OpenRouter base URL
- `GOOGLE_SERVICE_ACCOUNT_FILE` - Path to Google service account JSON
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `SUPABASE_SERVICE_KEY` - Alternative Supabase key
- `SUPABASE_ANON_KEY` - Supabase anonymous key

### Using Google Sheets

If you need Google Sheets integration:

1. Place your `service-account.json` file in the `python_backend` directory

2. Uncomment the volumes section in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./service-account.json:/app/service-account.json:ro
   ```

3. Or mount it when running with Docker directly:
   ```bash
   docker run -p 8000:8000 \
     --env-file .env \
     -v $(pwd)/service-account.json:/app/service-account.json:ro \
     python-backend
   ```

## Development

To rebuild the image after code changes:
```bash
docker-compose up --build
```

To view logs:
```bash
docker-compose logs -f
```

To access the container shell:
```bash
docker-compose exec python-backend sh
```

## Production Deployment

For production, consider:

1. Using a proper secrets management system instead of `.env` files
2. Setting up health checks and monitoring
3. Using a reverse proxy (nginx/traefik) for SSL termination
4. Running with a process manager or orchestration platform (Kubernetes, Docker Swarm)
5. Using `hypercorn` instead of `uvicorn` for better production performance:
   ```dockerfile
   CMD ["hypercorn", "api:app", "--bind", "0.0.0.0:8000"]
   ```

## Troubleshooting

**Container exits immediately:**
- Check logs: `docker-compose logs`
- Ensure `OPENROUTER_API_KEY` is set in `.env`

**Cannot connect to API:**
- Verify the container is running: `docker-compose ps`
- Check port mapping: `docker-compose port python-backend 8000`
- Ensure no other service is using port 8000

**Import errors:**
- The working directory in the container is `/app`, which contains all Python modules
- The app runs as `uvicorn api:app`, not `uvicorn python_backend.api:app`
