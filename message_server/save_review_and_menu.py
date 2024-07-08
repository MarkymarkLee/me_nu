from database import db


def save_review_and_menu_to_doc(menu: str, review: str, title: str) -> str:
    id = db.save_menu(title, menu)
    db.save_review(id, review)
    return id
