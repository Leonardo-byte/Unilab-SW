from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = "UniLab"
    debug: bool = True
    database_url: str = "sqlite:///unilab.db"
    modules_path: str = "unilab.modules"