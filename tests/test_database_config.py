import os
import subprocess
import sys


def test_database_url_is_required() -> None:
    env = os.environ.copy()
    env.pop("DATABASE_URL", None)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import app.database.database",
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert result.returncode != 0
    assert "DATABASE_URL environment variable is required" in result.stderr
