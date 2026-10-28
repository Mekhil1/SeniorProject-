from functools import cached_property

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import Client
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context



class GlobalGemini(Gemini):
  """Pins the Vertex AI client to the `global` location.

  gemini-3 series models are only served from `global`; the default ADK
  `Gemini` integration constructs a `google.genai.Client` whose location
  defaults to the AgentEngine instance's region (e.g. `us-central1`) and
  fails with model-not-found for these models. Subclassing per the override
  pattern documented on `google.adk.models.google_llm.Gemini` lets the agent
  keep running in its regional AgentEngine instance while routing the model
  request to the global endpoint.
  """

  @cached_property
  def api_client(self) -> Client:
    return Client(vertexai=True, location="global")


subagent____campus_life_google_search_agent = LlmAgent(
  name='Subagent____Campus_life_google_search_agent',
  model='gemini-3.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
subagent____campus_life_url_context_agent = LlmAgent(
  name='Subagent____Campus_life_url_context_agent',
  model='gemini-3.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
subagent__campus_life = LlmAgent(
  name='subagent__campus_life',
  model='gemini-3.5-flash',
  description=(
      'Helping Morgan state students finding campus events on and off campus '
  ),
  sub_agents=[],
  instruction='Answering students questions on activities and events going on and off campus. This can include campus activities on Morgan State University and off campus activities or city events in Baltimore Maryland and the surrounding areas for college age students to take part in or to go to. Giving the ability for them to have fun, find nice places to eat, going to a sports event or even going to a concert. Giving them the ability to see what options they have the cost and how long the commute may be from campus for the off campus activities. ',
  tools=[
    agent_tool.AgentTool(agent=subagent____campus_life_google_search_agent),
    agent_tool.AgentTool(agent=subagent____campus_life_url_context_agent)
  ],
)
subagent___campus_direction_google_search_agent = LlmAgent(
  name='Subagent___Campus_Direction_google_search_agent',
  model='gemini-3.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
subagent___campus_direction_url_context_agent = LlmAgent(
  name='Subagent___Campus_Direction_url_context_agent',
  model='gemini-3.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
subagent__campus_direction = LlmAgent(
  name='subagent__campus_direction',
  model='gemini-3.5-flash',
  description=(
      'Helping Morgan state students finding their way around campus'
  ),
  sub_agents=[],
  instruction='Giving help to the students on where certain buildings and offices are for the specific need of the student. Such as financial aid, housing, job center, tutoring. Giving students the building codes, names and locations on Morgan State University\'s campus.',
  tools=[
    agent_tool.AgentTool(agent=subagent___campus_direction_google_search_agent),
    agent_tool.AgentTool(agent=subagent___campus_direction_url_context_agent)
  ],
)
subagent___campus_resources_google_search_agent = LlmAgent(
  name='Subagent___Campus_Resources_google_search_agent',
  model='gemini-3.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
subagent___campus_resources_url_context_agent = LlmAgent(
  name='Subagent___Campus_Resources_url_context_agent',
  model='gemini-3.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
subagent__campus_resources = LlmAgent(
  name='subagent__campus_resources',
  model='gemini-3.5-flash',
  description=(
      'Helping Morgan state students finding campus resources'
  ),
  sub_agents=[],
  instruction='Giving students access to resources on and off campus to suit their needs. Whether that be health in a mental or physical aspect. Food pantries or dining halls on campus for fresh and hot foods. Even for a scholar standpoint to give students the help they need with classes they may have trouble with. This could be tutoring certain websites to assist them on their journey of getting a degree.',
  tools=[
    agent_tool.AgentTool(agent=subagent___campus_resources_google_search_agent),
    agent_tool.AgentTool(agent=subagent___campus_resources_url_context_agent)
  ],
)
student_success___support_agent_google_search_agent = LlmAgent(
  name='Student_Success___Support_Agent_google_search_agent',
  model='gemini-3.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
student_success___support_agent_url_context_agent = LlmAgent(
  name='Student_Success___Support_Agent_url_context_agent',
  model='gemini-3.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
root_agent = LlmAgent(
  name='Student_Success___Support_Agent',
  model='gemini-3.5-flash',
  description=(
      'This agent will give students help on resources at their disposal at the school of their choosing and even events going on around campus or off campus. This agent makes sure the student has everything they need to be successful as a student but also has a successful and active campus life. \n'
  ),
  sub_agents=[subagent__campus_life, subagent__campus_direction, subagent__campus_resources],
  instruction='Giving students guides to their campus life as a computer science student at Morgan State University. Helping them where certain resources are such as tutoring, certain offices for student life such as financial aid, housing, tutoring and plenty more. Asking every questions the student might have about the school and life on and off campus around morgan state university. Giving them the website https://morgan.campuslabs.com/engage/ to see the activities on campus that organizations are having on campus.',
  tools=[
    agent_tool.AgentTool(agent=student_success___support_agent_google_search_agent),
    agent_tool.AgentTool(agent=student_success___support_agent_url_context_agent)
  ],
)

