FROM python:3.13-alpine@sha256:399babc8b49529dabfd9c922f2b5eea81d611e4512e3ed250d75bd2e7683f4b0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
RUN addgroup -S app && adduser -S -G app app
COPY --chown=app:app src/reference_app/ /app/reference_app/
COPY --chown=app:app config/ /app/config/
COPY --chown=app:app pyproject.toml /app/pyproject.toml
USER app
EXPOSE 8080
CMD ["python", "-m", "reference_app.server"]
