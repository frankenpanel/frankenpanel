# FrankenPanel: multi-stage build (frontend + backend)
# Used by GitHub Actions; installer can pull this image and extract built frontend.

# -----------------------------------------------------------------------------
# Stage 1: build frontend
# -----------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /build

COPY frontend/package.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: backend + built frontend
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV FRANKENPANEL_ROOT=/app
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

WORKDIR $FRANKENPANEL_ROOT

# Copy backend
COPY backend/ control-panel/backend/
# Copy built frontend from stage 1
COPY --from=frontend-builder /build/dist control-panel/frontend/dist

# Create venv and install backend deps
RUN python3 -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r control-panel/backend/requirements.txt

# Default: run uvicorn (host 0.0.0.0 for container; Caddy or host proxies to it)
WORKDIR $FRANKENPANEL_ROOT/control-panel/backend
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
