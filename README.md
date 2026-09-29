# GitHub Intelligence Dashboard

A fast, lightweight dashboard that gives you instant insights into any public GitHub profile. It shows developer activity, code languages used, and account stats.

## Preview

![App Preview](assets/app-preview.png)

**🔗 [View Live Application](https://jatinp-inteldashboard.streamlit.app/)**

## Core Features

- **Profile Overview:** See the user's basic info, account age, and followers.
- **Codebase Analysis:** Beautiful charts showing which programming languages they use most.
- **Activity Metrics:** Keep track of recent updates and public events.
- **Smart Data Fetching:** Directly talks to GitHub's API while being mindful of limits.

## Architecture & Technical Decisions

This project was built with a focus on speed and reliability:

- **Smart Caching:** The app uses `@st.cache_data` to save API results. This means if you search the same user twice, it loads instantly and doesn't waste API calls.
- **Rate Limit Protection:** GitHub only allows 60 free requests per hour per IP. The dashboard catches errors (like `403 Rate Limit Exceeded`) gracefully and tells the user exactly what went wrong, rather than just crashing.
- **Timezone Aware:** All dates fetched from GitHub are converted properly to UTC so they display correctly no matter where the user is.

## UI & Design Decisions

- **Terminal Aesthetic:** A custom `style.css` gives the app a clean, retro "Terminal" look.
- **System Fonts:** To keep the app loading as fast as possible, it relies on fonts that are already installed on your computer (like `Consolas` or `Monaco`) instead of forcing you to download heavy web fonts.

## Tech Stack

- **Frontend & Logic:** Python + Streamlit
- **Data Handling:** Pandas
- **Charts:** Altair
- **Network:** Requests (RESTful APIs)

## Running it Locally

1. Make sure you have Python installed.
2. Clone this project.
3. Turn on your virtual environment (`.venv`).
4. Install the required tools:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the app:

   ```bash
   streamlit run app.py
   ```

## Deployment

This application is deployed via Streamlit Community Cloud.

**Live Application:** <https://jatinp-inteldashboard.streamlit.app/>
