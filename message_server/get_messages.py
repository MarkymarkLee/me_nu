import json
from linebot.v3.messaging import (
    TextMessage,
    FlexMessage,
    FlexContainer,
)
from get_questions import get_question


def question_message(qa):
    """
    Function to ask a question to the user
    """

    if qa is None:
        return TextMessage(text="設定完成")

    with open("assets/qa_message_template.json", "r", encoding='utf-8') as f:
        flex_message_dict = json.load(f)
        flex_message_dict["body"]["contents"][0]["text"] = qa['question']
        flex_message_dict["footer"]["contents"][0]["action"]["text"] = qa["answer0"]
        flex_message_dict["footer"]["contents"][0]["action"]["label"] = qa["answer0"]
        flex_message_dict["footer"]["contents"][1]["action"]["text"] = qa["answer1"]
        flex_message_dict["footer"]["contents"][1]["action"]["label"] = qa["answer1"]
        flex_message_dict['hero']['url'] += qa['image_path']

    return FlexMessage(
        alt_text="問題", contents=FlexContainer.from_dict(flex_message_dict))


def get_menu_request_message():
    with open("assets/menu_request_message.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    return FlexMessage(
        alt_text="問題", contents=FlexContainer.from_dict(data))


def get_finish_user_setting_message():
    with open("assets/finish_user_setting.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    return FlexMessage(
        alt_text="問題", contents=FlexContainer.from_dict(data))


def get_greeting_message(username: str):
    with open("assets/greeting_message.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    message: str = data["body"]["contents"][0]["text"]
    data["body"]["contents"][0]["text"] = message.replace(
        "__username__", username)

    return FlexMessage(
        alt_text="問題", contents=FlexContainer.from_dict(data))


if __name__ == "__main__":
    print(get_greeting_message("John"))
