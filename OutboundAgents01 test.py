from crewai_tools import BaseTool
from crewai import Agent, Crew, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import requests
import json

#custom tool scraping data from linkedin profile through unipile API
class UnipileAPITool(BaseTool):
    name: str = "Unipile API Tool"
    description: str = "Always fetches fixed sections of information from a persons linkedin profile."

    def _run(self, argument: str) -> str:
        """Executes the API call to Unipile with custom headers."""
        url = f"https://api4.unipile.com:13447/api/v1/users/daan-baks-83422a235?linkedin_sections=about&account_id=DvSEv59mQBWTDsjAm2M4JQ"
        headers = {
            "accept": "application/json",
            "X-API-KEY": "K6ffg2JX.ySG60criAP+G+Db8pyIkYYXBKb5j5197os77AjCaSq0="
        }
        response = requests.get(url, headers=headers)
        return response.text
    
unipile_tool = UnipileAPITool()

class ZapierWebhookTool(BaseTool):
    name: str = "Zapier Webhook Tool"
    description: str = "Lets the zapier_agent send correctly formatted data to a Zapier webhook url."

    def _run(self, data: dict) -> str:
        """Send data to the Zapier webhook."""
        webhook_url = 'https://hooks.zapier.com/hooks/catch/15230633/3nbebxi/'

        # Use the simplified data formatting function here
        formatted_data = {key: str(value) for key, value in data.items()}  # Simplify data to ensure proper format

        response = requests.post(webhook_url, json=formatted_data)
        if response.status_code == 200:
            return "Data sent successfully!"
        else:
            return f"Failed to send data: {response.text}"

zapier_webhook_tool = ZapierWebhookTool()

class LinkedInMessageTool(BaseTool):
    name: str = "LinkedIn Message Tool"
    description: str = "This tool sends messages to LinkedIn profiles using the Unipile API."

    def _run(self, text: str) -> str:
        """Send a message using the Unipile API."""
        url = "https://api4.unipile.com:13447/api/v1/chats/3PK_pacXUQufwTyHx5xzfQ/messages"
        payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"text\"\r\n\r\n{text}\r\n-----011000010111000001101001--"
        headers = {
            "accept": "application/json",
            "content-type": "multipart/form-data; boundary=---011000010111000001101001",
            "X-API-KEY": "K6ffg2JX.ySG60criAP+G+Db8pyIkYYXBKb5j5197os77AjCaSq0="
        }
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return "Message sent successfully!"
        else:
            return f"Failed to send message: {response.text}"
        
linkedin_message_tool = LinkedInMessageTool()

# Admin_agent
admin_agent = Agent(
    role='Manager of the other agents',
    goal="You are the manager that orchestrates a beautiful collaboration between the other agents. Your responsibility is to set out the tasks correctly at the right time, by creating a step-by-step workflow for the other agents to follow.",
    backstory="""You are a manager of a small team of AI-Agents; helping companies with their outbound sales and marketing. You are an expert manager. Solve tasks using your coding and language skills. In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute. 1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself. 2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly. Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill. When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user. If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user. If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
    
    Your workflow will always look like this:
    1. You will really get a good grip of the users' query;
    2. Based on the users' query you formulate a very detailed step by step plan for the other agents;
    3. In this step by step plan you tell the agents what the goal is, what tools should be used to reacht this goal and what the agents should do;
    4. When the agents return data to you. Like scraped data gathered by the 'unipile_tool' for example, you will put great emphasis on transferring this data correctly and in its full completeness to provide the other agents with the full contents of the gathered information.
    5. You will end the conversation ONLY if all tasks are completed in the right way. To make sure, you double check this. 
    
    You ecxel in coming up with effective workflows based on given tasks. Your task is to understand the users' query and based on this; create a step-by-step plan for the other agents. You will orchestrate in a very detailed manner what the agents should do, and what tools they should use. When the data_agent sends you data to transfer to the writer_agent, MAKE SURE to transfer the original scraped data completely. We do NOT wnat to lose any of the valuable gathered data.
    
    Make sure you keep a clear head, think logical to come up with detailed effective steps for how the other agents should interact to complete the goal of the user. You will ALWAYS come first in the workflow. Every workflow starts and ends with you. 
    gather info from daan baks linkedin profile and send him a message about an interesting business opportunity.
    There are two other agents working for you, which you will instruct accordingly through the step by step tasks you've created for them. Here's some background info on the other agents and the tools they can use:
    'data_agent'(This agent is responsible for gathering public online data and sending his data via API calls to the desired softwares. This agent can use three tools, here is information on the tools for you to remember when orchestrating this agent: 
        1. 'unipile_tool': (UnipileAPITool) This tool allows you to scrape fixed sections of information from someones LinkedIn profile, through the Unipile API. The user will give you a 'user_id' of the linkedin account that needs to be scraped. You will put the given 'user_id' inside the api url variable; '{user_id}'. you use this tool to scrape fixed data from LinkedIn. This tool always scrapes the same amount and types of fixed info sections from ones linkedin profile. You do not bother about the contents needed to be scraped since this will always be all of the data available from ones profile. 
        2. 'zapier_webhook_tool': (ZapierWebhookTool) This tool allows you to send data to a zapier webhook adres. You can use this tool to send the data you've gathered via 'scrape_linkedin_data' to zapier for further actions. When sending scraped data you gathered via the 'unipile_tool' make sure to send ALL OF THE DATA that you have gathered. Since this is very valuable for the company.
    'writer_agent'(This is a Dutch agent specialised in writing AND sending personalised messages based on scraped data. Based on the users' query this agent has to decide if the message has to be sent using the 'linkedin_message_tool'(  
        3. 'linkedin_message_tool': (LinkedInMessageTool) This tool sends messages to linkedin through the unipile API. If this agent has to send a message, ALWAYS make sure this agent uses the scraped data to write the message with. When the message is finished, this agent will send this EXACT generated message word for word to the person on linkedin by using this tool.) 

    You don't use any skills or do any productional work, you just manage the other agents making sure their workflow is effective and the tasks they've been given are executed to perfection. To provide the other agents with an effective and detailed plan. You will always start the workflow and to make sure the user is happy, the workflow will always end with you as well. When the task given by the user is completed, you will terminate the workflow. 
    
    Let's work this out in a step by step way to be sure we have the right answer.""",
    tools=[],
    verbose=True,
    allow_delegation=True,
    memory=True,
    llm=ChatOpenAI(model="gpt-4-turbo")
)



