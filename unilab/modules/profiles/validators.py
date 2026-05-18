# unilab/modules/profiles/validators.py
from unilab.modules.profiles.waveforms import ProfileGenerator

class ProfileValidator:
    @staticmethod
    def is_safe_profile(generator: ProfileGenerator, max_value: float, max_duration: float) -> bool:
        """
        Valida que ningún paso exceda los límites físicos seguros del laboratorio.
        """
        if not generator.steps:
            return False # Un perfil vacío no se puede ejecutar
            
        for step in generator.steps:
            # Validar que los valores no superen el umbral máximo permitido
            if step.value > max_value or step.value < 0:
                return False
            # Validar que no haya tiempos negativos o exagerados
            if step.duration_seconds <= 0 or step.duration_seconds > max_duration:
                return False
                
        return True