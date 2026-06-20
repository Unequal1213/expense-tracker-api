import os
import subprocess
import sys
from pathlib import Path


def test_database_url_is_required(tmp_path) -> None:
    env = os.environ.copy()
    env.pop("DATABASE_URL", None)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import app.database.database",
        ],
        capture_output=True,
        check=False,
        cwd=tmp_path,
        env=env,
        text=True,
    )

    assert result.returncode != 0
    assert "DATABASE_URL environment variable is required" in result.stderr
