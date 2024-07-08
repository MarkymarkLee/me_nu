from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ApiClient,
    MessagingApiBlob
)
from linebot.v3.webhooks import (
    Event,
    MessageEvent,
    FollowEvent,
    UnfollowEvent
)
from typing import List
import logging

from database import UserState, db, Userdata
from init_setup import initial_setup
from handle_text_events import handle_text_events

from get_reviews import get_reviews_from_lat_long
from get_menu import get_menu_and_review_from_qr, get_menu_from_title
from image_processing import process_qr_code_image


def handle_events(events: List[Event], api_client: ApiClient, logger: logging.Logger):
    logger.info("Handling events")
    message_api = MessagingApi(api_client)
    messaging_api_blob = MessagingApiBlob(api_client)
    for event in events:

        if isinstance(event, UnfollowEvent):
            userid = event.source.user_id
            db.delete_user_data(userid)
            message_api.unlink_rich_menu_id_from_user(userid)

        if not isinstance(event, MessageEvent) and not isinstance(event, FollowEvent):
            continue

        logger.info("getting user data")
        userid = event.source.user_id
        user_data = db.get_user_data(userid)

        # set up user data
        if isinstance(event, FollowEvent):
            replyToken = event.reply_token
            user_profile = message_api.get_profile_with_http_info(userid).data
            user_pic_url = user_profile.picture_url
            user_name = user_profile.display_name
            user_data = Userdata(
                userId=userid, pictureUrl=user_pic_url, displayName=user_name)
            initial_setup(user_data, message_api, replyToken, logger)
            return

        logger.info(f"User data: {user_data.to_dict()}")

        if event.message.type == "image" and user_data.userState == UserState.MAIN_MENU_REQUEST:
            image_id = event.message.id
            image_response = messaging_api_blob.get_message_content_with_http_info(
                image_id)
            image_content = image_response.data
            qr_result = process_qr_code_image(image_content)
            if qr_result is None:
                logger.info("QR code not found")
                message_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="抱歉，我們無法辨識這張圖片的 QR code，請再試一次")])
                )
                return

            logger.info(f"QR result: {qr_result}")

            menu, review = get_menu_and_review_from_qr(qr_result)
            if menu is None:
                message_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="抱歉，我們沒有這家店的資料，請再試一次")])
                )
                return
            user_data.review_data = review
            user_data.menu_data = menu
            user_data.userState = UserState.MAIN_NEED_REQUEST
            db.update_user_data(user_data)
            message_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="那你今天有想吃什麼東西嗎？🍔🍣🍜\n或是有什麼特殊需求嗎？沒有也別擔心，我是最懂你的😉")]
                )
            )

        elif event.message.type == "location" and user_data.userState == UserState.MAIN_MENU_REQUEST:
            lat = event.message.latitude
            lon = event.message.longitude
            address = event.message.address
            title = event.message.title
            review = get_reviews_from_lat_long((lat, lon), title, address)
            menu = get_menu_from_title(title)
            if menu is None:
                message_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="抱歉，我們沒有這家店的資料，請再試一次")])
                )
                return
            user_data.review_data = review
            user_data.menu_data = menu
            user_data.userState = UserState.MAIN_NEED_REQUEST
            db.update_user_data(user_data)
            message_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="那你今天有想吃什麼東西嗎？🍔🍣🍜\n或是有什麼特殊需求嗎？沒有也別擔心，我是最懂你的😉")]
                )
            )

        elif event.message.type == "text":
            handle_text_events(event, user_data, message_api, logger)
        else:
            message_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="不要亂傳東西給我😉")]
                )
            )
