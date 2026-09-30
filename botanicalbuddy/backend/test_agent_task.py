from crewai import Agent, Task

# Try instantiating an Agent
agent = Agent(
    role="Test Agent",
    goal="Say hello.",
    backstory="A simple test agent.",
    verbose=True,
    allow_delegation=False,
    llm_config={"model": "gemini/gemini-pro"}
)

print(f"Agent object: {agent}")
print(f"Agent name: {agent.role}")

# Try instantiating a Task with the Agent
task = Task(description="Say hello.", agent=agent,
expected_output="A greeting message")

print(f"Task object: {task}")
print(f"Task description: {task.description}")
print(f"Task agent: {task.agent}")