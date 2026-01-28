# Bill Lens Backend 🧾

Backend API for **Bill Lens**, an expense tracking application designed to simplify receipt management and financial organization.

## 🚀 Features

*   **Expense Management**: complete REST API to add, update, delete, and list expenses.
*   **Smart Export**: Integration with **Google Sheets** to export your data directly to Google Drive.
*   **User Management**: Firebase Authentication integration for secure user data.
*   **Cloud Ready**: Optimized for deployment on **Google Cloud Run** and **Cloud SQL**.

## 🛠️ Tech Stack

*   **Language**: Python 3.9
*   **Framework**: Flask
*   **Database**: PostgreSQL
*   **Containerization**: Docker & Docker Compose
*   **Authentication**: Firebase Admin SDK

## 🏃‍♂️ Getting Started

### Prerequisites
*   Docker & Docker Compose installed on your machine.

### Local Development

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/albertoDonof/bill-lens-backend.git
    cd bill-lens-backend
    ```

2.  **Start the services**:
    ```bash
    docker-compose up --build
    ```
    The API will be available at `http://localhost:5000`.

## ☁️ Deployment

This project is configured for continuous deployment on **Google Cloud Platform**.

*   **Compute**: Google Cloud Run (containerized stateless backend)
*   **Database**: Google Cloud SQL (PostgreSQL)

For detailed deployment steps, please refer to the `walkthrough.md` file included in this repository.

## 📚 API Documentation

Detailed API documentation is available in the `api_documentation.md` file.
