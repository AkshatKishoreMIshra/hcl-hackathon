import sys
import traceback
from pathlib import Path

try:
    import app.main
    res = "SUCCESS"
except Exception as e:
    res = traceback.format_exc()

Path("err_out.txt").write_text(res)
