from typing import Any

from unilab.config.settings import Settings
from unilab.contracts.protocols import ModuleProtocol
from unilab.core.experiment_service import ExperimentService
from unilab.core.module_loader import ModuleLoader
from unilab.core.registry import ModuleRegistry


class UniLabApp:
    """
    Aplicación principal de UniLab.

    Esta clase coordina los componentes principales del sistema:
    configuración global, registro de módulos, carga dinámica de módulos
    y servicio de experimentos.

    No implementa la lógica interna de cada módulo. Su función es actuar
    como punto central de integración.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        """
        Inicializa la aplicación UniLab.

        Args:
            settings: Configuración global opcional. Si no se proporciona,
            se crea una configuración por defecto.
        """

        self.settings = settings or Settings()
        self.registry = ModuleRegistry()
        self.loader = ModuleLoader()
        self.experiments = ExperimentService()
        self._is_setup = False

    def setup(self) -> None:
        """
        Inicializa la aplicación y todos los módulos registrados.

        Este método llama a setup() en cada módulo registrado.
        """

        for module in self.registry.get_all().values():
            module.setup()

        self._is_setup = True

    def shutdown(self) -> None:
        """
        Apaga la aplicación y libera recursos de los módulos registrados.

        Este método llama a shutdown() en cada módulo registrado.
        Si algún módulo falla al apagarse, se propaga el error.
        """

        for module in self.registry.get_all().values():
            module.shutdown()

        self._is_setup = False

    def register_module(self, name: str, module: ModuleProtocol) -> None:
        """
        Registra un módulo en la aplicación.

        Args:
            name: Nombre único del módulo.
            module: Objeto que implementa ModuleProtocol.
        """

        self.registry.register(name, module)

    def unregister_module(self, name: str) -> ModuleProtocol:
        """
        Elimina un módulo registrado.

        Args:
            name: Nombre del módulo.

        Returns:
            El módulo eliminado.
        """

        return self.registry.unregister(name)

    def get_module(self, name: str) -> ModuleProtocol:
        """
        Obtiene un módulo registrado por nombre.

        Args:
            name: Nombre del módulo.

        Returns:
            Módulo registrado.
        """

        return self.registry.get(name)

    def has_module(self, name: str) -> bool:
        """
        Verifica si un módulo está registrado.

        Args:
            name: Nombre del módulo.

        Returns:
            True si el módulo existe, False en caso contrario.
        """

        return self.registry.exists(name)

    def list_modules(self) -> list[str]:
        """
        Lista los nombres de los módulos registrados.

        Returns:
            Lista de nombres de módulos.
        """

        return self.registry.list_modules()

    def load_module_class(self, module_path: str, class_name: str) -> type:
        """
        Carga una clase de módulo usando el ModuleLoader.

        Args:
            module_path: Ruta importable del módulo.
            class_name: Nombre de la clase.

        Returns:
            Clase cargada.
        """

        return self.loader.load_class(module_path, class_name)

    def create_module_instance(
        self,
        module_path: str,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Carga una clase y crea una instancia.

        Args:
            module_path: Ruta importable del módulo.
            class_name: Nombre de la clase.
            *args: Argumentos posicionales para el constructor.
            **kwargs: Argumentos nombrados para el constructor.

        Returns:
            Instancia de la clase cargada.
        """

        return self.loader.create_instance(
            module_path,
            class_name,
            *args,
            **kwargs,
        )

    def load_and_register_module(
        self,
        name: str,
        module_path: str,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> ModuleProtocol:
        """
        Carga dinámicamente un módulo, crea una instancia y lo registra.

        Args:
            name: Nombre con el que se registrará el módulo.
            module_path: Ruta importable del módulo.
            class_name: Nombre de la clase.
            *args: Argumentos posicionales para el constructor.
            **kwargs: Argumentos nombrados para el constructor.

        Returns:
            Módulo creado y registrado.
        """

        module = self.loader.create_instance(
            module_path,
            class_name,
            *args,
            **kwargs,
        )

        self.register_module(name, module)

        return module

    def get_status(self) -> dict[str, Any]:
        """
        Devuelve un resumen general del estado de la aplicación.

        Returns:
            Diccionario con información del estado general.
        """

        return {
            "app_name": self.settings.app_name,
            "debug": self.settings.debug,
            "is_setup": self._is_setup,
            "modules_count": self.registry.count(),
            "modules": self.registry.list_modules(),
            "experiment_status": self.experiments.get_status(),
        }

    def get_modules_status(self) -> dict[str, dict[str, Any]]:
        """
        Devuelve el estado reportado por todos los módulos registrados.

        Returns:
            Diccionario con el estado de cada módulo.
        """

        return self.registry.get_status_summary()