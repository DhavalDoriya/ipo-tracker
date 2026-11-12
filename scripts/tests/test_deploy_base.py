"""The deploy base path must match the GitHub repo name, or every CSS/JS/font link 404s."""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def repo_name():
    try:
        out = subprocess.run(
            ["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return re.sub(r"\.git$", "", out.rstrip("/")).rsplit("/", 1)[-1]


class DeployBaseTests(unittest.TestCase):
    def test_default_base_matches_repo_name(self):
        name = repo_name()
        if not name:
            self.skipTest("no git remote")
        config = (ROOT / "astro.config.mjs").read_text()
        match = re.search(r"BASE_PATH \?\? '([^']+)'", config)
        self.assertIsNotNone(match, "BASE_PATH default not found")
        self.assertEqual(match.group(1), f"/{name}")

    def test_deploy_workflow_passes_base_from_repo_name(self):
        wf = (ROOT / ".github/workflows/deploy.yml").read_text()
        self.assertIn("BASE_PATH: /${{ github.event.repository.name }}", wf)


if __name__ == "__main__":
    unittest.main()
