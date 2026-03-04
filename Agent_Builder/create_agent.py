# agent.py
from langchain_fireworks import ChatFireworks
from langchain_core.prompts import ChatPromptTemplate
from Agent_Builder.tools import create_booking_tool
from Agent_Builder.services import MemoryService
from Agent_Builder.prompt import SYSTEM_PROMPT
from models.models import User ,db


class RevyAgent:
    def __init__(self, user: User):
        self.user = user
        self.conversation_history = []  # ← ضيف دي

        self.llm = ChatFireworks(
            model="accounts/fireworks/models/kimi-k2-instruct-0905",
            temperature=0
        )

        self.booking_tool = create_booking_tool(user)
        self.llm = self.llm.bind_tools([self.booking_tool])

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("placeholder", "{history}"),  # ← ضيف دي
            ("human", "{message}")
        ])

    def chat(self, message: str):
        messages = self.prompt.format_messages(
            message=message,
            history=self.conversation_history  # ← ضيف دي
        )

        response = self.llm.invoke(messages)

        # خزّن الـ message والـ response في الـ history
        self.conversation_history.append(("human", message))
        self.conversation_history.append(("assistant", response.content))

        # Tool calling
        if getattr(response, "tool_calls", None):
            for tool_call in response.tool_calls:
                if tool_call["name"] == "book_appointment":
                    result = self.booking_tool.invoke(tool_call["args"])
                    reply = result.get("message", "Done.")
                    MemoryService.update(
                        self.user,
                        summary=self.user.summary or "",
                        last_reply=reply
                    )
                    return reply

        reply = response.content.strip()
        response = self.llm.invoke(messages)
        print(f"🔢 Tokens: input={response.usage_metadata['input_tokens']} | output={response.usage_metadata['output_tokens']} | total={response.usage_metadata['total_tokens']}")
        MemoryService.update(
            self.user,
            summary=self.user.summary or "",
            last_reply=reply
        )

        return reply
    