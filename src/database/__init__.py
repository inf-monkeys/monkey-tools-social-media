from peewee import *
from src.config import config_data

database_url = config_data.get('database', {}).get('url', {})

# 连接到 PostgreSQL 数据库
db = PostgresqlDatabase(database_url)

# 定义基础模型类
class BaseModel(Model):
    id = BigAutoField()
    class Meta:
        database = db

# 定义工具凭证实体类
class ToolsCredentialEntity(BaseModel):
    credential_id = CharField()
    team_id = CharField()
    creator_user_id = CharField()

    display_name = CharField()
    type = CharField()
    data = TextField()

    class Meta:
        table_name = 'monkey_tools_social_media_credentials'

# 创建表
db.connect()
db.create_tables([ToolsCredentialEntity])
