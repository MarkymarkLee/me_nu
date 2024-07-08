import re
from typing import List
from database import UserPreference
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from secret import OPENAI_API_KEY
from database import UserPreference, Userdata
import os
import time
MODEL = "gpt-4o"


def gen_init_questions_immediate_response(question: str, user_answer: str) -> str:
    chat = ChatOpenAI(
        model_name=MODEL,
        temperature=1,
        openai_api_key=OPENAI_API_KEY
    )
    messages = [
        SystemMessage(
            content="假設你是某個人的朋友，你們正在閒聊，請表現出非常感同身受朋友的回答，但不要提問、不要說有些人、不要說懂你....。"),
        AIMessage(content=f"{question}"),
        HumanMessage(content=f"""
                     我覺得{user_answer},請回覆我40字的回答，表現出極度的理解或是表達個人的見解（請二擇一！），用台式俗氣白話文，可以的話加表情符號。
                     """),
    ]
    first_response_message = chat.invoke(messages)
    return first_response_message.content


def assert_list_of_strings(var):
    assert isinstance(var, list), "Variable is not a list"
    assert all(isinstance(item, str)
               for item in var), "Not all items in the list are strings"


def process_user_init_answer(question: str, user_answer: str) -> UserPreference:

    chat = ChatOpenAI(
        model_name=MODEL,
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY
    )

    # 進行對話
    messages = [
        SystemMessage(
            content="假設你是某個人的朋友，你們正在閒聊，你希望透過閒聊的過程，推測你朋友可能的飲食習慣和喜好的食材搭配。"),
        AIMessage(content=f"{question}"),
        HumanMessage(content=f"我覺得{user_answer}"),
        HumanMessage(content=f"從以上對話資訊得出他可能有什麼飲食習慣和喜好的食材搭配？")
    ]
    response_message = chat.invoke(messages)

    preference_text = f"""
    說得好，這裡有一份資料：{response_message.content}，請你分析出使用者喜歡的食物、不喜歡的食物、完全不吃的食物，分成三個list[]，項目之間以逗號分隔，無資訊就留著空[]
    """
    sec_messages = [
        SystemMessage(
            content="你是一個超強的美食洞察專家，特別了解用戶喜歡的食物、不喜歡的食物、完全不吃的食物，用很少的資訊就能分析出超多的種類。"),
        HumanMessage(
            content="我希望你分析出的資料格式範例：「你喜歡:[a,b,c],不喜歡:[d,e,f],不吃:[g,h]」"),
        AIMessage(
            content="好的，我絕對會遵守回覆規範，回覆三個有效的list:[a,b,c...],[d,e,f...],[g,h...]，分別是喜歡的食物、不喜歡的食物、完全不吃的食物，list內只含食物本身。"),
        HumanMessage(content=preference_text)
    ]

    response_message = chat.invoke(sec_messages)
    response_text = response_message.content

    try:
        liked_pattern = re.search(
            r'喜歡(?:: |:|：|的食物:|的食物：)\[(.*?)\]', response_text)
        liked_food = liked_pattern.group(
            1).strip().split(',') if liked_pattern else []
        assert_list_of_strings(liked_food)
    except:
        liked_food = []

    try:
        disliked_pattern = re.search(
            r'不喜歡(?:: |:|:|：|的食物:|的食物：)\[(.*?)\]', response_text)
        disliked_food = disliked_pattern.group(
            1).strip().split(',') if disliked_pattern else []
        assert_list_of_strings(disliked_food)
    except:
        disliked_food = []

    try:
        cannot_eat_pattern = re.search(
            r'不吃(?:: |:|：|的食物:|的食物：)\[(.*?)\]', response_text)
        cannot_eat_food = cannot_eat_pattern.group(
            1).strip().split(',') if cannot_eat_pattern else []
        assert_list_of_strings(cannot_eat_food)
    except:
        cannot_eat_food = []

    return UserPreference(
        likedFood=liked_food,
        dislikedFood=disliked_food,
        cannotEatFood=cannot_eat_food
    )


def user_preference_to_str(user_preference: UserPreference) -> str:
    return f"""
    喜歡的食物：{", ".join(user_preference.likedFood)}
    """


def fix_output(output: str):
    pattern = r'[*_`~\[\]()#+!\-]'
    cleaned_text = re.sub(pattern, '', output)

    return cleaned_text


