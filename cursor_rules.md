# Cursor Rules

- The app always runs using Docker Compose. All commands, including running the app, migrations, and tests, should be executed via Docker Compose, not directly on the local machine.
- Do not run backend or frontend services directly with local Python or Node commands; always use the appropriate docker compose service.
- **All new development must include type annotations, clear docstrings, and meaningful logging for all functions, methods, and route handlers. All endpoints and business logic must follow the modernized style in routes.py and other backend files. This is required for all future code contributions.** 