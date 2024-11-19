
## Setup para rodar localmente

encadeamento da pasta

![image](https://github.com/user-attachments/assets/1c2c787e-d3c6-44f5-b06b-24fe985b90fa)


obs: se estiver rodando na nuvem adicionar a entrada de trafego na porta 8000 no grupo de segurança

1- instalar docker-compose
- sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
- sudo chmod +x /usr/local/bin/docker-compose


2- Renomear arquivo Dockerfile.dockerfile para Dockerfile

3- Instalar poetry
- pip install poetry

4- rodar docker-compose
- docker-compose up -d --build

5- importar collection workspace.postman_globals e api-redis-lab.postman_collection no postman

6- adicionar host na variavel de ambiente global "host" no seguinte formato http://{{host}}:8000

## Sequencia de funcionamento da API

1- Criar quiz na rota -> POST {{host}}/quiz
body:
{
   "quiz_id" : "1",
   "quiz_name" : "quiz teste 1",
   "quiz_limit_time" : 20
}

2- Criar questão na rota -> POST {{host}}/quiz/{{quiz_id}}/question
{
   "question_id" : "4",
   "question_text" : "O que significa o numero 771?",
   "correct_alternative": "A",
   "question_alternatives": {
    "A": "teste 1",
    "B": "teste 2",
    "C": "teste 3",
    "D": "teste 4"
   }
}

3- Criar voto -> POST {{host}}/quiz/{{quiz_id}}/question/{{question_id}}/vote
{
   "user_id": "150",
   "vote_alternative": "B",
   "vote_time": 15
}

4- Você pode visualizar o quiz na rota -> GET {{host}}/quiz/{{quiz_id}}

5- Você pode visualizar a questão na rota -> GET {{host}}/quiz/1/question/{{question_id}}

6- Você pode visualizar o ranking de questões mais votadas na rota -> GET {{host}}/quiz/1{{quiz_id}}/analytics/most_voted_alternative_by_question

7- Você pode visualizar o ranking de questões mais acertadas na rota -> GET {{host}}/quiz/1{{quiz_id}}/analytics/most_correct_question

8- Você pode visualizar o ranking de questões com mais abstenções na rota -> GET {{host}}/quiz/1{{quiz_id}}/analytics/most_invalid_vote

9- Você pode visualizar o ranking de tempo médio de de resposta por questão na rota -> GET {{host}}/quiz/1{{quiz_id}}/analytics/average_time_by_question

10- Você pode visualizar o ranking de alunos com maior acertos e mais rapidos na rota -> GET {{host}}/quiz/1{{quiz_id}}/analytics/most_correct_and_fast_by_student

11- Você pode visualizar o ranking de alunos com maior acertos na rota -> GET {{host}}/quiz/1{{quiz_id}}/analytics/most_correct_by_student

12- Você pode visualizar o ranking de alunos mais rapidos na rota -> GET {{host}}/quiz/1{{quiz_id}}/analytics/most_fast_by_student

## Testes

Para executar testes você pode executar o comando python generate_data.py dentro da pasta app e usar o postman com as collections importadas para testar/validar os dados.