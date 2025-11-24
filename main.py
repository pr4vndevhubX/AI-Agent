from typing import List, Dict
from crewai import Agent,Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import SerperDevTool, ScrapeWebsiteTool, DirectoryReadTool, FileWriterTool, FileReadTool
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()


llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.7,
)


# -------------------------------
# Pydantic Models for Task Outputs
# -------------------------------


class Content(BaseModel):
    content_type: str = Field(..., description="The type of content to be created (e.g., blog post, social media post, reel script)")
    topic: str = Field(..., description="The topic of the content")
    target_audience: str = Field(..., description="The target audience for the content")
    tags: List[str] = Field(..., description="Tags to be used for the content")
    content: str = Field(..., description="The content itself")
    file_path: str = Field(..., description="The location where the content is saved")


class MarketResearchOutput(BaseModel):
    market_trends: List[str]
    competitor_analysis: Dict[str, str]
    customer_insights: Dict[str, str]
    recommendations: List[str]
    file_path: str = Field(..., description="Location of the market research report")


class MarketingStrategyOutput(BaseModel):
    target_audience_segments: List[str]
    marketing_channels: List[str]
    weekly_plan: Dict[str, List[str]]
    budget_allocation: float
    kpis: Dict[str, str]
    file_path: str = Field(..., description="Location of the marketing strategy document")


class ContentCalendarOutput(BaseModel):
    topics_formats: Dict[str, str]
    publishing_schedule: Dict[str, str]
    key_campaigns: List[str]
    calendar_file_path: str = Field(..., description="Location of the content calendar file")


class PostDraftsOutput(BaseModel):
    social_media_posts: Dict[str, str]
    email_campaigns: Dict[str, str]
    drafts_file_path: str = Field(..., description="Location of the drafted posts")


class ScriptReelsShortsOutput(BaseModel):
    scripts: Dict[str, str]
    file_path: str = Field(..., description="Location of the scripts for reels and shorts")


class ContentResearchBlogOutput(BaseModel):
    topics: List[str]
    supporting_data: Dict[str, str]
    keywords: List[str]
    research_file_path: str = Field(..., description="Location of blog research report")


class DraftBlogsOutput(BaseModel):
    blog_titles: List[str]
    blog_content: Dict[str, str]
    draft_file_path: str = Field(..., description="Location of drafted blog files")


class SEOOptimizationOutput(BaseModel):
    optimized_content: Dict[str, str]
    keywords_used: List[str]
    seo_score: Dict[str, int]
    file_path: str = Field(..., description="Location of SEO optimized content")

@CrewBase

class TheMarketingCrew():
    "The marketing crew is responsible for creating and executing marketing startegies"
    agents_config = 'config/agent.yaml'
    tasks_config = 'config/task.yaml'


    @agent
    def head_of_marketing(self) -> Agent:
        return Agent(
            config=self.agents_config['head_of_marketing'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool(),
            ],
            llm=llm,
            reasoning=True,
            inject_data=True,
            verbose=True,
            allow_delegation=True,
            max_rpm=3
        )
    
    @agent
    def content_creator_social_media(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator_social_media'],
            tools=[
                SerperDevTool(),               # For quick trend search
                ScrapeWebsiteTool(),           # For gathering content inspiration
                DirectoryReadTool('resources/drafts'),  # Access drafts and content calendar
                FileWriterTool(),              # Save created posts or media scripts
                FileReadTool()                # Read instructions, drafts, or scripts            
            ],
            llm=llm,
            reasoning=True,
            inject_data=True,
            verbose=True,
            allow_delegation=True,
            max_iter=30,
            max_rpm=5
        )
    
    @agent
    def content_writer_blogs(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer_blogs'],
            tools=[
                SerperDevTool(),               # Research blog topics and data
                DirectoryReadTool('resources/research'),  # Access blog research data
                DirectoryReadTool('resources/drafts'),   # Access prior drafts
                FileWriterTool(),              # Save blog drafts
                FileReadTool()                # Read research, guidelines, or instructions
            ],
            llm=llm,
            reasoning=True,
            inject_data=True,
            verbose=True,
            allow_delegation=True,
            max_iter=5,
            max_rpm=4
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],
            tools=[
                SerperDevTool(),                 # Keyword and SEO research
                DirectoryReadTool('resources/drafts'),   # Read content to optimize
                FileWriterTool(),                # Save optimized content
                FileReadTool(),                  # Read content drafts
            ],
            llm=llm,
            reasoning=True,
            inject_data=True,
            verbose=True,
            allow_delegation=True,
            max_iter=3,
            max_rpm=3
        )
    
    @task
    def market_research(self) -> Task:
        return Task(
            config=self.tasks_config['market_research'],
            agent=self.head_of_marketing(),
            output_json=MarketResearchOutput
        )

    @task
    def marketing_strategy(self) -> Task:
        return Task(
            config=self.tasks_config['marketing_strategy'],
            agent=self.head_of_marketing(),
            output_json=MarketingStrategyOutput
        )

    @task
    def content_calendar(self) -> Task:
        return Task(
            config=self.tasks_config['content_calendar'],
            agent=self.content_creator_social_media(),
            output_json=ContentCalendarOutput
        )

    @task
    def prepare_post_drafts(self) -> Task:
        return Task(
            config=self.tasks_config['post_draft'],
            agent=self.content_creator_social_media(),
            output_json=PostDraftsOutput
        )

    @task
    def script_reels_shorts(self) -> Task:
        return Task(
            config=self.tasks_config['script_reels_shorts'],
            agent=self.content_creator_social_media(),
            output_json=ScriptReelsShortsOutput
        )

    @task
    def content_research_blog(self) -> Task:
        return Task(
            config=self.tasks_config['content_research_blog'],
            agent=self.content_writer_blogs(),
            output_json=ContentResearchBlogOutput
        )

    @task
    def draft_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['draft_blogs'],
            agent=self.content_writer_blogs(),
            output_json=DraftBlogsOutput
        )

    @task
    def seo_optimization(self) -> Task:
        return Task(
            config=self.tasks_config['seo_optimization'],
            agent=self.seo_specialist(),
            output_json=SEOOptimizationOutput,
            structured_output=True
        )
    
    @crew
    def marketingcrew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            Process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=llm,
            max_rpm=3
        )

if __name__ == "__main__":
    from datetime import datetime

    inputs = {
        "product_name": "AI Powered Excel Automation Tool",
        "target_audience": "Small and Medium Enterprises(SMs)",
        "product_description": "A tool that automates repetitive tasks in Excel using AI",
        "budget": "Rs. 50,000",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }

    crew = TheMarketingCrew()
    crew.marketingcrew().kickoff(inputs=inputs)
    print("Marketing crew has been successfully created and run.")
    



    


        
            