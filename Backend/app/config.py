from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    APP_NAME: str = "UNILAB Backend API"
    DEBUG: bool = True
    SIMULATION_MODE: bool = True 
    
    
    JAULA_SERIAL_PORT: str = "/dev/ttyUSB0"  
    JAULA_BAUDRATE: int = 115200
    
    CUBESAT_IP: str = "192.168.1.100"
    CUBESAT_UDP_PORT: int = 5005
    CUBESAT_HTTP_PORT: int = 80

    WS_UPDATE_INTERVAL: float = 1.0  
    
    KX: float = 54.169
    KY: float = 44.906
    KZ: float = 29.426
    
    MIN_CURRENT: float = 1.3  
    MAX_CURRENT: float = 3.5  
    MIN_FIELD: float = 0.0  
    MAX_FIELD: float = 150.0   
    
    class Config:
        env_file = ".env"

settings = Settings()