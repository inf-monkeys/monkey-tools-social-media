import logging
from flask import Flask, request
from flask_restx import Api
from src.config import public_key

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Monkey Tools Social Medis API",
    description="Monkey Tools Social Medis API",
)


@api.errorhandler(Exception)
def handle_exception(error):
    return {"message": str(error)}, 500

@app.before_request
def before_request():
    request.app_id = request.headers.get("x-monkeys-appid")
    request.user_id = request.headers.get("x-monkeys-userid")
    request.team_id = request.headers.get("x-monkeys-teamid")
    request.workflow_instance_id = request.headers.get("x-monkeys-workflow-instanceid")


@app.get("/manifest.json")
def get_manifest():
    return {
        "schema_version": "v1",
        "namespace": "social_media",
        "display_name": "社交应用",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": "/swagger.json"},
        "contact_email": "dev@inf-monkeys.com",
        "rsaPublicKey": public_key,
        "credentials": [
            {
                "name": "xiaohongshu",
                "type": "AKSK",
                "displayName": "小红书",
                "iconUrl": "https://static.infmonkeys.com/logo/tools/xiaohongshu/logo.png",
                "properties": [
                    {
                        "displayName": "请前往[小红书创作服务平台](https://creator.xiaohongshu.com/) 网页获取 cookie，注意请不要退出登录，否则此 cookie 将会失效。[点击查看使用文档](https://inf-monkeys.github.io/docs/zh-cn/tools/others/get-xiaohongshu-cookie)。",
                        "type": "notice",
                        "name": "docs",
                    },
                    {
                        "displayName": "Cookie",
                        "name": "cookie",
                        "type": "string",
                        "required": True,
                    },
                ],
            },
            {
                "type": "AKSK",
                "name": "instagram",
                "displayName": "Instagram",
                "iconUrl": "https://img1.baidu.com/it/u=1083347651,3149271153&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500",
                "properties": [
                    {
                        "displayName": "用户名",
                        "name": "username",
                        "type": "string",
                        "required": True,
                    },
                    {
                        "displayName": "密码",
                        "name": "password",
                        "type": "string",
                        "required": True,
                    },
                ],
            },
        ],
    }


class NoSuccessfulRequestLoggingFilter(logging.Filter):
    def filter(self, record):
        return "GET /" not in record.getMessage()


# 获取 Flask 的默认日志记录器
log = logging.getLogger("werkzeug")
# 创建并添加过滤器
log.addFilter(NoSuccessfulRequestLoggingFilter())

