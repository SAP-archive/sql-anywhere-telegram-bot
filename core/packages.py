import importlib
import pkgutil
from types import ModuleType
from typing import Dict, List

from loguru import logger


class PackagesLoader:
    """Imports all required modules for all scripts in sub-folders.

    Attributes:
        modules (dict): A dict to store the modules' names and its imports.
    """

    def __init__(self):
        self.modules = {}

    def load_package(self, package: str, recursive: bool = True) -> Dict[str, ModuleType]:
        """Checks and loads a single package's modules.

        Args:
            package (str): Name of the imported package.
            [optional] recursive (boolean): Goes through the package's sub-packages recursively if True.

        Returns:
            results (dict): A dict of packages' name-module pairs.
        """

        if isinstance(package, str):
            pkg = importlib.import_module(package)

        package_name = pkg.__name__
        results = {package_name: pkg}

        for importer, modname, ispkg in pkgutil.walk_packages([package_name]):
            full_name = f"{package_name}.{modname}"
            logger.debug('Loading package "{}"', full_name)
            self.modules[full_name] = results[full_name] = importlib.import_module(full_name)

            if recursive and ispkg:
                results.update(self.load_package(full_name))

        return results

    def load_packages(self, packages: List[str], recursive: bool = True) -> List[Dict[str, ModuleType]]:
        """Loads all required modules from a list of packages.

        Args:
            packages (list): A list of package names to import modules from.
            [optional] recursive (boolean): Goes through the package's sub-packages recursively if True.

        Returns:
            results (list): A list of dicts that contain the packages' name-module pairs.
        """

        result = []
        logger.debug("Loading all required packages")

        for package in packages:
            result.append(self.load_package(package, recursive))

        logger.success("All packages have been loaded")
        return result
