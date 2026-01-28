# Bill Lens Backend Implementation Plan

## Goal Description
Create a Flask backend application to manage expenses. The application will expose RESTful APIs to create, retrieve, delete, and analyze expense data. The entire stack (Flask app + PostgreSQL database) will be containerized using Docker.
**Update**: Add automatic table creation and a data seeding script.
**Update**: Add pgAdmin for database management.
**Update**: Refactor for Offline-First Architecture (UUIDs, Soft Deletes, Synchronization).

## User Review Required
> [!IMPORTANT]
> **Breaking Change**: Switching Primary Key from `Integer` (Auto-increment) to `String` (UUID). This allows the Android app to generate IDs offline.
> **Logic Change**: `DELETE` will now perform a "soft delete" (setting `is_deleted=True`) instead of removing the row.

## Proposed Changes

### Project Structure
The project will follow a standard Flask application structure:
- `app.py`: Main entry point.
- `models.py`: Database models.
- `routes.py`: API endpoints.
- `config.py`: Configuration settings.
- `Dockerfile`: Docker image definition for the Flask app.
- `docker-compose.yml`: Orchestration for App and DB.
- `requirements.txt`: Python dependencies.
- `seed.py`: Script to populate the database with mock data.

### [MODIFY] [models.py](file:///c:/Progetti/Progetti Flask/bill-lens-backend/models.py)
- Change `id` to `String(36)` (UUID).
- Add `last_updated` (DateTime, default=now, onupdate=now).
- Add `is_deleted` (Boolean, default=False).
- **Change `total_amount` to `Numeric(10, 2)` for financial precision.**

### [MODIFY] [routes.py](file:///c:/Progetti/Progetti Flask/bill-lens-backend/routes.py)
- **GET /expenses**: Support `?since=<timestamp>` query param. Return only records where `last_updated > timestamp`. Include deleted records in response so client knows what to remove.
- **POST /expenses**: Accept `id` (UUID) from client. If not provided, generate one. Handle "upsert" (update if exists) logic if needed, or keep simple create.
- **DELETE /expenses/<id>**: Set `is_deleted=True`, update `last_updated`. Do not remove row.
- **PUT /expenses/<id>**: Implement update logic (needed for syncing edits).

### [MODIFY] [seed.py](file:///c:/Progetti/Progetti Flask/bill-lens-backend/seed.py)
- Update to generate UUIDs for mock data.

## Verification Plan

### Automated Tests
- Update `test_api.py` to:
    - Send UUIDs.
    - Test Soft Delete (verify record exists but `is_deleted=True`).
    - Test Sync (GET with `since` parameter).

### Manual Verification
1.  **Rebuild DB**: Since we are changing the PK type, we likely need to drop the existing DB volume or force a migration. (Simplest for dev: `docker-compose down -v`).
2.  **Sync Flow**:
    - Create expense.
    - Update expense.
    - Delete expense.
    - Call `GET /expenses?since=...` and verify only changed items are returned.
