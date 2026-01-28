# Bill Lens Backend Walkthrough

This walkthrough guides you through running and testing the Bill Lens Backend application.

## Prerequisites

- Docker and Docker Compose installed.
- Python installed (for running the test script).

## Running the Application

1.  Open a terminal in the project directory: `c:/Progetti/Progetti Flask/bill-lens-backend`
2.  Build and start the containers:
    ```bash
    docker-compose up --build
    ```
3.  Wait for the containers to start. The Flask app will be available at `http://localhost:5000`.

## Database Migration (First Run)

On the very first run, you might need to initialize the database. Since we are using `flask-migrate` but haven't set up the migration scripts yet, the tables will be created automatically if we add a small script or just rely on `db.create_all()` if we added it to `app.py`. 

*Correction*: In the current `app.py`, I didn't explicitly call `db.create_all()`. Let's do it manually via flask shell or update `app.py`.
For now, you can initialize the DB by running this command in another terminal while the containers are running:

```bash
docker-compose exec web python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

**Note**: The application is now configured to automatically create tables on startup, so the above step might be redundant but good to know.

## Seeding the Database

To populate the database with mock data for testing:

1.  Ensure the containers are running.
2.  Run the seed script inside the container:
    ```bash
    docker-compose exec web python seed.py
    ```
    This will create 50 random expense entries.

## Testing the API

You can run the test script either locally (if you have Python installed) or inside the Docker container.

### Option 1: Run inside Docker (Recommended)

Since `requests` is now in `requirements.txt`, you just need to rebuild the container once, and then you can run the test script directly.

1.  **Rebuild the container** (if you haven't already after the update):
    ```bash
    docker-compose up --build
    ```
2.  Run the test script:
    ```bash
    docker-compose exec web python test_api.py
    ```

### Option 2: Run Locally

1.  Install `requests`:
    ```bash
    pip install requests
    ```
    *Note: If `pip` is not recognized, try `python -m pip install requests` or use Option 1.*
2.  Run the test script:
    ```bash
    python test_api.py
    ```

## Database Management (pgAdmin)

You can manage the database using the pgAdmin web interface.

1.  **Access**: Open [http://localhost:5050](http://localhost:5050) in your browser.
2.  **Login**:
    *   Email: `admin@admin.com`
    *   Password: `root`
3.  **Connect to Server**:
    *   Click "Add New Server".
    *   **General** tab: Name it `Bill Lens DB`.
    *   **Connection** tab:
        *   Host name/address: `db`
        *   Port: `5432`
        *   Maintenance database: `bill_lens`
        *   Username: `postgres`
        *   Password: `password`
    *   Click "Save".

You can now browse tables, run SQL queries, and view data.

## API Endpoints

-   **POST /expenses**: Create a new expense.
-   **GET /expenses**: List all expenses.
-   **GET /expenses/<id>**: Get a specific expense.
-   **DELETE /expenses/<id>**: Delete an expense.
-   **GET /expenses/monthly/<year>/<month>**: Get expenses for a specific month.
-   **GET /expenses/analytics/last-month**: Get sum of expenses by category for the last month.

## Offline-First Features

The API now supports offline-first architecture:
-   **UUIDs**: IDs are strings (UUIDs) so clients can generate them offline.
-   **Sync**: Use `GET /expenses?since=<timestamp>` to get only changed items (including deleted ones).
-   **Soft Deletes**: Deleted items are marked with `isDeleted=true` instead of being removed.

### Resetting the Database

If you are upgrading from the previous version (integer IDs), you **MUST** reset the database because the schema has changed incompatible.

# Rebuild and start
docker-compose up --build
```

## Authentication Setup

The backend now uses Firebase Authentication.

### 1. Firebase Credentials
To run in production/development mode, you **MUST** place your `serviceAccountKey.json` file in the `bill-lens-backend` directory.
- Go to Firebase Console -> Project Settings -> Service Accounts.
- Generate new private key.
- Rename the downloaded file to `serviceAccountKey.json`.
- Place it next to `app.py`.

### 2. Testing Mode
For testing without a real Android app, I have configured `docker-compose.yml` with `FLASK_ENV=testing`.
This allows the `test_api.py` script to bypass real Firebase verification by sending a special header:
`Authorization: Bearer TEST_TOKEN`

If you want to test with a REAL token from your app:
1.  Change `FLASK_ENV` back to `development` in `docker-compose.yml`.
2.  Add your `serviceAccountKey.json`.
3.  Update `test_api.py` with a real ID token printed from your Android app.
    
## Google Sheets Export Setup

To enable the export feature:
1.  **Google Cloud Console**:
    *   Enable **Google Sheets API**.
    *   Enable **Google Drive API**.
2.  **Service Account**:
    *   Ensure your `serviceAccountKey.json` belongs to the project where these APIs are enabled.
    *   The Service Account acts as the "creator" of the sheet.
3.  **Requirements**:
    *   Rebuild the container to install `gspread` and `google-auth`:
      ```bash
      docker-compose up --build
      ```
