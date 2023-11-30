"""Convert tutorial notebooks and create a zip file with exercises."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import zipfile

import nbformat
from nbconvert.exporters import NotebookExporter
from nbconvert.exporters.exporter import ResourcesDict
from nbconvert.preprocessors import ClearOutputPreprocessor, Preprocessor
from traitlets import Unicode
from traitlets.config import Config

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MAIN_DIR = os.path.join(CURRENT_DIR, "..")
TUTORIALS_DIR = os.path.join(CURRENT_DIR, "tutorials")
EXERCISES_DIR = os.path.join(TUTORIALS_DIR, "exercises")


class ClearSolutionsPreProcessor(Preprocessor):
    """Remove solutions from a notebook.

    Notes
    -----
    The implementation of this class is inspired by the ClearSolutions preprocessor from
    the nbgrader package.
    """

    solution_start = Unicode("### BEGIN SOLUTION", config=True)
    solution_end = Unicode("### END SOLUTION", config=True)
    solution_code_subs = Unicode("###\n### YOUR CODE HERE\n###", config=True)
    solution_text_subs = Unicode("YOUR ANSWER HERE", config=True)

    def _replace_solution_regions(self, cell: nbformat.NotebookNode):
        """Replace solution regions in a cell."""
        if cell.cell_type == "code":
            solution_subs = self.solution_code_subs.splitlines()
        else:
            solution_subs = self.solution_text_subs.splitlines()

        new_lines = []
        in_solution = False

        for line in cell.source.splitlines():
            if self.solution_start in line and not in_solution:
                in_solution = True
                indent = re.match(r"\s*", line).group(0)
                new_lines.extend([indent + line for line in solution_subs])
            elif in_solution and self.solution_end in line:
                in_solution = False
            elif not in_solution:
                new_lines.append(line)
        if in_solution:
            raise ValueError("Solution region not closed")
        cell.source = "\n".join(new_lines)

    def preprocess_cell(self, cell: nbformat.NotebookNode, resources: ResourcesDict,
                        index: int) -> tuple[nbformat.NotebookNode, ResourcesDict]:
        """Preprocess a cell."""
        self._replace_solution_regions(cell)
        return cell, resources


class UpdateImagePathsPreprocessor(Preprocessor):
    """Update image paths in a notebook."""

    def preprocess(self, nb: nbformat.NotebookNode, resources: ResourcesDict
                   ) -> tuple[nbformat.NotebookNode, ResourcesDict]:
        """Preprocess a notebook."""
        resources["required_files"] = {}
        return super().preprocess(nb, resources)

    def preprocess_cell(self, cell: nbformat.NotebookNode, resources: ResourcesDict,
                        index: int) -> tuple[nbformat.NotebookNode, ResourcesDict]:
        """Preprocess a cell."""

        def replace(match):
            path = match.group(2)
            if path.startswith("http"):
                return match.group()
            new_path = os.path.join(".", "images", os.path.basename(path))
            resources["required_files"][path] = new_path
            return f'<img{match.group(1)} src="{new_path}"'

        if cell.cell_type == "markdown":
            # replace with multiline being true
            cell.source = re.sub(r'<img([^>]+)src="([^"]+)"', replace, cell.source,
                                 flags=re.M)

        return cell, resources


def convert_notebook(input_file: str, output_file: str
                     ) -> tuple[nbformat.NotebookNode, ResourcesDict]:
    """Convert a solution notebook to an exercise notebook."""
    with open(input_file, encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    c = Config()
    c.NotebookExporter.preprocessors = [
        ClearOutputPreprocessor, ClearSolutionsPreProcessor,
        UpdateImagePathsPreprocessor]
    exporter = NotebookExporter(config=c)
    body, resources = exporter.from_notebook_node(nb)
    with open(output_file, "w") as f:
        f.write(body)
    return body, resources


def main():
    """Convert notebooks and create a zip file with exercises."""
    required_files = {}

    # Create a folder with exercise notebooks.
    if not os.path.isdir(EXERCISES_DIR):
        os.mkdir(EXERCISES_DIR)
    notebooks = [f for f in os.listdir(TUTORIALS_DIR) if f.endswith(".ipynb")]
    for notebook in notebooks:
        body, resources = convert_notebook(os.path.join(TUTORIALS_DIR, notebook),
                                           os.path.join(EXERCISES_DIR, notebook))
        required_files.update(resources["required_files"])

    # Create a zip file with exercise notebooks.
    create_zip(required_files)

    # Execute notebooks.
    notebooks = notebooks_to_execute()
    if notebooks:
        command = get_command_environment()
        install_local_brim_version(command)
        for notebook in notebooks:
            execute_notebook(notebook, command)


def create_zip(required_files: dict[str, str]) -> None:
    """Create a zip file with exercise notebooks."""
    # Create a folder with files to be zipped.
    zip_dir = os.path.join(TUTORIALS_DIR, "zip")
    if os.path.isdir(zip_dir):
        shutil.rmtree(zip_dir)
    os.mkdir(zip_dir)
    os.mkdir(os.path.join(zip_dir, "images"))
    for file in os.listdir(EXERCISES_DIR):
        shutil.copy(os.path.join(EXERCISES_DIR, file), zip_dir)
    for file, new_location in required_files.items():
        shutil.copy(os.path.join(TUTORIALS_DIR, file),
                    os.path.join(zip_dir, new_location))
    for file in ("README.md", "tutorials_environment.yml"):
        shutil.copy(os.path.join(TUTORIALS_DIR, file), zip_dir)

    # Create a zip file.
    with zipfile.ZipFile(os.path.join(TUTORIALS_DIR, "tutorials.zip"), "w") as f:
        for root, _dirs, files in os.walk(zip_dir):
            for file in files:
                f.write(os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), zip_dir))

    # Remove the folder with files to be zipped.
    shutil.rmtree(zip_dir)


def notebook_is_executed(nb: str | nbformat.NotebookNode) -> bool:
    """Check if a notebook is executed."""
    if isinstance(nb, str):
        with open(nb, encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
    for _cell in nb.cells:
        # If statement is from the nbsphinx source code.
        if (
                # At least one code cell actually containing source code:
                any(c.source for c in nb.cells if c.cell_type == "code") and
                # No outputs, not even a prompt number:
                not any(c.get("outputs") or c.get("execution_count")
                        for c in nb.cells if c.cell_type == "code")
        ):
            return False
    return True


def notebooks_to_execute() -> tuple[str]:
    """Return a list of notebooks that need to be executed."""
    notebooks = [os.path.join(TUTORIALS_DIR, f)
                 for f in os.listdir(TUTORIALS_DIR) if f.endswith(".ipynb")]
    return tuple(nb for nb in notebooks if not notebook_is_executed(nb))


def get_tutorials_environment_name():
    """Return the name of the tutorials' environment."""
    with open(os.path.join(TUTORIALS_DIR, "tutorials_environment.yml")) as f:
        for line in f:
            if line.startswith("name:"):
                return line.split(":")[1].strip()


