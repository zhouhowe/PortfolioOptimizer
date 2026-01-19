import sys
import traceback

try:
    print("Importing app.main...")
    from app.main import app
    print("Import successful!")
except Exception:
    traceback.print_exc()
