import sys
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from pathlib import Path
from types import ModuleType


def load_module_from_path(module_name: str, module_path: Path) -> ModuleType:
    existing_module = sys.modules.get(module_name)
    if existing_module is not None:
        return existing_module

    module_spec = spec_from_file_location(module_name, module_path)
    if module_spec is None or module_spec.loader is None:
        raise ImportError(f"Unable to load module spec for {module_name} at {module_path}")

    module = module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    return module
