import os, sys
print("cwd", os.getcwd())
print("sys.path", sys.path)

try:
    import app
    print("app module available", app)
except Exception as e:
    print("import app failed", repr(e))

from uvicorn import run
run("app.main:app", reload=True)
