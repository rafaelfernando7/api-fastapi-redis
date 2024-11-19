import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi.encoders import jsonable_encoder

from app.redis_client import RedisClient
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import NumericFilter, Query


app = FastAPI()

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
redis_client = RedisClient(REDIS_HOST, REDIS_PORT)

ALTERNATIVES = ['A', 'B', 'C', 'D']


class Vote(BaseModel):
    user_id: int
    vote_alternative: str
    vote_time: int
    

class Question(BaseModel):
    question_text: str
    correct_alternative: str
    question_id: int
    question_alternatives: dict
    

class Quiz(BaseModel):
    quiz_id: int
    quiz_name: str
    quiz_limit_time: Optional[int]
    
    
@app.get("/")
def hello_world():
    return json.dumps({'200': 'Hello World!'})
    

@app.post("/quiz")
def create_quiz(quiz: Quiz):
    if redis_client.conn.hget("quiz:"+str(quiz.quiz_id), "quiz_name") is not None:
        return {"message": "Quiz already exists."}

    quiz_limit_time = 20
    
    if bool(quiz.quiz_limit_time) != False:
            quiz_limit_time = quiz.quiz_limit_time
        
    try:
        redis_client.conn.hset(f'quiz:{quiz.quiz_id}', mapping={"name": quiz.quiz_name, "limit_time": quiz_limit_time})
    except Exception as e:
        return e
    
    return {"message": "Quiz created successfully."}


@app.get("/quiz/{quiz_key}")
def get_quiz(quiz_key: str):
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    
    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
    
    return quiz


@app.post("/quiz/{quiz_key}/question")
def create_question(question: Question, quiz_key: str):
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    initial_vote = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    correct_votes = {'correct_votes': 0}
    invalid_votes = {'invalid_votes': 0}

    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
        
    alternatives = question.question_alternatives
    correct_alternative = question.correct_alternative
    alternatives_keys = question.question_alternatives.keys()
    j_question = jsonable_encoder(question)
    j_question.update(correct_votes)
    j_question.update(invalid_votes)
    
    try:
        schema = (
            TextField('$.question_text', as_name = "text"),  # 'question_text' será um campo de texto com peso maior
            TextField('$.correct_alternative', as_name = "correct"),        # 'correct_alternative' será um campo de texto
            NumericField('$.question_id', as_name = "question"),             # 'question_id' será um campo numérico
            NumericField('$.correct_votes', as_name = "correctv"),
            NumericField('$.invalid_votes', as_name = "invalidv"),
        )
        # Criar um índice para os campos definidos
        redis_client.conn.ft("idx:quiz_question") \
        .create_index(schema, definition=IndexDefinition(prefix=[f'quiz:{quiz_key}:question'], 
        index_type=IndexType.JSON))
    except:
        pass
    
    if alternatives is None:
        return {"message": 'All questions must have alternatives A, B, C and D.'}
        
    if len(alternatives_keys) != 4:
        return {"message": 'All questions must have 4 alternatives.'}
        
    for alternative in alternatives_keys:
        if alternative not in ALTERNATIVES:
            return {"message": f'Alternative {alternative} is missing.'}
        
    if correct_alternative not in ALTERNATIVES:
        return {"message": 'Correct alternative not given.'}

    if redis_client.conn.json().get(f'quiz:{quiz_key}:question:{question.question_id}', "$") is not None:
        return {"message": "Question already exists."}

    # Use the data from the request body
    try:
        redis_client.conn.json().set(f'quiz:{quiz_key}:question:{question.question_id}', "$", j_question)
        redis_client.conn.json().set(f'quiz:{quiz_key}:votes:question:{question.question_id}', "$", initial_vote)
    except Exception as e:    
        return {"message": e}
    
    return {"message": "Question created successfully."}


@app.get("/quiz/{quiz_key}/question/{question_key}")
def get_question(quiz_key: str, question_key: str):
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)

    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
        
    question = redis_client.conn.json().get(f'quiz:{quiz_key}:question:{question_key}', "$")
    
    if bool(question) == False:
        return {"message": 'Invalid selected question.'}
        
    question[0]['votes'] = redis_client.conn.json().get(f'quiz:{quiz_key}:votes:question:{question_key}', "$")

    return question[0]
    
    
