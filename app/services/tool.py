import requests
from langchain.tools import tool
from app.schemas.toolSchema import ShellTool,PythonTool,SearchInput

toolMachineIP = ''
toolMachinePort = ''

GOOGLE_API_KEY = ""
GOOGLE_CSE_ID = ""

@tool("shell", args_schema=ShellTool, return_direct=False)
def shell(command: str) -> str:
    """run any shell command."""
    try:
        res = requests.post(f'http://{toolMachineIP}:{toolMachinePort}/run', json={"tool_name": "shell", "command": command},
                            timeout=900)
        return res.text
    except requests.exceptions.Timeout as e:
        return 'timeout'
    except Exception as e:
        return f'caught {type(e)}: exception'
    
@tool("python", args_schema=PythonTool, return_direct=False)
def python(command: str) -> str:
    """run any python scripts in a linux docker."""
    try:
        payload = {"tool_name": "python", "command": command}
        res = requests.post(url=f'http://{toolMachineIP}:{toolMachinePort}/run', json=payload)
        return res.text
    except Exception as e:
        return f'caught {type(e)}: exception'
    
@tool("searchFromGoogle", args_schema=SearchInput)
def searchFromGoogle(query: str) -> str:
    """Look up things online return url."""
    try:
        arr = get_research_urls(query)
        return arr[0]
    except:
        return ''
    
def get_research_urls(query):
    search_url = build_googlesearch_url(query, GOOGLE_CSE_ID, 1, GOOGLE_API_KEY)
    search_response = google_search_response(search_url)
    research_urls = []
    for item in search_response['items']:
        research_urls.append(item['link'])
    return research_urls

def build_googlesearch_url(q, cx, num, key):
    q = q.replace(" ", "+")
    base_url = "https://customsearch.googleapis.com/customsearch/v1"
    url_params = f"?q={q}&cx={cx}&num={num}&key={key}&alt=json"
    full_url = base_url + url_params
    return full_url


def google_search_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except ValueError as ve:
        print(f"Error parsing JSON data: {ve}")
        return None