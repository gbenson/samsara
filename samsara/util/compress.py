import gzip
import os

def attempt_compression(path, payload = None):
    if payload is None:
        payload = open(path, "r").read()
    path += ".gz"
    gzip.open(path, "w").write(payload)
    if os.path.getsize(path) > len(payload):
        os.unlink(path)
