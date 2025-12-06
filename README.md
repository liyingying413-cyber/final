# Emotion × City × Memory — Poster Generator

This repository contains a Streamlit app that:
- Asks user to input a city name first, then a memory about that city.
- Uses OpenAI (new SDK) to analyze the text (emotions, palette, intensity, keywords).
  If an OpenAI API key is not available, a deterministic local analyzer is used as fallback.
- Generates an abstract poster image based on the analysis, with style presets, seed, wobble.
- Shows analysis results and offers PNG download.

## Run locally
1. Create virtual env and install:
   ```
   pip install -r requirements.txt
   ```
2. (Optional) Create `.streamlit/secrets.toml` with your OpenAI key for analysis:
   ```
   OPENAI_API_KEY = "sk-..."
   ```
3. Run:
   ```
   streamlit run app.py
   ```

## Deploy to Streamlit Cloud
- Push this repo to GitHub and create a new app on Streamlit Cloud.
- Add `OPENAI_API_KEY` in the app's Secrets (if you want to use the real OpenAI analyzer).