import os
from os import stat
import subprocess
from typing import Optional
from pathlib import Path
import shutil

from big_git_python.git_error import GitError


class Repo:
    """
    A class representing a git repository.
    it allows to manage git from python with a simple interface, and without a global state (unlike gitpython) and without the need to use subprocess directly.
    """
    def __init__(self, url: Optional[str], path = "./"):
        """
        Initializes a new Repo instance with the specified URL and path.
         :param url: The URL of the git repository to clone.
         :param path: The local path where the repository should be initialized. Defaults to the current directory.
        """
        try:
            self.path = path
            folder_path = Path(self.path)
            folder_path.mkdir(parents=True, exist_ok=True)
            if url:
                self._clone(url)
                self.path = os.path.join(self.path, url.split("/")[-1].replace(".git", ""))
                print(f"Updated Repo path to: {self.path}")
            else:
                process = subprocess.run(["git", "init"], cwd=self.path)
                if process.stderr:
                    raise GitError(f"Failed to initialize git repository in {self.path}: {process.stderr.decode()}")
        except Exception as e:
            raise GitError(f"Failed to initialize Repo: {e}")


    def pull(self):
        """
        Pulls the latest changes from the remote repository into this Repo instance.
        """
        try: 
            print(f"Pulling latest changes in {self.path}")
            process = subprocess.run(["git", "pull"], cwd=self.path)
            if process.stderr:
                raise GitError(f"Failed to pull changes in {self.path}: {process.stderr.decode()}")
        except Exception as e:
            raise GitError(f"Failed to pull changes in {self.path}: {e}")


    def commit(self, message : str):
        """
        Commits changes in this Repo instance with the specified commit message.
         :param message: The commit message to use for the commit.
         """
        try:
            print(f"Committing changes in {self.path} with message: {message}")
            process = subprocess.run(["git", "add", "."], cwd=self.path)
            if process.stderr:
                raise GitError(f"Failed to add changes in {self.path}: {process.stderr.decode()}")
            process = subprocess.run(["git", "commit", "-m", message], cwd=self.path)
            if process.stderr:
                raise GitError(f"Failed to commit changes in {self.path}: {process.stderr.decode()}")
        except Exception as e:
            raise GitError(f"Failed to commit changes in {self.path}: {e}")

    def push(self):
        """
         Pushes committed changes from this Repo instance to the remote repository.
         """
        try:
            print(f"Pushing changes from {self.path}")
            process = subprocess.run(["git", "push"], cwd=self.path)
            if process.stderr:
                raise GitError(f"Failed to push changes from {self.path}: {process.stderr.decode()}")
        except Exception as e:
            raise GitError(f"Failed to push changes from {self.path}: {e}")

    def list_submodules(self) -> list[str]:
        """
         Lists the submodules in this Repo instance.
         :return: A list of submodule names.
         """
        try:
            modules_file = Path(os.path.join(self.path, ".gitmodules"))
            if not modules_file.exists():
                return []
            with open(modules_file, "r") as f:
                lines = f.readlines()
            submodules = []
            for line in lines:
                if line.strip().startswith("[submodule"):
                    submodule_name = line.strip().split('"')[1]
                    submodules.append(submodule_name)
            return submodules
        except Exception as e:
            raise GitError(f"Failed to list submodules in {self.path}: {e}")

    def add_submodule(self, url : str):
        """
         Adds a submodule to this Repo instance with the specified URL.
         :param url: The URL of the git repository to use as the submodule.
         """
        try:
            print(f"Adding submodule from URL {url} to {self.path}")
            process = subprocess.run(["git", "submodule", "add", url], cwd=self.path)
            if process.stderr:
                raise GitError(f"Failed to add submodule in {self.path}: {process.stderr.decode()}")
        except Exception as e:
            raise GitError(f"Failed to add submodule: {e}")

    def remove_submodule(self, name : str):
        """
         Removes a submodule from this Repo instance.
         :param name: The name of the submodule to remove.
         """
        try:
            print(f"Removing submodule {name} from {self.path}")
            process = subprocess.run(["git", "submodule", "deinit", "-f", name], cwd=self.path)
            if process.stderr:
                raise GitError(f"Failed to deinit submodule {name} in {self.path}: {process.stderr.decode()}")
            shutil.rmtree(os.path.join(self.path, ".git", "modules", name), ignore_errors=True, onerror=self._remove_readonly)
            process = subprocess.run(["git", "config", "-f" ,".gitmodules","--remove-section", f"submodule.{name}"], cwd=self.path)
        except Exception as e:
            raise GitError(f"Failed to remove submodule {name}: {e}")

    def remove_all_submodules(self):
        """
         Removes all submodules from this Repo instance.
         """
        for submodule in self.list_submodules():
            self.remove_submodule(submodule)
            print(f"Removed submodule {submodule} from {self.path}")
        print(f"All submodules removed from {self.path}")
        

    def _clone(self, url : str):
        """
        Clones a git repository from the specified URL into the path of this Repo instance.
         :param url: The URL of the git repository to clone."""
        try:
            print(f"Cloning {url} into {self.path}")            
            process = subprocess.run(["git", "clone", url] , cwd=self.path)
            
            if process.stderr:
                raise GitError(f"Failed to clone repository {url}: {process.stderr.decode()}")
        except Exception as e:
            raise GitError(f"Failed to clone repository {url}: {e}")
        
    def _remove_readonly(self, func : callable, path : str, excinfo : Exception):
        """
        Helper function to remove read-only files when deleting directories.
         :param func: The function that raised the exception.
         :param path: The path of the file that caused the exception.
         :param excinfo: The exception information.
         """
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print(f"Failed to remove read-only file {path}: {e}")