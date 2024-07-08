import json
import requests
from secret import LINE_CHANNEL_ACCESS_TOKEN
# Replace these variables with your actual data
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    RichMenuRequest,
    CreateRichMenuAliasRequest
)


class RichmenuData():
    def __init__(self, text, image, name):
        self.text = text
        self.image = image
        self.name = name


main_menu = """
{
  "size": {
    "width": 2500,
    "height": 843
  },
  "selected": true,
  "name": "main_menu",
  "chatBarText": "查看更多資訊",
  "areas": [
    {
      "bounds": {
        "x": 0,
        "y": 0,
        "width": 1250,
        "height": 843
      },
      "action": {
        "type": "uri",
        "uri": "https://liff.line.me/2005733926-rxZjpKdP"
      }
    },
    {
      "bounds": {
        "x": 1251,
        "y": 0,
        "width": 1249,
        "height": 843
      },
      "action": {
        "type": "message",
        "text": "開始使用"
      }
    }
  ]
}
"""

main_menu_image_path = "assets/main_menu.png"

intro_menu = """
{
  "size": {
    "width": 2500,
    "height": 843
  },
  "selected": true,
  "name": "intro_menu",
  "chatBarText": "查看更多資訊",
  "areas": [
    {
      "bounds": {
        "x": 0,
        "y": 0,
        "width": 2500,
        "height": 843
      },
      "action": {
        "type": "message",
        "text": "初始設定"
      }
    }
  ]
}
"""

intro_menu_image_path = "assets/intro_menu.png"


def delete_all_rich_menu(api_client):
    message_api = MessagingApi(api_client)
    response = message_api.get_rich_menu_list()
    for rich_menu in response.richmenus:
        message_api.delete_rich_menu(rich_menu.rich_menu_id)
    response = message_api.get_rich_menu_alias_list()
    for rich_menu_alias in response.aliases:
        message_api.delete_rich_menu_alias(rich_menu_alias.rich_menu_alias_id)


def set_rich_menu_image(rich_menu_id: str, image_path: str):
    # rich_menu_id = "your_rich_menu_id_here"
    channel_access_token = LINE_CHANNEL_ACCESS_TOKEN
    # image_path = "assets/rich_menu_image.jpg"

    url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"

    headers = {
        "Authorization": f"Bearer {channel_access_token}",
        "Content-Type": "image/jpeg"
    }

    with open(image_path, 'rb') as image_file:
        data = image_file.read()
        response = requests.post(url, headers=headers, data=data)

    print(response.status_code)
    print(response.text)


def set_rich_menu(api_client, rich_menu_data: RichmenuData, is_defalut: bool = False):
    message_api = MessagingApi(api_client)
    response = message_api.create_rich_menu_with_http_info(
        rich_menu_request=RichMenuRequest.from_dict(
            json.loads(rich_menu_data.text))
    )
    set_rich_menu_image(response.data.rich_menu_id,
                        rich_menu_data.image)

    message_api.create_rich_menu_alias_with_http_info(
        create_rich_menu_alias_request=CreateRichMenuAliasRequest(
            rich_menu_alias_id=rich_menu_data.name,
            rich_menu_id=response.data.rich_menu_id
        )
    )

    if is_defalut:
        message_api.set_default_rich_menu(response.data.rich_menu_id)


if __name__ == "__main__":
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        delete_all_rich_menu(api_client)
        default_rich_menu = RichmenuData(
            main_menu, main_menu_image_path, "main_menu")
        intro_rich_menu = RichmenuData(
            intro_menu, intro_menu_image_path, "intro_menu")
        set_rich_menu(api_client, default_rich_menu)
        set_rich_menu(api_client, intro_rich_menu)
