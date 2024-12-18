import asyncio
import redis
import openai
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from uvicorn import Config, Server

app = FastAPI()

redis.UsernamePasswordCredentialProvider(username=None, password="devzoneadmin")

import redis.asyncio as redis

# Redis 설정
r = redis.Redis(host="10.150.2.41", password="devzoneadmin", port=6379, db=0, decode_responses=True)
REDIS_SUB_CHANNEL = "question"

# OpenAI API 설정
openai.api_key = ''

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# SSE 엔드포인트: 클라이언트가 질문을 보내고 실시간으로 응답 받음
@app.get("/chat/{user_key}")
async def chat_sse(request: Request, user_key: str, question: str):
    """SSE 연결을 통해 질문을 받고, 그에 대한 응답을 Redis에서 받는 엔드포인트"""

    # Redis에 질문을 publish
    # await r.publish(f"{REDIS_PUB_CHANNEL}:{user_key}", question)

    # SSE로 Redis Pub/Sub 스트림을 구독하여 응답 대기
    event_generator = pub_sub_redis_stream(user_key)
    return EventSourceResponse(event_generator)

async def pub_sub_redis_stream(user_key: str):
    """Redis Pub/Sub 구독을 통해 클라이언트에게 실시간으로 메시지를 전달"""
    pubsub = r.pubsub()
    await pubsub.subscribe(f"{REDIS_SUB_CHANNEL}:{user_key}")
    print(user_key)
    async for message in pubsub.listen():
        if message["type"] == "message":
            yield {
                "data": message["data"],
                "event": "message"
            }

async def get_chatgpt_response(question: str):
    """ChatGPT API를 호출하여 질문에 대한 답변을 반환하는 함수"""
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 챗 모델을 사용할 때는 ChatCompletion 사용
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},  # 시스템 메시지
            {"role": "user", "content": question}  # 사용자의 질문
        ],
        max_tokens=3,
    )

    return response.choices[0].message['content'].strip()

async def worker():
    """Redis Pub/Sub 매커니즘을 통해 메시지를 처리하는 워커 프로세스"""
    pubsub = r.pubsub()
    print("hihi")
    await pubsub.subscribe(f"{REDIS_SUB_CHANNEL}:2022111401")
    async for message in pubsub.listen():
        if message["type"] == "message":
            question = message["data"]
            user_key = extract_user_key_from_message(message)  # 메시지에서 user_key 추출

            response = await get_chatgpt_response(question)

            await r.publish(f"{REDIS_SUB_CHANNEL}:{user_key}", response)

def extract_user_key_from_message(message):
    channel = message["channel"]
    return channel.split(":")[-1]

async def start_server():
    config = Config(app=app, host="0.0.0.0", port=8000, loop="asyncio")
    server = Server(config=config)
    await server.serve()

async def main():
    await asyncio.gather(
        worker(),
        start_server()
    )

# 메인 실행
if __name__ == "__main__":
    asyncio.run(main())