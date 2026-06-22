from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = "UniLab"
    debug: bool = True
    database_url: str = "sqlite:///unilab.db"
    modules_path: str = "unilab.modules"

    # Configuración ESP32 serial
    esp32_port: str = "/dev/ttyUSB0"  
    esp32_baudrate: int = 115200
    esp32_timeout: float = 1.0
    esp32_source: str = "esp32_01"