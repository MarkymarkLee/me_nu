import json
import time
from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
)

import logging

from database import db, Userdata, UserPreference, UserState

from init_setup import link_rich_menu_to_user
from get_messages import get_finish_user_setting_message, question_message, get_menu_request_message

from get_questions import get_question
from openai_process import process_user_init_answer
from openai_process import gen_recommendation
from openai_process import gen_init_questions_immediate_response
from openai_process import gen_chat


def handle_text_events(event: MessageEvent, user_data: Userdata, message_api: MessagingApi, logger: logging.Logger):
    """
    Function to handle text events
    """
    if user_data.userState == UserState.INIT:
        if event.message.text == "初始設定":
            welcome_text = """歡迎進入初始設定！請回答 10 個簡單的問題，我們將根據你的回答來提供個人化的餐點推薦。
你可以直接點選快速回覆，也可以用鍵盤詳細輸入偏好原因喔（回覆的理由寫得越詳細我們將來提供的服務會越準確）"""
            message_api.reply_message(
                reply_message_request=ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=welcome_text),
                              question_message(get_question(0))])
            )
            user_data.userState = UserState.INIT_QA
            user_data.user_init_qa_count += 1
            db.update_user_data(user_data)
        else:
            message_api.reply_message(
                reply_message_request=ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="請點選「初次設定」來開始旅程")])
            )
    elif user_data.userState == UserState.INIT_QA:

        old_question = get_question(
            user_data.user_init_qa_count - 1)["question"]
        user_answer = event.message.text
        new_question = get_question(user_data.user_init_qa_count)

        if user_data.user_init_qa_count >= 10:
            link_rich_menu_to_user(message_api, "main_menu", user_data.userId)

        if user_data.user_init_qa_count >= 10:
            user_data.userState = UserState.INIT_DONE
            message_api.reply_message(
                reply_message_request=ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=gen_init_questions_immediate_response(
                        old_question, user_answer)), get_finish_user_setting_message()])
            )
        else:
            message_api.reply_message(
                reply_message_request=ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=gen_init_questions_immediate_response(
                        old_question, user_answer)), question_message(new_question)])
            )

        user_data.user_init_qa_count += 1
        db.update_user_data(user_data)

        new_preference = process_user_init_answer(
            question=old_question, user_answer=user_answer)

        db.update_user_preferences(user_data.userId, new_preference)

    elif user_data.userState == UserState.INIT_DONE or user_data.userState == UserState.MAIN_AUTO_CHAT:
        user_message = event.message.text
        if user_message == "開始使用":
            user_data.userState = UserState.MAIN_MENU_REQUEST
            user_data.chat = []
            db.update_user_data(user_data)
            message_api.reply_message(
                reply_message_request=ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[get_menu_request_message()])
            )
        else:
            # continue auto chat
            user_data.chat.append(user_message)
            response = gen_chat(user_data)
            message_api.reply_message(
                reply_message_request=ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response)])
            )
            user_data.chat.append(response)
            user_data.last_chat_time = time.time()
            db.update_user_data(user_data)

    elif user_data.userState == UserState.MAIN_NEED_REQUEST:
        user_todays_request = event.message.text
        user_data.chat.append(user_todays_request)
        menu_info = user_data.menu_data
        review_info = user_data.review_data

        # gen recommendation
        response = gen_recommendation(
            user_data, user_todays_request, menu_info, review_info)
        user_data.chat.append(response)

        message_api.reply_message(
            reply_message_request=ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response)])
        )
        user_data.userState = UserState.MAIN_AUTO_CHAT
        db.update_user_data(user_data)

    elif user_data.userState == UserState.MAIN_MENU_REQUEST:
        message_api.reply_message(
            reply_message_request=ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="我要看菜單的圖片啦！")]
            )
        )

    else:
        message_api.reply_message(
            reply_message_request=ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="very bad")]
            )
        )