def get_command_environment() -> str:
    """Check if the tutorials' environment exists."""
    commands = ("mamba", "micromamba", "conda")
    for command in commands:
        # Check if command is installed.
        if shutil.which(command) is None:
            if command == commands[-1]:
                raise RuntimeError(f"{command.capitalize()} is not installed.")
            continue
        try:  # If the command cannot be found, try using the full path.
            subprocess.run([command])
        except FileNotFoundError:
            command = subprocess.run(
                ["where", "mamba"], capture_output=True).stdout.decode().strip()
        # Check if the tutorials' environment exists.
        env = get_tutorials_environment_name()
        if env in subprocess.run([command, "env", "list"], capture_output=True
                              ).stdout.decode():
            return command
        else:
            if command == commands[-1]:
                raise RuntimeError(f"The {command} environment '{env}' does not exist.")


def install_local_brim_version(command: str) -> None:
    """Install a local version of BRiM."""
    env = get_tutorials_environment_name()
    subprocess.run([command, "uninstall", "-n", env, "brim", "-y"])
    subprocess.run([command, "run", "-n", env, "pip", "install", "-e", MAIN_DIR])


def execute_notebook(nb: str, command: str = "conda") -> None:
    """Execute a notebook."""
    subprocess.run([command, "run", "-n", get_tutorials_environment_name(),
                    "jupyter", "nbconvert", nb, "--execute", "--inplace"])


if __name__ == "__main__":
    main()
