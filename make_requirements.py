import subprocess
import sys

wanted = {
    "fastapi", "uvicorn", "python-multipart", "pandas", "numpy",
    "scikit-learn", "statsmodels", "scipy", "sqlalchemy",
}

out = subprocess.check_output(
    [sys.executable, "-m", "pip", "freeze"], text=True
)
lines = [
    line for line in out.splitlines()
    if line.split("==")[0].lower().replace("_", "-") in wanted
]

with open("requirements.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")

print("\n".join(lines))