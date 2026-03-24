import os

# Set before any test module imports app, so Settings picks it up.
os.environ.setdefault("ADMIN_API_KEY", "test-admin-key")

TEST_API_KEY = os.environ["ADMIN_API_KEY"]
