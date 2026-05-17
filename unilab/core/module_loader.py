import importlib


class ModuleLoader:
    def load_class(self, module_path: str, class_name: str) -> type:
        module = importlib.import_module(module_path)

        if not hasattr(module, class_name):
            raise AttributeError(f"Class '{class_name}' not found in '{module_path}'")

        return getattr(module, class_name)
