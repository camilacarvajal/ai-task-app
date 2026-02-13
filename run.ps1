# Find Python and run: python -m streamlit run app.py
# Use from AI Task App folder: .\run.ps1
# Skips the Windows Store stub (fake python.exe that says "Python was not found").

$py = $null

# Prefer real installs on disk (avoid Store stub)
$searchPaths = @(
    "$env:LOCALAPPDATA\Programs\Python\Python*",
    "$env:APPDATA\Python\Python*",
    "$env:LOCALAPPDATA\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.*"
)
foreach ($d in $searchPaths) {
    $exe = Get-ChildItem -Path $d -Filter python.exe -Recurse -Depth 1 -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($exe) { $py = $exe.FullName; break }
}

# Fallback: PATH, but skip the WindowsApps stub (root python.exe that opens Store)
if (-not $py) {
    foreach ($cmd in @('python', 'python3', 'py')) {
        try {
            $p = Get-Command $cmd -ErrorAction SilentlyContinue
            if ($p) {
                $src = $p.Source
                if ($src -notmatch "WindowsApps\\python\.exe$") { $py = $src; break }
            }
        } catch {}
    }
}

if (-not $py) {
    Write-Host "Python not found. Install from https://www.python.org/downloads/ and check 'Add Python to PATH'."
    exit 1
}
& $py -m streamlit run app.py @args
