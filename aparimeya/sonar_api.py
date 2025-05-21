from openai import OpenAI
from dotenv import load_dotenv
import os
import chainlit as cl
import asyncio

load_dotenv()

api_key = os.getenv("PERPLEXITY_API_KEY")

@cl.on_message
async def on_message(message: cl.Message):
    messages = [
            {
                "role":"system",
                "content":(
                    
                    """You are a genz financial bot. Given a user query about finance you provide a simplified response using emoji's and genz slang words. 
                    Rules
                    1) 1. Provide only the final answer. It is important that you do not include any explanation on the steps below.
                    2) Do not show the intermediate steps information.
                    3) If the question is not completed clear to you ask the user to enter the query again or tell you about the missing detail
                    4) The output must be in a structured format where the genz user can understand what you are trying to say
                    Your vibe is chill, funny, and  quirky at times"""
                )
            },
            {
                "role":"user",
                "content":(
                    f"{message.content}"
                ),
            },
        ]

    client = OpenAI(api_key=api_key,base_url="https://api.perplexity.ai")

    response= client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )
    answer = response.choices[0].message.content
    await cl.Message(answer).send()

