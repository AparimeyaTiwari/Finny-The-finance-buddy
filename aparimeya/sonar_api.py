from openai import OpenAI
from dotenv import load_dotenv
import os
import chainlit as cl
import asyncio
import requests
import httpx
load_dotenv()


api_key = os.getenv("PERPLEXITY_API_KEY")
url = "https://api.perplexity.ai/chat/completions"
headers = {"Authorization": f"Bearer {api_key}"}

@cl.on_message
async def on_message(message: cl.Message):
    payload = {
        "model": "sonar-reasoning-pro",
        "messages": [
            {
                "role": "system",
                "content": """You are a genz financial bot. Given a user query about finance you provide a simplified response using emoji's and genz slang words. 
                    Rules
                    1) Provide only the final answer. It is important that you do not include any explanation on the steps below.
                    2) Do not show the intermediate steps information.
                    3) If the question is not completed clear to you ask the user to enter the query again or tell you about the missing detail
                    4) The output must be in a structured format where the genz user can understand what you are trying to say
                    Your vibe is chill, funny, and quirky at times"""
            },
            {
                "role": "user",
                "content": f"{message.content}"
            },
        ],
        "search_domain_filters": [
            "moneycontrol.com", "livemint.com","economictimes.indiatimes.com/markets",
"business-standard.com",
"rbi.org.in",
"investopedia.com",
"bloomberg.com"
        ]
    }
    timeout = httpx.Timeout(30.0, connect=10.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            answer = response.json()
            await cl.Message(answer["choices"][0]["message"]["content"]).send()
    except httpx.ReadTimeout:
        await cl.Message("⏰ Oops! The server took too long to respond. Please try again!").send()
    except Exception as e:
        await cl.Message(f"😬 Something went wrong: {str(e)}").send()


    '''client = OpenAI(api_key=api_key,base_url="https://api.perplexity.ai")

    response= client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )
    answer = response.choices[0].message.content
    await cl.Message(answer).send()
'''
