from pathlib import Path
from pydantic import BaseSettings, BaseModel
from logging import basicConfig, getLogger, FileHandler, StreamHandler, INFO
from yaml import load, SafeLoader


CONFIG_FILE = str(Path(__file__).parent.absolute()) + "/settings.yaml"
LOGFILE_FILE = str(Path(__file__).parent.absolute()) + "/utmn.log"
basicConfig(
    level=INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s():%(lineno)s] %(message)s",
    handlers=[FileHandler(LOGFILE_FILE), StreamHandler()],
)
with open(CONFIG_FILE, "r") as f:
    cfg = load(f, SafeLoader)


class App(BaseModel):
    usernameOrEmail: str
    password: str


class Settings(BaseSettings):
    app: App


settings = Settings.parse_obj(cfg)
