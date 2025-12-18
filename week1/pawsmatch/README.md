# PawsMatch

A dog adoption web app that presents dog profiles with a "Like" (to adopt) or "Pass" interface, similar to popular matching apps.

## Project Structure

```
pawsmatch/
├── .env                  # Environment variables (not tracked in git)
├── .env.example          # Example environment file
├── .python-version       # Python version specification
├── generate_pets.py      # Script to generate dog profiles using Gemini AI
├── pets.json             # Generated dog profiles data
├── pyproject.toml        # Project configuration and dependencies
├── README.md             # This file
└── uv.lock               # Dependency lock file
```

## Data Generation Process

The `generate_pets.py` script uses Google's Gemini AI to generate dog profiles:

1. **API Configuration**: The script loads the `GOOGLE_API_KEY` from a `.env` file using `python-dotenv`
2. **AI Generation**: Uses the `gemini-3-flash-preview` model via the `google-genai` library
3. **Profile Structure**: Each dog profile contains:
   - `id`: Unique integer identifier (1-50)
   - `name`: Creative dog name
   - `bio`: 3-line adoption-focused biography in Spanish describing personality, ideal home, and adoption appeal
4. **Output**: Saves 50 dog profiles to `pets.json` with UTF-8 encoding

### Running the Data Generation Script

```bash
# Create .env file with your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run the script
uv run python generate_pets.py
```

## Stack

- **Package Manager**: [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- **Language**: Python 3.13+
- **AI Model**: Google Gemini 3 Flash Preview (`gemini-3-flash-preview`)
- **Dependencies**:
  - `google-genai` - Google Generative AI Python client
  - `python-dotenv` - Environment variable management

## Setup

1. Install uv if not already installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository and navigate to the project:
   ```bash
   cd pawsmatch
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   # Add your GOOGLE_API_KEY to .env
   ```

5. Generate pet data:
   ```bash
   uv run python generate_pets.py
   ```

## Sample Data

Each dog profile in `pets.json` follows this format:

```json
{
  "id": 1,
  "name": "Max",
  "bio": "Soy un perrito lleno de energía y muy sociable con otros animales.\nBusco un hogar con patio grande donde pueda correr y jugar.\nSeré tu compañero de aventuras más leal desde el primer día."
}
```
