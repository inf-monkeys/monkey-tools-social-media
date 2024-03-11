import json
import uuid
from pathlib import Path

from instagrapi import Client

from .app import api, app
from flask_restx import Resource
from flask import request

from ..logger import logger
from ..utils import download_image, base64_to_bytes, get_and_ensure_exists_tmp_files_folder, save_bytes_to_image
from ..config import config_data
from ..utils.xhs.utils import beauty_print

social_media_ns = api.namespace('social-media', description='Social Media operations')

proxy_config = config_data.get('proxy')


@social_media_ns.route('/instagram-post')
class InstagramPost(Resource):
    @social_media_ns.doc('instagram')
    @social_media_ns.vendor({
        "x-monkey-tool-name": "instagram",
        "x-monkey-tool-categories": ["auto"],
        "x-monkey-tool-display-name": "Instagram",
        "x-monkey-tool-description": "自动发布 Instagram 帖子",
        "x-monkey-tool-icon": "emoji:🤖️:#7fa3f8",
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
                    {
                        "name": "图文",
                        "value": "image"
                    },
                    {
                        "name": "视频",
                        "value": "video"
                    }
                ]
            },
            {
                "displayName": "标题",
                "name": "title",
                "type": "string",
                "default": "",
                "required": True,
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
                "type": "string",
                "default": None,
                "required": True,
                "displayOptions": {
                    "show": {
                        "note_type": [
                            "image"
                        ]
                    }
                },
                "typeOptions": {
                    "multipleValues": True
                }
            },
            {
                "displayName": "视频封面",
                "name": "video_cover_url",
                "type": "string",
                "default": None,
                "required": False,
                "displayOptions": {
                    "show": {
                        "note_type": [
                            "video"
                        ]
                    }
                }
            },
            {
                "displayName": "视频链接",
                "name": "video_url",
                "type": "string",
                "default": None,
                "required": True,
                "displayOptions": {
                    "show": {
                        "note_type": [
                            "video"
                        ]
                    }
                }
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
                "typeOptions": {
                    "multipleValues": True
                }
            },
            {
                "displayName": "话题信息",
                "name": "topics",
                "type": "string",
                "default": [],
                "required": False,
                "typeOptions": {
                    "multipleValues": True
                }
            },
            {
                "displayName": "是否私密发布",
                "name": "is_private",
                "type": "boolean",
                "default": False,
                "required": True,
            },
        ],
        "x-monkey-tool-credentials": [
            {
                "name": "instagram",
                "required": True
            }
        ]
    })
    def post(self):
        input_data = request.json

        # TODO
        credential_data = {}
        if credential_data is None:
            raise Exception("请先配置 Instagram 账号")

        username = credential_data.get('username')
        password = credential_data.get('password')

        if proxy_config.get('enabled'):
            print(f"使用代理 {proxy_config.get('url')} 访问 Instagram")

        cl = Client(
            proxy=proxy_config.get('url'),
            logger=logger
        )
        login_success = cl.login(username, password)
        if not login_success:
            raise Exception("登录 Instagram 失败")

        image_type = input_data.get('image_type')
        image_url = input_data.get("image_url")
        image_base64 = input_data.get('image_base64')

        image_buffer = None
        extension = ''
        if image_type == 'url':
            image_buffer = download_image(
                url=image_url
            )
            try:
                extension = image_url.split('/')[-1].split('.')[-1]
            except Exception as e:
                logger.warn(f"图像链接 {image_url} 无法获取后缀，使用 jpg 作为 fallback")
                extension = 'jpg'
        elif image_type == 'base64':
            extension = image_base64.split(';')[0].split('/')[1]
            if extension not in ['jpg', 'jpeg']:
                raise Exception("传入的 base64 图片不是 jpg 或者 jpeg 格式")
            image_buffer = base64_to_bytes(
                base64_string=image_base64
            )
        base_folder = get_and_ensure_exists_tmp_files_folder()
        file_path = Path(base_folder, f"{uuid.uuid4()}.{extension}")
        logger.info(f"保存图片到本地临时文件：{file_path}")
        save_bytes_to_image(
            bytes_data=image_buffer,
            file_path=file_path
        )
        caption = input_data.get("caption")
        custom_accessibility_caption = input_data.get("custom_accessibility_caption", None)
        like_and_view_counts_disabled = input_data.get("like_and_view_counts_disabled", False)
        disable_comments = input_data.get("disable_comments", False)

        try:
            media = cl.photo_upload(
                file_path,
                caption,
                extra_data={
                    "custom_accessibility_caption": custom_accessibility_caption,
                    "like_and_view_counts_disabled": 1 if like_and_view_counts_disabled else 0,
                    "disable_comments": 1 if disable_comments else 0,
                }
            )

            logger.info(f"上传图片成功：{media}")
            result_str = media.json()
            return json.loads(result_str)
        except Exception as e:
            err_msg = f"发布失败：{str(e)}"
            if 'Request processing failed' in err_msg:
                err_msg += "请检查图片是否为 jpg 或者 jpeg 格式（注意不能直接修改文件后缀，需要进行实际转换）"
            raise Exception(err_msg)


