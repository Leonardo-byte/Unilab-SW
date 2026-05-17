from typing import Any

from unilab.contracts.protocols import ModuleProtocol


class ModuleRegistry:
    """
    Registro central de módulos de UniLab.

    Esta clase permite registrar, buscar, listar y eliminar módulos
    que forman parte del sistema, como instrumentos, adquisición,
    simulación, scheduler, safety, storage, web, SiLA, entre otros.

    El registry no ejecuta la lógica interna de los módulos.
    Solo mantiene referencias organizadas a ellos.
    """

    def __init__(self) -> None:
        """
        Inicializa un registro vacío de módulos.
        """
        self._modules: dict[str, ModuleProtocol] = {}

    def register(self, name: str, module: ModuleProtocol) -> None:
        """
        Registra un módulo en el sistema.

        Args:
            name: Nombre único del módulo.
            module: Objeto que implementa ModuleProtocol.

        Raises:
            ValueError: Si el nombre está vacío o ya existe.
            TypeError: Si el objeto no cumple con ModuleProtocol.
        """

        self._validate_name(name)

        if name in self._modules:
            raise ValueError(f"El módulo '{name}' ya está registrado.")

        if not isinstance(module, ModuleProtocol):
            raise TypeError(
                f"El módulo '{name}' no cumple con ModuleProtocol. "
                "Debe implementar name, setup(), shutdown() y get_status()."
            )

        self._modules[name] = module

    def get(self, name: str) -> ModuleProtocol:
        """
        Obtiene un módulo registrado por su nombre.

        Args:
            name: Nombre del módulo.

        Returns:
            El módulo registrado.

        Raises:
            ValueError: Si el nombre está vacío.
            KeyError: Si el módulo no existe.
        """

        self._validate_name(name)

        if name not in self._modules:
            raise KeyError(f"El módulo '{name}' no fue encontrado.")

        return self._modules[name]

    def unregister(self, name: str) -> ModuleProtocol:
        """
        Elimina un módulo del registro y lo retorna.

        Args:
            name: Nombre del módulo a eliminar.

        Returns:
            El módulo eliminado.

        Raises:
            ValueError: Si el nombre está vacío.
            KeyError: Si el módulo no existe.
        """

        self._validate_name(name)

        if name not in self._modules:
            raise KeyError(f"El módulo '{name}' no fue encontrado.")

        return self._modules.pop(name)

    def exists(self, name: str) -> bool:
        """
        Verifica si un módulo está registrado.

        Args:
            name: Nombre del módulo.

        Returns:
            True si el módulo existe, False en caso contrario.
        """

        self._validate_name(name)

        return name in self._modules

    def list_modules(self) -> list[str]:
        """
        Lista los nombres de todos los módulos registrados.

        Returns:
            Lista de nombres de módulos.
        """

        return list(self._modules.keys())

    def get_all(self) -> dict[str, ModuleProtocol]:
        """
        Devuelve una copia del diccionario de módulos registrados.

        Returns:
            Copia del registro de módulos.
        """

        return self._modules.copy()

    def count(self) -> int:
        """
        Devuelve la cantidad de módulos registrados.

        Returns:
            Número de módulos registrados.
        """

        return len(self._modules)

    def clear(self) -> None:
        """
        Elimina todos los módulos del registro.
        """

        self._modules.clear()

    def get_status_summary(self) -> dict[str, dict[str, Any]]:
        """
        Devuelve un resumen del estado de todos los módulos registrados.

        Returns:
            Diccionario con el estado reportado por cada módulo.
        """

        summary: dict[str, dict[str, Any]] = {}

        for name, module in self._modules.items():
            try:
                summary[name] = module.get_status()
            except Exception as exc:
                summary[name] = {
                    "status": "error",
                    "message": str(exc),
                }

        return summary

    @staticmethod
    def _validate_name(name: str) -> None:
        """
        Valida que el nombre del módulo sea un texto no vacío.

        Args:
            name: Nombre a validar.

        Raises:
            ValueError: Si el nombre no es válido.
        """

        if not isinstance(name, str):
            raise ValueError("El nombre del módulo debe ser un string.")

        if not name.strip():
            raise ValueError("El nombre del módulo no puede estar vacío.")