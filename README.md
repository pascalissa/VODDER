# VODDER

VODDER is a **completely self-contained**, locally-hosted Video-On-Demand (VOD) player built with Django and SQLite. It is designed for offline or "air-gapped" environments, ensuring that all functionality works without any internet connection.

## Key Principles & Architecture

- **Air-Gapped Ready:** The application is "offline-first." Every CSS, JS, and image asset is stored locally in the `static/` directory. No CDNs or external API calls are used.
- **Zero-Dependency Frontend:** No modern frontend build tools (npm/yarn) are required. All styling is managed via robust internal CSS and Django templates.
- **Local Streaming:** Videos are streamed directly from your local filesystem using Django’s `FileResponse`, which support range requests for efficient seeking.
- **Strict Isolation:** Uses a dedicated Python virtual environment to prevent global dependency pollution.

## Features

- **Local Directory Syncing:** Automatically scan and index video course directories based on a specific naming convention.
- **Interactive Dashboard:** View your course progress with a clean, card-based UI.
- **Progress Tracking:** Saves your watched duration and completion status for every video.
- **Course Statistics:** Get visual feedback on total duration, watched time, and completion percentage.
- **Multi-Platform Support:** Includes setup and run scripts for macOS, Ubuntu, and Windows.

## Installation

### Prerequisites
- Python 3.12 (Recommended) or Python 3.x.
- `pip` (Python package manager).

### Setup
1. Clone or download this repository to your local machine.
2. Run the installation script corresponding to your operating system:

   **macOS:**
   ```bash
   ./install_mac.sh
   ```

   **Linux (Ubuntu):**
   ```bash
   chmod +x install_ubuntu.sh
   ./install_ubuntu.sh
   ```

   **Windows:**
   ```batch
   install_windows.bat
   ```

These scripts will automatically create a virtual environment (`.venv`), install dependencies from `requirements.txt`, run database migrations, and collect static files.

## Usage

### 1. Start the Application
Run the execution script for your platform:

**macOS/Linux:**
```bash
./run.sh
```

**Windows:**
```batch
run_windows.bat
```

The application will be available at `http://127.0.0.1:8000`.

### 2. Configure Your VOD Directory
VODDER expects a specific folder hierarchy to correctly parse course sections and modules:

```text
Course Folder/
├── 1 - Section Title/
│   ├── 1.1 - Module Title/
│   │   ├── 1.1.1 - Video Name.mp4
│   │   └── 1.1.2 - Video Name.mp4
│   └── 1.2 - Module Title/
│       └── 1.2.1 - Video Name.mp4
└── 2 - Section Title/
    └── ...
```

1. Navigate to the **Settings** page in the web UI.
2. Provide the absolute path to your root course directory (e.g., `/Users/name/Movies/MyCourse`).
3. Click "Sync" to index the videos.

## Technology Stack

- **Backend:** [Django](https://www.djangoproject.com/)
- **Database:** [SQLite](https://www.sqlite.org/)
- **Static Assets:** [WhiteNoise](https://whitenoise.evans.io/en/stable/) (for efficient local serving)
- **Metadata:** [Mutagen](https://github.com/quodlibet/mutagen) (for extracting video duration)
- **Frontend:** Vanilla CSS (Modern Flexbox/Grid) & Django Templates