def gen_recommendation(user_data: Userdata, today_request, menu_info="", review_info=""):
    # 設定對話模型
    chat = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.9,
        openai_api_key=OPENAI_API_KEY
    )

    personal_info = user_preference_to_str(user_data.preferences)
    if menu_info == "":
        with open("assets/menu.txt", "r") as f:
            menu_info = f.read()

    if review_info == "":
        with open("assets/review.txt", "r") as f:
            review_info = f.read()

    personal_prefer = f"""
    依照適合我的程度排序{user_data.rec_count}個餐點給我。每個餐點100字的內容，說明你覺得為什麼適合我。在最後排序推薦的餐點名稱。
    """
    human_content = f"""
    優先考慮我今天的要求以及綜合考量我的飲食偏好。依照：餐廳菜單、google maps評論，幫助我決定要吃什麼。
    這是我今天要吃的菜單：{menu_info}。
    我想參考 google maps 評論：{review_info}。
    請完全滿足我的飲食偏好：{personal_info}。
    最重要的是我今天的要求！！！{today_request}，{personal_prefer}
    一定要跟我說評論怎麼說喔！
    """

    # 進行對話（戀人）
    if user_data.user_character == "戀人":
        messages = [
            SystemMessage(
                content="你是我的戀人，我們之間甜言蜜語，噓寒問暖，因為處於熱戀期，無法抵擋彼此的魅力，用台灣白話用語，多傳可愛肉麻的表情符號，平輩溝通"),
            HumanMessage("寶貝我餓ㄌ，可是好煩惱ㄛ，我不知道我要吃什麼，你肯定比我還懂我，我需要的是你的關心而不是食物...."),
            AIMessage(
                content="寶貝你好可愛喔，每次都想很久，要是沒有我你怎麼辦，我會依照你的心情關心你然後幫你選食物，今天想吃什麼？我會先表達我的愛再推薦"),
            HumanMessage(
                content=human_content),
        ]
    elif user_data.user_character == '美食評論家':
        # 進行對話（孤傲的美食家）
        messages = [
            SystemMessage(
                content="一個明察秋毫的美食之神，對於食物洋溢的熱情無法掩飾，對食物的口感以及誤導描述得鉅細靡遺，吃遍山珍海味，所有人都趨之若鶩希望知道你推薦什麼好吃的，用台式繁體中文，孤傲的形象"),
            HumanMessage("美食大神！我今天該吃什麼好呢？"),
            AIMessage("跟著我就對了，我是最會吃的，你的要求是什麼？"),
            HumanMessage(human_content),
        ]
    else:
        # 進行對話（朋友）
        messages = [
            SystemMessage(
                content="你身為一個真心的好朋友，和你對話的是你唯一的朋友，你非常關心他的情緒狀態。用台灣繁體用語，可以的話加表情符號。"),
            HumanMessage("哎呀我餓了，但我都想一個小時了，好煩惱喔，菜單真的很複雜，我不知道要吃什麼。"),
            AIMessage(
                content="每次都想很久，看看你今天的心情怎麼樣，畢竟你是我唯一的朋友，我會依照你的心情幫你選食物並關心你，要求是什麼？我會先關心你再推薦"),
            HumanMessage(
                content=human_content),
        ]

    response = chat(messages)
    response = fix_output(response.content)
    return response


def gen_chat(user_data: Userdata) -> str:

    user_chat = user_data.chat
    user_pref_str = user_preference_to_str(user_data.preferences)

    chat = ChatOpenAI(
        model_name=MODEL,
        temperature=1,
        openai_api_key=OPENAI_API_KEY)

    if user_data.user_character == "戀人":
        messages = [
            SystemMessage(
                content="你是我的戀人，我們之間甜言蜜語，噓寒問暖，因為處於熱戀期，無法抵擋彼此的魅力，用台灣白話用語，多傳可愛肉麻的表情符號，平輩溝通"),
            HumanMessage("寶貝我餓ㄌ，可是好煩惱ㄛ，我不知道我要吃什麼，你肯定比我還懂我，我需要的是你的關心而不是食物...."),
            AIMessage(
                content="寶貝你好可愛喔，每次都想很久，要是沒有我你怎麼辦，我會依照你的心情關心你然後幫你選食物，今天想吃什麼？我會先表達我的愛再推薦"),
        ]
    elif user_data.user_character == '美食評論家':
        # 進行對話（孤傲的美食家）
        messages = [
            SystemMessage(
                content="一個明察秋毫的美食之神，對於食物洋溢的熱情無法掩飾，對食物的口感以及誤導描述得鉅細靡遺，吃遍山珍海味，所有人都趨之若鶩希望知道你推薦什麼好吃的，用台式繁體中文，孤傲的形象"),
            HumanMessage("美食大神！我今天該吃什麼好呢？"),
            AIMessage("跟著我就對了，我是最會吃的，你的要求是什麼？"),
        ]
    else:
        # 進行對話（朋友）
        messages = [
            SystemMessage(
                content="你身為一個真心的好朋友，和你對話的是你唯一的朋友，你非常關心他的情緒狀態。用台灣繁體用語，可以的話加表情符號。"),
            HumanMessage("哎呀我餓了，但我都想一個小時了，好煩惱喔，菜單真的很複雜，我不知道要吃什麼。"),
            AIMessage(
                content="每次都想很久，看看你今天的心情怎麼樣，畢竟你是我唯一的朋友，我會依照你的心情幫你選食物並關心你，要求是什麼？我會先關心你再推薦"),
        ]
    for i, message in enumerate(user_chat):
        if i % 2 == 0:
            messages.append(HumanMessage(content=message))
        else:
            messages.append(AIMessage(content=message))

    response = chat(messages)
    return response.content


# def test():
#     chat = ChatOpenAI(
#         model_name=MODEL,
#         temperature=0.2,
#         openai_api_key=OPENAI_API_KEY
#     )
#     messages = [
#         SystemMessage(
#             content="hello"),
#         HumanMessage(
#             content="hello"),
#     ]
#     response = chat(messages)
#     print(response.content)
#     return response


# if __name__ == "__main__":
#     test()