@app.post("/quiz/{quiz_key}/question/{question_key}/vote")
def create_vote(vote: Vote, quiz_key: str, question_key: str):
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    question = redis_client.conn.json().get(f'quiz:{quiz_key}:question:{question_key}', "$")
    
    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
        
    if bool(question) == False:
        return {"message": 'Invalid selected question.'}
    
    question_id = question[0]['question_id']
    question_votes = redis_client.conn.json().get(f'quiz:{quiz_key}:votes:question:{question_id}', "$")
    j_quiz = convert_text_to_json(quiz)
    j_vote = jsonable_encoder(vote)
    j_vote['question_id'] = question_id
    j_vote['is_correct'] = 0
    
        
    if redis_client.conn.json().get(f'quiz:{quiz_key}:list_votes:{vote.user_id}:question:{question_id}', "$") is not None:
        return {"message": "Invalid vote. Vote already registered."}
        
    if vote.vote_time > int(j_quiz['limit_time']):
        return {"message": 'Response timeout exceeded.'}
        
    if vote.vote_alternative not in ALTERNATIVES:
        invalid_votes = int(question[0]['invalid_votes']) + 1
        question[0]['invalid_votes'] = invalid_votes
    else:
        question_votes[0][vote.vote_alternative] = int(question_votes[0].get(vote.vote_alternative)) + 1
        
    
    if question[0]['correct_alternative'] == vote.vote_alternative:
        correct_votes = int(question[0]['correct_votes']) + 1
        question[0]['correct_votes'] = correct_votes
        j_vote['is_correct'] = 1
        
    try:
        redis_client.conn.json().set(f'quiz:{quiz_key}:votes:question:{question_id}', "$", question_votes[0])
        redis_client.conn.json().set(f'quiz:{quiz_key}:list_votes:{vote.user_id}:question:{question_id}', "$", j_vote)
        redis_client.conn.json().set(f'quiz:{quiz_key}:question:{question_id}', "$", question[0])
        redis_client.conn.expire(f'quiz:{quiz_key}:votes:question:{question_id}', 2592000)
        redis_client.conn.expire(f'quiz:{quiz_key}:list_votes:{vote.user_id}:question:{question_id}', 2592000)
    except Exception as e:    
        return {"message": e}
        
    try:
        schema = (
            NumericField('$.user_id', as_name = "user"),
            NumericField('$.question_id', as_name = "question"),
            NumericField('$.vote_time', as_name = "time"),
            NumericField('$.is_correct', as_name = "iscorrect"),
            TextField('$.vote_alternative', as_name = "alternative"),
        )
        # Criar um índice para os campos definidos
        redis_client.conn.ft("idx:user_vote").create_index(schema, definition=IndexDefinition(prefix=[f'quiz:{quiz_key}:list_votes'], index_type=IndexType.JSON))
    except:
        pass
    
    return {"message": "Vote created successfully."}
    

@app.get("/quiz/{quiz_key}/analytics/most_voted_alternative_by_question")
def get_most_voted_alternative_by_question(quiz_key: str):
    result = []
    list_ids = []
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    
    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
        
    q = aggregations.AggregateRequest("*").group_by(['@question', '@alternative'], reducers.count().alias("total")).sort_by("@question")
    rows = redis_client.conn.ft("idx:user_vote").aggregate(q).rows
    
    for row in rows:
        if row[1] not in list_ids:
            result.append({'question_id': row[1], 'alternative': row[3], 'total': row[5]})
            list_ids.append(row[1])

    return result

    
    
@app.get("/quiz/{quiz_key}/analytics/most_correct_question")
def get_most_correct_question(quiz_key: str):
    result = []
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    
    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
        
    q = Query("*").return_field("$.question_id", as_field="question_id").return_field("$.correct_votes", as_field="correctv").sort_by("correctv", asc=False)
    rows = redis_client.conn.ft("idx:quiz_question").search(q).docs
    
    for row in rows:
        result.append({'question_id': row.question_id, 'total': row.correctv})
    
    return result
    

@app.get("/quiz/{quiz_key}/analytics/most_invalid_vote")
def get_most_invalid_vote(quiz_key: str):
    result = []
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    
    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
        
    q = Query("*").return_field("$.question_id", as_field="question_id").return_field("$.invalid_votes", as_field="invalidv").sort_by("invalidv", asc=False)
    rows = redis_client.conn.ft("idx:quiz_question").search(q).docs
    
    for row in rows:
        result.append({'question_id': row.question_id, 'total': row.invalidv})
    
    return result


@app.get("/quiz/{quiz_key}/analytics/average_time_by_question")
def get_average_time_by_question(quiz_key: str):
    result = []
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    
    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
        
    q = aggregations.AggregateRequest("*").group_by(['@question'], reducers.avg('@time').alias("avg")).sort_by("@question")
    rows = redis_client.conn.ft("idx:user_vote").aggregate(q).rows
    
    for row in rows:
        result.append({'question_id': row[1], 'time_average': row[3]})

    return result


@app.get("/quiz/{quiz_key}/analytics/most_correct_and_fast_by_student")
def get_most_correct_and_fast_by_student(quiz_key: str):
    result = []
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    
    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
    
    q = aggregations.AggregateRequest("*") \
        .group_by(['@user'], reducers.sum('@iscorrect')
            .alias('points'), reducers.avg('@time')
            .alias("time_average")) \
        .sort_by(aggregations.Desc("@points"), aggregations.Asc("@time_average"))
    rows = redis_client.conn.ft("idx:user_vote").aggregate(q).rows
    
    for row in rows:
        result.append({'user_id': row[1], 'points': row[3], 'time_average': row[5]})
    
    return result 
    

@app.get("/quiz/{quiz_key}/analytics/most_correct_by_student")
def get_most_correct_by_student(quiz_key: str):
    result = []
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    
    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
    
    q = aggregations.AggregateRequest("*") \
    .group_by(['@user'], reducers.sum('@iscorrect').alias('points')) \
    .sort_by(aggregations.Desc("@points"))
    rows = redis_client.conn.ft("idx:user_vote").aggregate(q).rows
    
    for row in rows:
        result.append({'user_id': row[1], 'points': row[3]})
    
    return result
    

@app.get("/quiz/{quiz_key}/analytics/most_fast_by_student")
def get_most_fast_by_student(quiz_key: str):
    result = []
    quiz = redis_client.conn.hgetall("quiz:"+quiz_key)
    
    if bool(quiz) == False:
        return {"message": 'Invalid selected quiz.'}
    
    q = aggregations.AggregateRequest("*").group_by(['@user'], reducers.avg('@time').alias("time_average")).sort_by("@time_average")
    rows = redis_client.conn.ft("idx:user_vote").aggregate(q).rows
    
    for row in rows:
        result.append({'user_id': row[1], 'time_average': row[3]})
    
    return result
    
def convert_text_to_json(text):
    return json.loads(str(text).replace('b','').replace('"','').replace("'",'"'))
    