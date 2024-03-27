
from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from app.services.tool import shell,python,searchFromGoogle

from app import schemas
import os
router = APIRouter()

os.environ["OPENAI_API_KEY"] = ""

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>llm</title>
    </head>
    <body>
    </body>
</html>
"""

@router.get("/")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws",response_model=schemas.AskResponse)
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    vector = FAISS.load_local('./data', OpenAIEmbeddings())
    retriever = vector.as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        "domain_knowledge_search",
        "Search for information about domain knowledge. For any questions about this domain, you must use this tool!",
    )
    tools = [searchFromGoogle, retriever_tool, shell, python]
    prompt = hub.pull("hwchase17/openai-tools-agent")

    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=500,
                                   handle_parsing_errors="Check your output and make sure it conforms, use the Action/Action Input syntax", )
    
    while True:
        async for chunk in agent_executor.astream(
                {"input": "Complex problem",}
        ):
            # Agent Action
            if "actions" in chunk:
                for action in chunk["actions"]:
                    await websocket.send_text(f"Calling Tool: `{action.tool}` with input `{action.tool_input}`")
                    print(f"Calling Tool: `{action.tool}` with input `{action.tool_input}`")
            # Observation
            elif "steps" in chunk:
                for step in chunk["steps"]:
                    await websocket.send_text(f"Tool Result: `{step.observation}`")
                    print(f"Tool Result: `{step.observation}`")
            # Final result
            elif "output" in chunk:
                await websocket.send_text(f'Final Output: {chunk["output"]}')
                print(f'Final Output: {chunk["output"]}')
                break
            else:
                raise ValueError()
            print("---")