@social_media_ns.route('/xiaohongshu-post')
class InstagramPost(Resource):
    @social_media_ns.doc('xiaohongshu')
    @social_media_ns.vendor({
        "x-monkey-tool-name": "xiaohongshu",
        "x-monkey-tool-categories": ["auto"],
        "x-monkey-tool-display-name": "小红书",
        "x-monkey-tool-description": "自动发布小红书帖子",
        "x-monkey-tool-icon": "emoji:🤖️:#7fa3f8",
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
                    {
                        "name": "图文",
                        "value": "image"
                    },
                    {
                        "name": "视频",
                        "value": "video"
                    }
                ]
            },
            {
                "displayName": "标题",
                "name": "title",
                "type": "string",
                "default": "",
                "required": True,
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
                "displayOptions": {
                    "show": {
                        "note_type": [
                            "image"
                        ]
                    }
                },
                "typeOptions": {
                    "multipleValues": True,
                    "accept": ".png,.jpg,.jpeg"
                }
            },
            {
                "displayName": "视频封面",
                "name": "video_cover_url",
                "type": "string",
                "default": None,
                "required": False,
                "displayOptions": {
                    "show": {
                        "note_type": [
                            "video"
                        ]
                    }
                }
            },
            {
                "displayName": "视频链接",
                "name": "video_url",
                "type": "string",
                "default": None,
                "required": True,
                "displayOptions": {
                    "show": {
                        "note_type": [
                            "video"
                        ]
                    }
                }
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
                "typeOptions": {
                    "multipleValues": True
                }
            },
            {
                "displayName": "是否私密发布",
                "name": "is_private",
                "type": "boolean",
                "default": False,
                "required": True,
            },
        ],
        "x-monkey-tool-credentials": [
            {
                "name": "xiaohongshu",
                "required": True
            }
        ],
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
    })
    def post(self):
        input_data = request.json
        print(input_data)
        credential_data = {}
        cookie = credential_data.get('cookie')
        is_private = input_data.get("is_private", False)
        note_type = input_data.get("note_type", "image")
        ats = input_data.get("ats", [])
        video_url = input_data.get("video_url", None)
        video_cover_url = input_data.get('video_cover_url', None)
        images = input_data.get("images", [])
        if isinstance(images, str):
            images = [images]
        title = input_data.get('title')
        post_time = input_data.get('post_time')
        desc = input_data.get('desc')

        topics = []
        if title:
            topics += self.extract_topics(title)
        if desc:
            topics += self.extract_topics(desc)
        topics = list(set(topics))
        print("topics: ", topics)

        xhs_client = XhsClient(cookie, sign=sign)
        result = None
        if note_type == 'image':
            result = xhs_client.create_image_note(
                title=title,
                desc=desc,
                files=images,
                is_private=is_private,
                topics=topics,
                post_time=post_time,
                ats=ats
            )
        elif note_type == 'video':
            result = xhs_client.create_video_note(
                title=title,
                desc=desc,
                video_path=video_url,
                is_private=is_private,
                topics=topics,
                post_time=post_time,
                ats=ats,
                cover_path=video_cover_url
            )
        beauty_print(result)
        id, score = result['id'], result['score']
        link = f"https://www.xiaohongshu.com/explore/{id}"
        return {
            "id": id,
            "score": score,
            "link": link
        }
