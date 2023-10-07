from pathlib import Path


def pytester_path(pytester):
    if hasattr(pytester, "path"):
        return pytester.path
    return Path(pytester.tmpdir)  # pytest v5
