from flask_restx import Resource
from flask import request
from src.server.app import api
from src.utils.xhs.sign import sign
from src.utils.xhs.core import XhsClient
from src.utils.xhs.utils import beauty_print
import re
from src.utils.rsa import decrypt_with_private_key
from loguru import logger

xiaohongshu_ns = api.namespace("xiaohongshu", description="Xiaohongshu operations")


def extract_topics(input_string):
    # 定义正则表达式模式
    pattern = r"#(\w+)\[话题\]#"

    # 使用正则表达式查找匹配的话题
    topics = re.findall(pattern, input_string)

    return topics


@xiaohongshu_ns.route("/post")
class XiaohongshuPost(Resource):
    @xiaohongshu_ns.doc("xiaohongshu_post")
    @xiaohongshu_ns.vendor(
        {
            "x-monkey-tool-name": "xiaohongshu",
            "x-monkey-tool-categories": ["auto"],
            "x-monkey-tool-display-name": "小红书",
            "x-monkey-tool-description": "自动发布小红书帖子",
            "x-monkey-tool-icon": "https://static.infmonkeys.com/logo/tools/xiaohongshu/logo.png",
            "x-monkey-tool-extra": {
                "estimateTime": 30,
            },
            "x-monkey-tool-input": [
                {
                    "displayName": "帖子类型",
                    "name": "note_type",
                    "type": "options",
                    "default": "image",
                    "required": True,
                    "options": [
                        {"name": "图文", "value": "image"},
                        {"name": "视频", "value": "video"},
                    ],
                },
                {
                    "displayName": "标题",
                    "name": "title",
                    "type": "string",
                    "default": "",
                    "required": True,
                    "description": "标题中的话题请使用 #xxx[话题]# 格式来添加话题，例如：#美食[话题]# #旅行[话题]#"
                },
                {
                    "displayName": "描述信息",
                    "name": "desc",
                    "type": "string",
                    "default": "",
                    "required": True,
                },
                {
                    "displayName": "图片列表",
                    "name": "images",
                    "type": "file",
                    "default": None,
                    "required": True,
                    "displayOptions": {"show": {"note_type": ["image"]}},
                    "typeOptions": {
                        "multipleValues": True,
                        "accept": ".png,.jpg,.jpeg",
                    },
                },
                {
                    "displayName": "视频封面",
                    "name": "video_cover_url",
                    "type": "string",
                    "default": None,
                    "required": False,
                    "displayOptions": {"show": {"note_type": ["video"]}},
                },
                {
                    "displayName": "视频链接",
                    "name": "video_url",
                    "type": "string",
                    "default": None,
                    "required": True,
                    "displayOptions": {"show": {"note_type": ["video"]}},
                },
                {
                    "displayName": "设置定时发布时间",
                    "description": "时间格式：2023-07-25 23:59:59",
                    "name": "post_time",
                    "type": "string",
                    "default": None,
                    "required": False,
                },
                {
                    "displayName": "@用户信息",
                    "name": "ats",
                    "type": "string",
                    "default": [],
                    "required": False,
                    "typeOptions": {"multipleValues": True},
                },
                {
                    "displayName": "是否私密发布",
                    "name": "is_private",
                    "type": "boolean",
                    "default": False,
                    "required": True,
                },
            ],
            "x-monkey-tool-credentials": [{"name": "xiaohongshu", "required": True}],
            "x-monkey-tool-output": [
                {
                    "name": "id",
                    "displayName": "小红书帖子 id",
                    "type": "string",
                },
                {
                    "name": "score",
                    "displayName": "分数",
                    "type": "number",
                },
                {
                    "name": "link",
                    "displayName": "链接",
                    "type": "string",
                },
            ],
        }
    )
    def post(self):
        input_data = request.json
        credential = input_data.get("credential", {})
        credential_encrypted_data = credential.get("encryptedData")
        if not credential_encrypted_data:
            return {"message": "Invalid credential"}, 400
        credential_data = decrypt_with_private_key(credential_encrypted_data)

        cookie = credential_data.get("cookie")
        logger.info(f"Got xiaohongshu cookie: {cookie}")
        is_private = input_data.get("is_private", False)
        note_type = input_data.get("note_type", "image")
        ats = input_data.get("ats", [])
        video_url = input_data.get("video_url", None)
        video_cover_url = input_data.get("video_cover_url", None)
        images = input_data.get("images", [])
        if isinstance(images, str):
            images = [images]
        title = input_data.get("title")
        post_time = input_data.get("post_time")
        desc = input_data.get("desc")

        logger.info(
            f"Start to post xiaohongshu note, note_type: {note_type}, title: {title}, desc: {desc}, images: {images}, video_url: {video_url}, video_cover_url: {video_cover_url}, post_time: {post_time}, ats: {ats}, is_private: {is_private}"
        )

        topics = []
        if title:
            topics += extract_topics(title)
        if desc:
            topics += extract_topics(desc)
        topics = list(set(topics))
        logger.info(
            f"Extracted topics: {topics}",
        )

        xhs_client = XhsClient(cookie, sign=sign)
        result = None
        if note_type == "image":
            result = xhs_client.create_image_note(
                title=title,
                desc=desc,
                files=images,
                is_private=is_private,
                topics=topics,
                post_time=post_time,
                ats=ats,
            )
        elif note_type == "video":
            result = xhs_client.create_video_note(
                title=title,
                desc=desc,
                video_path=video_url,
                is_private=is_private,
                topics=topics,
                post_time=post_time,
                ats=ats,
                cover_path=video_cover_url,
            )
        beauty_print(result)
        id, score = result["id"], result["score"]
        link = f"https://www.xiaohongshu.com/explore/{id}"
        return {"id": id, "score": score, "link": link}
