from pydantic import BaseSettings


class Setting(BaseSettings):
    PG_USER: str
    PG_PASSWORD: str
    PG_HOST: str = "localhost"
    PG_PORT: str = "5432"
    PG_DB: str


# TODO Возможно, этому не место тут, но пусть будет в настройках
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    WHITE = '\033[97m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


setting = Setting()
color = Color()
