import json
import random


def get_random_supporting_sentences():
    with open("assets/random_sentences", "r") as f:
        sentences = f.readlines()
    return random.choice(sentences).strip()


def get_question(index):
    with open("assets/questions.json", "r", encoding='utf-8') as f:
        questions = json.load(f)
    if not 0 <= index < len(questions):
        return None
    q = questions[index]
    q["question"] = f"{index+1}. {q['question']}"
    return q


if __name__ == '__main__':
    print(get_question(0))
