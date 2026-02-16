# Changelog

## Unreleased

### Added
- **5-day weather in sidebar** — Optional. Set `OPENWEATHER_API_KEY` and `WEATHER_CITY` (or `WEATHER_LAT`/`WEATHER_LON`) in `.env`; forecast cached 10 min.
- **Cursor command** — `ScheduleTodayCursorPrompt.txt` and `.cursor/commands/whatsuptoday.md`; copy into `.cursor/commands` to generate app-compatible `today.md` from Cursor. README updated.

### Changed
- **today.md date parsing** — Recognizes `# Sunday, February 15, 2026` (and `# Feb 15, 2026`) so "Plan is from another day" no longer triggers on that format.
- **CSS** — Table/hr styling targets `.plan-section` instead of Streamlit’s emotion cache class. Checkbox styling uses `[class*="st-key-task_"]`.

### Fixed
- **Stale plan false positive** — Plans with `# Day, Month Date, Year` in the first line are now parsed correctly.
- **Forecast on every rerun** — Forecast API cached 10 min (`@st.cache_data(ttl=600)`).
- **Python 3.12** — Replaced deprecated `datetime.utcfromtimestamp` with `fromtimestamp(ts, tz=timezone.utc)`.

### Security
- **XSS from today.md** — Markdown→HTML is sanitized with `bleach` before `unsafe_allow_html`.
- **Geocoding** — OpenWeatherMap geo endpoint uses HTTPS.

### Other
- **Logging** — App logs `load_and_parse` and `toggle_task` failures; weather_forecast logs geocoding failures at debug.
- **Deps** — `bleach>=6.0.0` added to requirements.
