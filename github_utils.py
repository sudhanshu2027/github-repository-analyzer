import os
import shutil
import tempfile
from git import Repo


def clone_repository(repo_url: str) -> str:
    """
    Clone a GitHub repository into a temporary directory.

    Args:
        repo_url (str): GitHub repository URL.

    Returns:
        str: Path to the cloned repository.
    """

    # Remove trailing slash if present
    repo_url = repo_url.rstrip("/")

    # Add .git if the user didn't include it
    if not repo_url.endswith(".git"):
        repo_url += ".git"

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="repo_")

    # Clone the repository
    Repo.clone_from(
        repo_url,
        temp_dir,
    )

    return temp_dir


def delete_repository(repo_path: str):
    """
    Delete the cloned temporary repository.

    Args:
        repo_path (str): Path to the cloned repository.
    """

    if repo_path and os.path.exists(repo_path):
        shutil.rmtree(
            repo_path,
            ignore_errors=True,
        )