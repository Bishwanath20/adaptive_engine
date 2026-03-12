import sys, os
print('cwd', os.getcwd())
print('sys.path', sys.path)
try:
    import app
    print('import succeeded')
except Exception as e:
    print('import failed', repr(e))
