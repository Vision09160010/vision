import os.path
from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
PATH = os.path.dirname(os.path.abspath(__file__))
# __file__:当前路径
# os.path.abspath:当前文件绝对路径
# dirname: 拿上级路径

class Settings(BaseSettings):
    api_key : str
    model_name:str
    base_url:str
    host:str
    port:int
    user:str
    password:str
    database:str
    es_user:str
    es_password:str
    es_host:List[str]

    milvus_uri:str
    milvus_user:str
    milvus_password:str

    redis_host:str
    redis_port:int
    redis_password:str

    faq_path:str


    model_config = ConfigDict(  # 映射配置文件的配置
        extra = "allow",
        env_file = f'{PATH}/.env',
        case_sensitive = False,
    )
    @ property
    def url(self):
        mysql_url = f"mysql+pymysql://{settings.user}:{settings.password}@{settings.host}:{settings.port}/{settings.database}"
        return mysql_url

settings = Settings()
if __name__ == '__main__':
    print(settings.model_name)
    print(settings.url)
    print(PATH)
    print(settings.url)