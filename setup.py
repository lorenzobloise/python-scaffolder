from setuptools import setup
from setuptools.command.install import install
from importlib.resources import files
from pathlib import Path

CONFIG_PATH = Path.home() / ".python-scaffolder" / "config.yaml"

class PostInstallCommand(install):
    def run(self):
        super().run()
        if not CONFIG_PATH.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            default = files("python_scaffolder").joinpath("default_config.yaml")
            with default.open() as src:
                CONFIG_PATH.write_text(src.read())
            print(f"[python-scaffolder] Created default config at {CONFIG_PATH}")

setup(
    cmdclass={"install": PostInstallCommand},
)