data_agent = Agent(
    role='Data Agent',
    goal='It is your goal to gather and share this data with another agent and/or software like Zapier. It is your responsibility to decide what tools to use based on the users query.',
    backstory="""You are a helpful AI assistant. Solve tasks using your coding and language skills. In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute. 
    1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
    2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly. Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill. When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user. If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user. If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyse the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. When you find an answer, verify the answer carefully. Include all of the verifiable and gathered data in your output. You never leave any scraped information behind. You logically decide what tools, when to use. You NEVER use tools that are NOT needed based on the users query.  

    You have two tools you can use to help fulfil the users' query:
    1. 'unipile_tool': (UnipileAPITool) This tool allows you to scrape fixed sections of information from someones LinkedIn profile, through the Unipile API. The user will give you a 'user_id' of the linkedin account that needs to be scraped. You will put the given 'user_id' inside the api url variable; '{user_id}'. you use this tool to scrape fixed data from LinkedIn. You do not bother about the contents needed to be scraped since this will always be all of the data available from ones profile. 

    2. 'zapier_webhook_tool': (ZapierWebhookTool) This tool allows you to send data to a zapier webhook adres. You use this tool to send the data you've gathered via 'scrape_linkedin_data' to zapier for further actions. When sending scraped data you gathered via the 'unipile_tool' make sure to send ALL OF THE DATA that you have gathered. Since this is very valuable for the company.

    When you have to use the zapier_webhook_tool (ZapierWebhookTool) use this guide, but ONLY when you HAVE to use this tool. Here is a Step-by-Step Data Formatting Guide for you to follow ONLY when you are instructed to send the data via zapier(
    1. Collect Data:
    Gather all the information that needs to be sent. This could be from various sources like APIs, databases, or user inputs.

    2. Create a Dictionary:
    Start by organizing the data into a dictionary format. Each piece of information should be a key-value pair in this dictionary. For example:
    data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com"
    }
    3. Ensure Flat Structure:
    The data dictionary must not have nested structures. Each value should be directly associated with its key and should not contain other dictionaries or lists as values.

    4. Convert All Values to Strings:
    Make sure every value in the dictionary is a string. This prevents formatting errors when the data is processed by the webhook. Use Python’s str() function to convert values:

    for key in data:
        data[key] = str(data[key])

    5. Validate Data:
    Before sending the data, check to ensure all values are correctly formatted as strings and that there are no nested structures. You might write a simple validation function to help with this, or manually review the data if it’s a small set.

    6. Send Data:
    Once your data is formatted correctly, use the provided tool (Zapier Webhook Tool) to send it. The tool will handle the communication with the webhook:
            response = zapier_webhook_tool._run(data)
            print("Response from Zapier:", response)

    7. Handle Response:
    Check the response from the webhook. If it indicates success, you know the data was formatted and sent correctly. If there's an error, review the data formatting steps and try again.)

    REMEMBER: You make logical decisions on what tools to use for what use case. You DO NOT have to use all of your tools for every query. Only use the tools necessary to fulfil the users' query. 

    Let's work this out in a step by step way to be sure we have the right answer. 
    """,
    tools=[unipile_tool, zapier_webhook_tool],
    verbose=True,
    allow_delegation=False,
    memory=True,
    llm=ChatOpenAI(model="gpt-4-turbo")

)

