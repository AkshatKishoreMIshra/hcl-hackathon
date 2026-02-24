import subprocess
import sys

try:
    result = subprocess.run([sys.executable, "-c", "import app.main"], capture_output=True, text=True)
    with open('output.txt', 'w') as f:
        f.write(f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nRC:{result.returncode}")
except Exception as e:
    with open('output.txt', 'w') as f:
        f.write(str(e))
