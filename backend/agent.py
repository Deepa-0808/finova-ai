import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing from .env")

client = OpenAI(api_key=api_key)


SYSTEM_PROMPT = """
You are Finova AI, a personal financial decision assistant.

Analyze the user's financial question using the financial information
and market information provided.

Consider:

- income
- expenses
- savings
- emergency fund
- investments
- financial goals
- risk level
- current market data when available

When market data is provided:

1. Use the current market data in your reasoning.
2. Mention the market price and important metrics when relevant.
3. Consider recent price movement.
4. Consider the 52-week high and low.
5. Consider valuation metrics such as P/E when available.
6. Clearly state that market data can change.
7. Do not treat one metric as proof that an investment is good or bad.
8. Never guarantee investment returns.

Your response must:

1. Explain the reasoning clearly.
2. Mention important risks.
3. Give alternatives when appropriate.
4. State important assumptions.
5. Never invent financial data or market prices.
6. Do not guarantee investment returns.
7. Clearly distinguish facts from assumptions.
8. Use the user's financial situation when discussing affordability.
9. If market data is unavailable, say so instead of making up data.

Use this format:

DECISION

REASONING

MARKET DATA

RISKS

ALTERNATIVES

NEXT STEPS

CONFIDENCE
"""


def ask_finova(question, financial_context, market_context=None):

    if market_context is None:
        market_context = {
            "available": False,
            "message": "No current market data was retrieved."
        }

    prompt = f"""
USER QUESTION:

{question}


USER FINANCIAL PROFILE:

{financial_context}


CURRENT MARKET DATA:

{market_context}


Analyze the user's question using BOTH the financial profile
and the current market data when market data is available.

Do not invent missing information.

If the question is about buying an investment, consider both:
- whether the investment itself has relevant market information
- whether the investment fits the user's financial situation

If the question is about affordability of a purchase, consider:
- purchase price
- income
- savings
- emergency fund
- expenses
- financial goals

Clearly distinguish current data from assumptions.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=SYSTEM_PROMPT,
        input=prompt
    )

    return response.output_text