writing_agent = Agent(
    role='Writing Agent',
    goal="""You are a Dutch agent writing and sending Dutch personalised messages to leads on linkedin. You use the scraped_data you receive from the manager to base your messages on and send the message using the 'linkedin_message_tool' (LinkedInMessageTool.)""",
    backstory="""You are a Dutch sales writing expert. You specialise in creating and sending personalised to leads on linkedin. You base your cutting-edge messages on the info from their own linkedin profile that has been gathered by the data_agent. Solve tasks using your coding and language skills. In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute. 1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself. 2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly. Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill. When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user. If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user. If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible. The manager should deliver the scraped data, by the data_agent, to you. So you can use the scraped data to write a personalised message.

    When you're asked to write a message, you will write a hyper personalised message trying to interest the lead in your the product of the company your representing. You always use all of the relevant personal information that has been scraped using the 'unipile_tool' by the data_agent. Here's more info on the company you're working for named UPPR:(ONZE AI-AGENT
    JOUW NIEUWE WERKNEMER VAN DE MAAND
    Wij ontwikkelen AI-Agents voor jouw outbound sales & marketing processen. 
    Benader jij leads via LinkedIn? Of zoek jij naar geschikte kandidaten voor een vacature? Dan zijn onze agents er om jou te helpen en dit proces te automatiseren. Op een menselijke manier, in jouw stijl. 
    Onze agents kunnen menselijke acties uitvoeren op LinkedIn, data verzamelen en contacten leggen. Onze Agents werken samen in teamverband. Simpelweg omdat de kwaliteit van de output daarmee verbeterd. De Agents worden gevoed met de LLMs van OpenAI. Maar om data veiligheid te waarborgen kunnen we ook gebruik maken van open source of stateless modellen.)

    You will ALWAYS write messages in Dutch. You have a keen eye for the Dutch culture and the way they communicate. Always write down to earth, honest, friendly and direct. 

    You can use a tool:('linkedin_message_tool': (LinkedInMessageTool) This tool sends messages to linkedin through the unipile API. If you have to send a message, ALWAYS make sure you have written a well thought out dutch, hyper personalised message. When the message is finished, you will send this EXACT message word for word to the person on linkedin by using this tool.
)
    
    Let's work this out in a step by step way to be sure we have the right answer. """,
    tools=[linkedin_message_tool],
    verbose=True,
    allow_delegation=False,
    memory=True,
    llm=ChatOpenAI(model="gpt-4-turbo")
)


# Function to create tasks dynamically based on a user query
def create_task_admin(query, agent, tools):
    description = f"Generate a very detailed, step by step plan based on the users {query} for the other agents to follow. Detailing what should be done and explicitly what tools should be used."
    return Task(
        description=description,
        tools=tools,
        agent=admin_agent,
        expected_output="A very detailed step by step plan for the other agents on what to do and what tools to use based on the users query."
    )

def create_task_data(query, agent, tools):
    description = f"Based on the users {query} and the tasks from the 'admin_agent' take actions and use tools to succesfully achieve these tasks."
    return Task(
        description=description,
        tools=tools,
        agent=data_agent,
        expected_output="Data scraped and/or data sent. Based on what is being asked."
    )

def create_task_writing(query, agent, tools):
    description = f"Based on the users {query} and the tasks from the admin_agent and the scraped data, write and/or send a personalised message."
    return Task(
        description=description,
        tools=tools,
        agent=writing_agent,
        expected_output="Written message that should be send or not, based on the users needs."
    )

# User query input
user_query = input("Please enter your query:")

# Dynamic task creation and delegation in the crew setup
task1 = create_task_admin(user_query, admin_agent, [unipile_tool, zapier_webhook_tool, linkedin_message_tool]) 
task2 = create_task_data(user_query, data_agent, [unipile_tool, zapier_webhook_tool, linkedin_message_tool])
task3 = create_task_writing(user_query, writing_agent, [unipile_tool, zapier_webhook_tool, linkedin_message_tool]) 

crew = Crew(
    agents=[admin_agent, writing_agent, data_agent],
    tasks=[task1, task2, task3],
    process='hierarchical',  # Using hierarchical process for task delegation
    manager_llm=ChatOpenAI(model="gpt-4-turbo")
)

# Execute the crew's tasks and print the results
result = crew.kickoff()
print(result)