from database import db, Userdata
from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
)
import logging
from get_messages import get_greeting_message


def link_rich_menu_to_user(message_api: MessagingApi, rich_menu_alias_id: str, user_id: str):
    """
    Function to link a rich menu to a user
    """
    intro_menu_resp = message_api.get_rich_menu_alias(
        rich_menu_alias_id=rich_menu_alias_id
    )
    intro_menu_id = intro_menu_resp.rich_menu_id
    message_api.link_rich_menu_id_to_user(
        user_id, intro_menu_id)


def initial_setup(user_data: Userdata, message_api: MessagingApi, replyToken: str, logger: logging.Logger) -> Userdata:
    """
    Function to set up a new user in the database
    and set up the initial preferences
    """
    logger.info("Setting up user data")
    db.set_user_data(user_data)
    message_api.reply_message(
        reply_message_request=ReplyMessageRequest(
            reply_token=replyToken,
            messages=[get_greeting_message(user_data.displayName)]
        )
    )
