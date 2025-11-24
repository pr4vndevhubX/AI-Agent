````markdown
# Setup Python `.venv` with uv on Windows (PowerShell)

A step-by-step guide to fix `.venv`, uv, and VS Code interpreter issues.

---

## 1. Check current directory

```powershell
pwd
````

Verify you are in the project folder.

---

## 2. Remove old virtual environment

```powershell
rd /s /q .venv
```

Deletes any existing `.venv` to start fresh.

---

## 3. Install uv (Universal Virtual Environment manager)

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Downloads and installs `uv`.

---

## 4. Verify uv installation folder

```powershell
dir "$env:USERPROFILE\.local\bin"
```

Ensure `uv.exe`, `uvx.exe`, and `uvw.exe` exist.

---

## 5. Add uv to PATH for current session

```powershell
$env:PATH="$env:USERPROFILE\.local\bin;$env:PATH"
```

Temporary fix if `setx` truncates PATH.

---

## 6. Verify uv is recognized

```powershell
uv --version
```

Should output uv version, e.g., `0.9.11`.

---

## 7. Create & sync the environment

```powershell
uv sync
```

Creates `.venv` and installs dependencies from `pyproject.toml`.

---

## 8. Activate the virtual environment

```powershell
.\.venv\Scripts\activate
```

You should see `(.venv)` in the prompt.

---

## 9. Check Python executable

```powershell
python -c "import sys; print(sys.executable)"
```

Should point to `.venv\Scripts\python.exe`.

---

## 10. Open project in VS Code

```powershell
code .
```

---

## 11. Select Python interpreter in VS Code

* Press `Ctrl + Shift + P` → `Python: Select Interpreter`
* Choose `.venv\Scripts\python.exe`

---

## 12. Force VS Code to use `.venv` permanently

Edit `.vscode/settings.json` and add:

```json
{
  "python.defaultInterpreterPath": ".venv\\Scripts\\python.exe"
}
```

---

## 13. Verify Python version inside `.venv`

```powershell
python --version
```

---

## 14. Add Jupyter kernel support

```powershell
uv add ipykernel
```

---

## 15. Register Jupyter kernel

```powershell
python -m ipykernel install --user --name=mark-stats-env --display-name "Mark Stats (Python 3.11 - uv)"
```

---

## 16. Verify `.venv` contents

```powershell
dir .venv\Scripts
```

Ensure `python.exe`, `pip.exe`, and `activate` scripts exist.

---

## Notes

* For **permanent uv PATH fix**, go to **Windows Settings → Environment Variables → User Variables → Path** and add `C:\Users\psuresh\.local\bin`.
* Always **open a new PowerShell window** after modifying PATH or installing uv.
* Commands assume **Windows PowerShell / WSL**.

```

---
