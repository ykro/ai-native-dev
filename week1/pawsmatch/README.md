# PawsMatch

![PawsMatch Home](assets/screenshot.png)

PawsMatch is a pet adoption application designed to connect loving families with pets in need of a home. The application features a warm and friendly design with a modern technical stack.

## Tech Stack

- **Vite (v7.2+)**: Next-generation frontend tooling for fast development and optimized builds.
- **React (v19+)**: A JavaScript library for building user interfaces with a focus on component-based architecture.
- **Tailwind CSS (v4+)**: Utility-first CSS framework with a CSS-first configuration and high-performance engine.
- **TypeScript**: Static typing for enhanced developer experience and code reliability.

## Architecture

The project follows a standard React directory structure in the `app/` folder:

- `app/src/components/`: Reusable UI components.
- `app/src/hooks/`: Custom React hooks for shared logic.
- `app/src/services/`: API and data fetching services.
- `app/src/types/`: TypeScript interfaces and type definitions.
- `app/src/data/`: Static assets and mock data.

## Design System

PawsMatch uses a "warm and friendly" color palette configured in `app/src/index.css` using Tailwind CSS 4's `@theme` block. This includes:
- **Warm Palette**: Earthy oranges and browns for a cozy feel.
- **Friendly Palette**: Soft greens for growth and positivity.
- **Typography**: Focused on readability and a premium aesthetic using modern sans-serif fonts.

## Getting Started

1.  Navigate to the `app/` directory.
2.  Install dependencies: `npm install`
3.  Run development server: `npm run dev`
4.  Build for production: `npm run build`

## Asset Generation

To generate fresh mock data for the application, use the provided Python script in the `asset-generation/` directory. This script uses Google's Gemini API to create unique dog profiles.

### Prerequisites
- Python installed
- `uv` package manager (recommended) or `pip`
- A Google Cloud project with Vertex AI enabled or a Gemini API key

### Running the Generator

1.  Navigate to the `asset-generation/` directory.
2.  Set your API key:
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```
3.  Run the script:
    ```bash
    # Using uv (recommended)
    uv run main.py

    # Or using standard python
    # pip install -r requirements.txt (if available)
    python main.py
    ```
4.  The script will generate a new `pets.json` file. Copy this file to `app/src/data/pets.json` to update the app data.
