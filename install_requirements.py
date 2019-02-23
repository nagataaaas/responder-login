import sys
import os

if sys.version_info <= (3, 6):
    raise AssertionError("Responder only supports 3.6+")

os.system("pip install -r requirements.txt")
