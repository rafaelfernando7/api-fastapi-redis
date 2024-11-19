import requests
import random
import time

BASE_URL = "http://127.0.0.1:8000"

# 1. Criar Quizzes
def create_quizzes():
    quizzes = [
        {"quiz_id": 1, "quiz_name": "Quiz de Tecnologia", "quiz_limit_time": 600},
        {"quiz_id": 2, "quiz_name": "Quiz de História", "quiz_limit_time": 900},
    ]
    for quiz in quizzes:
        response = requests.post(f"{BASE_URL}/quiz", json=quiz)
        print(f"Quiz: {quiz['quiz_name']} -> {response.json()}")

# 2. Criar Perguntas
def create_questions():
    questions = [
        {
            "quiz_id": 1,
            "questions": [
                {
                    "question_text": "Qual é a capital da França?",
                    "correct_alternative": "A",
                    "question_id": 101,
                    "question_alternatives": {
                        "A": "Paris",
                        "B": "Londres",
                        "C": "Roma",
                        "D": "Berlim",
                    },
                },
                {
                    "question_text": "Qual linguagem de programação é usada para criar sites dinâmicos?",
                    "correct_alternative": "B",
                    "question_id": 102,
                    "question_alternatives": {
                        "A": "C++",
                        "B": "JavaScript",
                        "C": "Java",
                        "D": "Python",
                    },
                },
            ],
        },
        {
            "quiz_id": 2,
            "questions": [
                {
                    "question_text": "Quem descobriu o Brasil?",
                    "correct_alternative": "C",
                    "question_id": 201,
                    "question_alternatives": {
                        "A": "Dom Pedro II",
                        "B": "Cristóvão Colombo",
                        "C": "Pedro Álvares Cabral",
                        "D": "Vasco da Gama",
                    },
                },
                {
                    "question_text": "Em que ano aconteceu a Revolução Francesa?",
                    "correct_alternative": "D",
                    "question_id": 202,
                    "question_alternatives": {
                        "A": "1500",
                        "B": "1776",
                        "C": "1905",
                        "D": "1789",
                    },
                },
            ],
        },
    ]
    for quiz in questions:
        quiz_key = quiz["quiz_id"]
        for question in quiz["questions"]:
            response = requests.post(f"{BASE_URL}/quiz/{quiz_key}/question", json=question)
            print(f"Question ID {question['question_id']} -> {response.json()}")

# 3. Criar Votos
def create_votes():
    votes = [
        {"quiz_id": 1, "question_id": 101, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B"]), "vote_time": random.randint(1, 20)} for i in range(1, 2)]},
        {"quiz_id": 1, "question_id": 102, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B"]), "vote_time": random.randint(1, 20)} for i in range(1, 2)]},
        {"quiz_id": 1, "question_id": 101, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B"]), "vote_time": random.randint(1, 20)} for i in range(1, 2)]},
        {"quiz_id": 1, "question_id": 101, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B"]), "vote_time": random.randint(1, 20)} for i in range(1, 2)]},
        {"quiz_id": 1, "question_id": 101, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B"]), "vote_time": random.randint(1, 20)} for i in range(1, 2)]},
        {"quiz_id": 1, "question_id": 102, "votes": [{"user_id": i, "vote_alternative": random.choice(["W", "H", "G", "T"]), "vote_time": random.randint(1, 20)} for i in range(1, 10)]},
        {"quiz_id": 1, "question_id": 101, "votes": [{"user_id": i, "vote_alternative": random.choice(["W", "H", "G", "T"]), "vote_time": random.randint(1, 20)} for i in range(1, 10)]},
        {"quiz_id": 1, "question_id": 101, "votes": [{"user_id": i, "vote_alternative": random.choice(["W", "H", "G", "T"]), "vote_time": random.randint(1, 20)} for i in range(1, 10)]},
        {"quiz_id": 1, "question_id": 101, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B", "C", "D"]), "vote_time": random.randint(1, 20)} for i in range(1, 100)]},
        {"quiz_id": 1, "question_id": 102, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B", "C", "D"]), "vote_time": random.randint(1, 20)} for i in range(1, 100)]},
        {"quiz_id": 1, "question_id": 102, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B", "C", "D"]), "vote_time": random.randint(1, 20)} for i in range(1, 100)]},
        {"quiz_id": 1, "question_id": 102, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B", "C", "D"]), "vote_time": random.randint(1, 20)} for i in range(1, 100)]},
        {"quiz_id": 1, "question_id": 102, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B", "C", "D"]), "vote_time": random.randint(1, 20)} for i in range(1, 100)]},
        {"quiz_id": 1, "question_id": 102, "votes": [{"user_id": i, "vote_alternative": random.choice(["A", "B", "C", "D"]), "vote_time": random.randint(1, 20)} for i in range(1, 100)]},
    ]
    for vote_group in votes:
        quiz_key = vote_group["quiz_id"]
        question_key = vote_group["question_id"]
        for vote in vote_group["votes"]:
            response = requests.post(f"{BASE_URL}/quiz/{quiz_key}/question/{question_key}/vote", json=vote)
            try:
                print(f"Vote User {vote['user_id']} -> {response.json()}")
            except Exception as e:
                print(f"Erro: User {vote['user_id']} -> ")


# 4. Executar Funções
if __name__ == "__main__":
    print("Criando quizzes...")
    create_quizzes()
    time.sleep(1)

    print("\nCriando perguntas...")
    create_questions()
    time.sleep(1)

    print("\nCriando votos...")
    create_votes()
