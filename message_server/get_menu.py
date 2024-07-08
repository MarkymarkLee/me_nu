from database import db


def get_menu_from_title(title):
    store_title_dict = db.list_menus()
    for key in store_title_dict:
        store_title = store_title_dict[key]
        if title == store_title or title in store_title:
            menu = db.get_menu(key)
            return menu
    return None


def get_menu_and_review_from_qr(qr_data: str):
    menu = db.get_menu(qr_data.strip())
    review = db.get_review(qr_data.strip())
    return menu, review
