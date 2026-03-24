# agent.py
from langchain_fireworks import ChatFireworks
from langchain_core.prompts import ChatPromptTemplate
from Agent_Builder.tools import create_booking_tool , create_rag_tool
from Agent_Builder.services import MemoryService
from Agent_Builder.prompt import SYSTEM_PROMPT
from models.models import User ,db
import re


class RevyAgent:
    def __init__(self, user: User):
        self.user = user
        self.user.summary=""

        self.llm = ChatFireworks(
            model="accounts/fireworks/models/kimi-k2-instruct-0905",
            temperature=0
        )

        self.booking_tool = create_booking_tool(user)
        self.rag_tool = create_rag_tool()
        self.llm = self.llm.bind_tools([self.booking_tool, self.rag_tool])

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),

            ("human", "{message}")
        ])

    def _build_messages(self, message: str):
        """Add the summary from the DB as a contex"""
        messages = self.prompt.format_messages(message=message)
        
        # لو في summary محفوظ، حطه قبل الـ message
        if self.user.summary:
            from langchain_core.messages import SystemMessage
            summary_msg = SystemMessage(content=f"Previous conversation summary:\n{self.user.summary}")
            messages.insert(1, summary_msg)
        
        return messages
    
    def _update_summary(self, human_msg: str, assistant_reply: str):
        """Send to LLM to make an updated summary"""
        summary_prompt = f"""
        Previous summary: {self.user.summary or 'None'}

        New exchange:
        User: {human_msg}
        Assistant: {assistant_reply}
 
        Update the summary concisely in 2-3 sentences to include the new information.
        """
        summary_response = ChatFireworks(
            model="accounts/fireworks/models/kimi-k2-instruct-0905",
            temperature=0
        ).invoke(summary_prompt)
        print(summary_response)
        
        return summary_response.content.strip()


    def chat(self, message: str):
        messages = self.prompt.format_messages(
            message=message,
           
        )

        response = self.llm.invoke(messages)

    
        # Tool calling
        if getattr(response, "tool_calls", None):
            for tool_call in response.tool_calls:
                print(f"🔧 Tool used: {tool_call['name']}")

                if tool_call["name"] == "book_appointment":
                    print("📅 Booking appointment...")
                    result = self.booking_tool.invoke(tool_call["args"])
                    reply = result.get("message", "Done.")
                
                elif tool_call["name"] == "query_knowledge_base":
                    print("🔍 Searching knowledge base...")
                    tool_result = self.rag_tool.invoke(tool_call["args"])
                    messages.append(response)
                    messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result
                })
                    print(tool_result)
                    print(f"📄 Tool result length: {len(tool_result)} chars")
                    second_response = self.llm.invoke(messages)
                    print(f"🔢 RAG Tokens: input={second_response.usage_metadata['input_tokens']} | output={second_response.usage_metadata['output_tokens']} | total={second_response.usage_metadata['total_tokens']}")
                    print(f"🔢 Tokens: input={response.usage_metadata['input_tokens']} | output={response.usage_metadata['output_tokens']} | total={response.usage_metadata['total_tokens']}")

                    full_reply = second_response.content.strip()
                    # استخرج الـ summary من الرد
                    match = re.search(r'<summary>(.*?)</summary>', full_reply, re.DOTALL)
                    if match:
                        new_summary = match.group(1).strip()
                        reply = full_reply[:match.start()].strip()
                    else:
                        reply = re.sub(r'</summary>', '', full_reply).strip()
                        new_summary = self.user.summary or ""
                        reply = full_reply    

                else:
                    reply = "I couldn't process that request."   
                new_summary = self._update_summary(message, reply)
                MemoryService.update(
                        self.user,
                        summary=new_summary,
                        last_reply=reply
                    )
                return reply

        reply = response.content.strip()

        print(f"🔢 Tokens: input={response.usage_metadata['input_tokens']} | output={response.usage_metadata['output_tokens']} | total={response.usage_metadata['total_tokens']}")
        new_summary = self._update_summary(message, reply)
        
        MemoryService.update(
            self.user,
            summary=new_summary,
            last_reply=reply
        )

        return reply
    