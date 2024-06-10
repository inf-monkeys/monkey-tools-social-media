import json
import uuid
from pathlib import Path
from instagrapi import Client

from src.utils.rsa import decrypt_with_private_key
from .app import api
from flask_restx import Resource
from flask import request

from loguru import logger
from src.utils import download_image, base64_to_bytes, get_and_ensure_exists_tmp_files_folder, save_bytes_to_image
from src.config import config_data

instagram_ns = api.namespace('instagram', description='Instagram')

proxy_config = config_data.get('proxy')


@instagram_ns.route('/post')
class InstagramPost(Resource):
    @instagram_ns.doc('instagram_post')
    @instagram_ns.vendor({
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

        credential = input_data.get("credential", {})
        credential_encrypted_data = credential.get("encryptedData")
        if not credential_encrypted_data:
            return {"message": "Invalid credential"}, 400
        credential_data = decrypt_with_private_key(credential_encrypted_data)
    
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

