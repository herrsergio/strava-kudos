# Strava Kudos

This Python script automates the process of giving kudos to activities on your Strava feed. It uses Playwright to simulate a real user, logging in and interacting with the dashboard.

## Features

-   **Automated Login**: Securely logs in using credentials stored in an environment file.
-   **Stealth Mode**: Uses `playwright-stealth` to evade basic bot detection.
-   **Smart Interaction**: Handles cookie banners, scrolls through the feed, and intelligently clicks "Kudos" buttons only on activities you haven't already liked.
-   **Debug Support**: Captures screenshots and HTML dumps if errors occur to help with troubleshooting.

## Prerequisites

-   Python 3.7+
-   Pip (Python Package Installer)

## Installation

1.  **Clone the repository** (or download the files):
    ```bash
    git clone https://github.com/herrsergio/strava-kudos
    cd strava-kudos
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browsers**:
    ```bash
    playwright install chromium
    ```

## Configuration

1.  Copy the template environment file to created your local configuration:
    ```bash
    cp .env.template .env
    ```

2.  Open `.env` in a text editor and fill in your Strava credentials:
    ```ini
    STRAVA_EMAIL=your_email@example.com
    STRAVA_PASSWORD=your_password
    ```

## Usage

Run the main script:

```bash
python main.py
```

The script will:
1.  Launch a browser window (visible mode).
2.  Navigate to Strava and log in.
3.  Scroll through your feed.
4.  Give kudos to recent activities.

## Troubleshooting

If the script fails, check the generated debug files:
-   `error_page.png` / `login_failed.png`: Screenshots of where the script got stuck.
-   `debug_page.html` / `empty_feed_debug.html`: HTML dumps of the page state.
-   `*.log`: Check any generated log files.

