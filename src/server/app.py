from flask import Flask, request
from flask_restx import Api
import traceback

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Monkey Tools Social Medis API",
    description="Monkey Tools Social Medis API",
)


@api.errorhandler(Exception)
# Register an error handler for all exceptions
def handle_exception(error):
    traceback.print_exc()
    return {'message': str(error)}, 500


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
        "namespace": "monkey_tools_social_media",
        "display_name": "社交应用",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": "/swagger.json"},
        "contact_email": "dev@inf-monkeys.com",
        "credentialEndpoints": [
            {"type": "create", "url": "/credentials", "method": "POST"},
            {"type": "update", "url": r"/credentials/{credentialId}", "method": "POST"},
            {
                "type": "delete",
                "url": r"/credentials/{credentialId}",
                "method": "DELETE",
            },
            {"type": "test", "url": "/credentials/test", "method": "DELETE"},
        ],
        "credentials": [
            {
                "name": "xiaohongshu",
                "type": "AKSK",
                "displayName": "小红书",
                "iconUrl": "https://static.aside.fun/upload/frame/img_v2_99283942-6e81-4051-a45c-6c7b1e0f19eg.jpg",
                "properties": [
                    {
                        "displayName": "请前往[小红书创作服务平台](https://creator.xiaohongshu.com/) 网页获取 cookie，注意请不要退出登录，否则此 cookie 将会失效。[点击查看使用文档](https://inf-monkeys.feishu.cn/docx/Lfi6dtZHRo6mNNxfZWTc57UBnUh)。",
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
