import importlib
from types import ModuleType
from typing import Any


class ModuleLoader:
    """
    Cargador dinámico de módulos y clases.

    Esta clase permite importar módulos de Python usando su ruta como texto
    y obtener clases específicas dentro de esos módulos.

    Es útil para que UniLab pueda cargar componentes de forma dinámica,
    por ejemplo instrumentos, simuladores, schedulers o módulos externos.
    """

    def load_module(self, module_path: str) -> ModuleType:
        """
        Carga un módulo de Python a partir de su ruta.

        Args:
            module_path: Ruta importable del módulo.
                Ejemplo: "unilab.modules.instruments.mock"

        Returns:
            El módulo importado.

        Raises:
            ValueError: Si module_path está vacío.
            ImportError: Si el módulo no puede importarse.
        """

        self._validate_text(module_path, "La ruta del módulo")

        try:
            return importlib.import_module(module_path)
        except ModuleNotFoundError as exc:
            raise ImportError(
                f"No se pudo importar el módulo '{module_path}'. "
                "Verifica que la ruta exista y que tenga __init__.py si corresponde."
            ) from exc

    def load_class(self, module_path: str, class_name: str) -> type:
        """
        Carga una clase desde un módulo importable.

        Args:
            module_path: Ruta importable del módulo.
                Ejemplo: "unilab.modules.instruments.mock"
            class_name: Nombre de la clase dentro del módulo.
                Ejemplo: "MockInstrument"

        Returns:
            La clase solicitada.

        Raises:
            ValueError: Si module_path o class_name están vacíos.
            ImportError: Si el módulo no puede importarse.
            AttributeError: Si la clase no existe dentro del módulo.
            TypeError: Si el atributo encontrado no es una clase.
        """

        self._validate_text(module_path, "La ruta del módulo")
        self._validate_text(class_name, "El nombre de la clase")

        module = self.load_module(module_path)

        if not hasattr(module, class_name):
            raise AttributeError(
                f"La clase '{class_name}' no fue encontrada en el módulo '{module_path}'."
            )

        loaded_object = getattr(module, class_name)

        if not isinstance(loaded_object, type):
            raise TypeError(
                f"'{class_name}' existe en '{module_path}', pero no es una clase."
            )

        return loaded_object

    def create_instance(
        self,
        module_path: str,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Carga una clase y crea una instancia de ella.

        Args:
            module_path: Ruta importable del módulo.
            class_name: Nombre de la clase.
            *args: Argumentos posicionales para el constructor.
            **kwargs: Argumentos nombrados para el constructor.

        Returns:
            Instancia de la clase cargada.

        Raises:
            Los mismos errores que load_class, además de errores propios
            del constructor de la clase.
        """

        loaded_class = self.load_class(module_path, class_name)

        try:
            return loaded_class(*args, **kwargs)
        except TypeError as exc:
            raise TypeError(
                f"No se pudo crear una instancia de '{class_name}'. "
                "Verifica los argumentos del constructor."
            ) from exc

    @staticmethod
    def _validate_text(value: str, field_name: str) -> None:
        """
        Valida que un valor de texto sea un string no vacío.

        Args:
            value: Texto a validar.
            field_name: Nombre descriptivo del campo.

        Raises:
            ValueError: Si el texto no es válido.
        """

        if not isinstance(value, str):
            raise ValueError(f"{field_name} debe ser un string.")

        if not value.strip():
            raise ValueError(f"{field_name} no puede estar vacío.")