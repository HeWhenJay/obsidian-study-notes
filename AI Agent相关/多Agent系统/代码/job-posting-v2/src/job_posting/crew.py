from typing import List
from crewai import Agent, Crew, Process, Task, LLM ##
from crewai.project import CrewBase, agent, crew, task

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, FileReadTool
from pydantic import BaseModel, Field
##
import os
from dotenv import load_dotenv
load_dotenv()

llm = LLM(
    model="openai/qwen-max",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

web_search_tool = WebsiteSearchTool()
seper_dev_tool = SerperDevTool()
file_read_tool = FileReadTool(
    file_path='job_description_example.md',
    description='读取职位描述示例文件的工具'
)

class ResearchRoleRequirements(BaseModel):
    """Research role requirements model"""
    skills: List[str] = Field(..., description="列出符合公司文化、正在进行的项目和特定职位要求的理想候选人所应具备的技能。")
    experience: List[str] = Field(..., description="列出符合公司文化、正在进行的项目以及具体职位要求的理想候选人的推荐经验。")
    qualities: List[str] = Field(..., description="列出符合公司文化、正在进行的项目以及具体职位要求的理想候选人所应具备的素质。")


@CrewBase
class JobPostingCrew:
    """JobPosting crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            tools=[web_search_tool, seper_dev_tool],
            verbose=True,
            llm=llm ##
        )
    
    @agent
    def writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['writer_agent'],
            tools=[web_search_tool, seper_dev_tool, file_read_tool],
            verbose=True,
            llm=llm ##
        )
    
    @agent
    def review_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['review_agent'],
            tools=[web_search_tool, seper_dev_tool, file_read_tool],
            verbose=True,
            llm=llm ##
        )


    @task
    def research_company_culture_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_company_culture_task'],
            agent=self.research_agent()
        )

    @task
    def industry_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['industry_analysis_task'],
            agent=self.research_agent()
        )

    @task
    def research_role_requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_role_requirements_task'],
            agent=self.research_agent(),
            output_json=ResearchRoleRequirements
        )

    @task
    def draft_job_posting_task(self) -> Task:
        return Task(
            config=self.tasks_config['draft_job_posting_task'],
            agent=self.writer_agent()
        )

    @task
    def review_and_edit_job_posting_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_and_edit_job_posting_task'],
            agent=self.review_agent()
        )



    @crew
    def crew(self) -> Crew:
        """Creates the JobPostingCrew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True, ##
        )