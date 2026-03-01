"""
Configurações da aplicação via dynaconf.
O ambiente é controlado pela variável ENV_FOR_DYNACONF.
"""

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="USERAPI",          # Variáveis de ambiente com prefixo USERAPI_
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,                 # Ativa suporte a ambientes ([development], [production] etc.)
    load_dotenv=True,                  # Carrega o .env automaticamente
    dotenv_path=".env",
    env_switcher="ENV_FOR_USERAPI",    # Variável que controla o ambiente ativo
    merge_enabled=True,                # Faz merge entre default e o ambiente ativo
)
