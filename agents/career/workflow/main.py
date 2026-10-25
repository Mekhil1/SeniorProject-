from vertexai.agent_engines import AdkApp

from .agent import root_agent

app = AdkApp(agent=root_agent)
