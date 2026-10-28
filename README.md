# AI Civic Issue Reporting System

This repository contains a Streamlit-based civic issue management dashboard for citizens, field staff, and municipal admins.

## Features

- Citizen portal for reporting civic problems
- GPS-based issue registration
- Duplicate detection within a 30m radius
- Department auto-routing
- Field staff status updates
- Admin dashboard analytics

## Run locally

1. Clone this repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the app:

```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to https://share.streamlit.io/
3. Connect the repository and select `app.py` as the main file.
4. Set the Python version to 3.11 or newer.

## Project structure

- `app.py` — main Streamlit application
- `requirements.txt` — Python dependencies

## Notes

This version uses in-memory session storage and is intended for demo/development use. For production usage, replace session state with a database and persistent file storage.
