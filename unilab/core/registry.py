class ModuleRegistry:
    def __init__(self) -> None:
        self._modules = {}

    def register(self, name: str, module: object) -> None:
        if name in self._modules:
            raise ValueError(f"Module '{name}' is already registered")

        self._modules[name] = module

    def get(self, name: str) -> object:
        if name not in self._modules:
            raise KeyError(f"Module '{name}' not found")

        return self._modules[name]

    def list_modules(self) -> list[str]:
        return list(self._modules.keys())
