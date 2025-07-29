from google.adk.agents import Agent

from adk_test_bot.prompt import ROOT_AGENT_INSTRUCTION
from adk_test_bot.tools import count_characters

root_agent = Agent(
    name="adk_test_bot",
    model="gemini-2.0-flash",
    description="A bot that creates a summary sentence for messages",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[count_characters],
)
