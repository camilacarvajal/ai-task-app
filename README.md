# Today.md UI

A small local web app that turns your `today.md` markdown file into a visual checklist. Only the task lines (`- [ ]` / `- [x]`) are interactive; everything else (title, rhythm, calendar, pipeline, deadlines) is read-only. Data stays in the file on your machine. Toggling a task updates the file and the UI re-reads it on every interaction.

## Run locally

1. **Clone or download** this folder.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   On Windows, if `python` or `pip` aren't found, use: `py -m pip install -r requirements.txt`

3. **Set the path to your today.md file:**
   - Copy `.env.example` to `.env`
   - Edit `.env` and set `TODAY_MD_PATH` to the full path of your `today.md`.
   - Example (Windows): `TODAY_MD_PATH=C:\Users\YourName\Desktop\Tasks\today.md`
   - Example (Mac/Linux): `TODAY_MD_PATH=/Users/yourname/Desktop/Tasks/today.md`

4. **Start the app:**
   ```bash
   python -m streamlit run app.py
   ```
   **Windows:** If `python` and `py` aren't found, use the PowerShell launcher from the app folder:
   ```powershell
   .\run.ps1
   ```
   It finds Python in common install locations and skips the Store stub. (Avoid `run.bat` if you get "Python was not found" — it can hit the Store stub when Python isn't on PATH.)
   Open the URL shown in the terminal (usually http://localhost:8501).

## Sharing

You can push this repo to GitHub so others can clone it and point `TODAY_MD_PATH` at their own `today.md`. No data is sent off your machine; the app only reads and writes the file you specify.
