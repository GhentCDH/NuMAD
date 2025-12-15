import subprocess

from src.config import DB_STRING

subprocess.run(["eralchemy", "-i", DB_STRING, "-s", "public", "-o", "erd.md"])

subprocess.run(["sed", "-i", "s/public_//g", "erd.md"])
subprocess.run(
    ["sed", "-i", "-e", "/^<!--$/d", "-e", "/^-->$/d", "-e", "/!\[\]/d", "erd.md"]
)
subprocess.run(["mv", "erd.md", "erd.mermaid"])
