import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import List
from enum import Enum


class UserPreference():
    def __init__(self, cannotEatFood: List[str] = [], dislikedFood: List[str] = [], likedFood: List[str] = []) -> None:
        self.cannotEatFood = cannotEatFood
        self.dislikedFood = dislikedFood
        self.likedFood = likedFood

    @classmethod
    def from_dict(cls, data: dict):
        return UserPreference(
            cannotEatFood=data.get("cannotEatFood", []),
            dislikedFood=data.get("dislikedFood", []),
            likedFood=data.get("likedFood", []),
        )

    def to_dict(self):
        return {
            "cannotEatFood": self.cannotEatFood,
            "dislikedFood": self.dislikedFood,
            "likedFood": self.likedFood,
        }

    def merge(self, other):
        self.cannotEatFood += other.cannotEatFood
        self.dislikedFood += other.dislikedFood
        self.likedFood += other.likedFood

        self.cannotEatFood = list(set(self.cannotEatFood))
        self.dislikedFood = list(set(self.dislikedFood))
        self.likedFood = list(set(self.likedFood))


class UserState(Enum):
    INIT = 0
    INIT_QA = 1
    INIT_DONE = 2
    MAIN_MENU_REQUEST = 4
    MAIN_NEED_REQUEST = 5
    MAIN_WAIT_RECOMMENDATION = 6
    MAIN_AUTO_CHAT = 7


class Userdata():
    def __init__(self, userId: str, pictureUrl: str = "", displayName: str = "",
                 preferences: UserPreference = UserPreference(), statusMessage: str = "",
                 userState=UserState.INIT, user_init_qa_count: int = 0, images: List[str] = [],
                 rec_count: int = 3, user_character: str = "美食評論家", chat: List[str] = [],
                 last_chat_time: int = -1, menu_data: str = "", review_data: str = "") -> None:
        self.pictureUrl = pictureUrl
        self.displayName = displayName
        self.preferences = preferences
        self.statusMessage = statusMessage
        self.userId = userId
        self.userState = userState
        self.user_init_qa_count = user_init_qa_count
        self.images = images
        self.rec_count = rec_count
        self.chat = chat
        self.last_chat_time = last_chat_time
        self.user_character = user_character
        self.menu_data = menu_data
        self.review_data = review_data

    def to_dict(self):
        return {
            "pictureUrl": self.pictureUrl,
            "displayName": self.displayName,
            "preferences": self.preferences.to_dict(),
            "statusMessage": self.statusMessage,
            "userId": self.userId,
            "userState": self.userState.value,
            "user_init_qa_count": self.user_init_qa_count,
            "images": self.images,
            "rec_count": self.rec_count,
            "chat": self.chat,
            "last_chat_time": self.last_chat_time,
            "userCharacter": self.user_character,
            "menu_data": self.menu_data,
            "review_data": self.review_data,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return Userdata(
            userId=data["userId"],
            pictureUrl=data.get("pictureUrl", ""),
            displayName=data.get("displayName", ""),
            preferences=UserPreference.from_dict(data.get("preferences", {})),
            statusMessage=data.get("statusMessage", ""),
            userState=UserState(data.get("userState", 0)),
            user_init_qa_count=data.get("user_init_qa_count", 0),
            images=data.get("images", []),
            rec_count=data.get("rec_count", 3),
            chat=data.get("chat", []),
            last_chat_time=data.get("last_chat_time", -1),
            user_character=data.get("userCharacter", "美食評論家"),
            menu_data=data.get("menu_data", ""),
            review_data=data.get("review_data", ""),
        )


class Database():
    def __init__(self, name=None) -> None:
        cred = credentials.Certificate("secret_service_account.json")
        if name is None:
            app = firebase_admin.initialize_app(cred)
        else:
            app = firebase_admin.initialize_app(cred, name=name)
        self._db = firestore.client(app)

    def get_user_data(self, user_id: str) -> Userdata:
        snapshot = self._db.collection("users").document(user_id).get()
        if not snapshot.exists:
            return None
        user_data = snapshot.to_dict()
        return Userdata.from_dict(user_data)

    def update_user_data(self, user_data: Userdata):
        self._db.collection("users").document(
            user_data.userId).update(user_data.to_dict())

    def update_user_preferences(self, user_id: str, preferences: UserPreference):
        user_preferences = self.get_user_data(user_id).preferences
        user_preferences.merge(preferences)
        self._db.collection("users").document(user_id).update({
            "preferences": user_preferences.to_dict()
        })

    def set_user_data(self, user_data: Userdata):
        self._db.collection("users").document(
            user_data.userId).set(user_data.to_dict())

    def get_image_base64(self, image_id: str):
        snapshot = self._db.collection("images").document(image_id).get()
        if not snapshot.exists:
            return None
        return snapshot.to_dict()

    def save_image_base64(self, base64_str: str, analysis_string: str) -> str:
        ref = self._db.collection("images").document()
        ref.set({
            "base64": base64_str,
            "analysis": analysis_string
        })
        return ref.id

    def delete_user_data(self, user_id: str):
        self._db.collection("users").document(user_id).delete()

    def list_menus(self):
        docs = self._db.collection("menus").get()
        menu_titles = {}
        for doc in docs:
            menu_titles[doc.id] = doc.to_dict()["title"]
        return menu_titles

    def get_menu(self, id):
        snapshot = self._db.collection("menus").document(id).get()
        if not snapshot.exists:
            return None
        return snapshot.to_dict()['content']

    def save_menu(self, title: str, content: str) -> str:
        doc = self._db.collection("menus").document()
        doc.set({
            "title": title,
            "content": content,
            "id": doc.id
        })
        return doc.id

    def save_review(self, id: str, content: str) -> str:
        doc = self._db.collection("reviews").document(id)
        doc.set({
            "content": content,
        })

    def get_review(self, id: str):
        snapshot = self._db.collection("reviews").document(id).get()
        if not snapshot.exists:
            return None
        return snapshot.to_dict()['content']


db = Database()

if __name__ == '__main__':
    print(db.list_menus())
