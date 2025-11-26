from typing import List, Dict
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, DirectoryReadTool, FileWriterTool, FileReadTool
from pydantic import BaseModel, Field
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()


# Configure LLM with OpenRouter (Free models)
llm = LLM(
    model="openrouter/x-ai/grok-4.1-fast",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.7,
    timeout=180
)

fallback_llm = LLM(
    model="openrouter/meta-llama/llama-3.1-8b-instruct:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.7,
    timeout=180
)


# -------------------------------
# Helper Functions
# -------------------------------

def get_llm_with_fallback():
    """Returns LLM with automatic fallback"""
    try:
        return llm
    except:
        print("⚠️ Primary LLM failed, using fallback...")
        return fallback_llm


def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'resources/research',
        'resources/drafts/posts',
        'resources/drafts/reels',
        'resources/drafts/blogs',
        'resources/seo_optimized'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ All required directories have been created/verified.")


# -------------------------------
# Pydantic Models for Task Outputs
# -------------------------------

class MarketResearchOutput(BaseModel):
    market_trends: List[str] = Field(..., description="List of key market trends")
    competitor_analysis: Dict[str, str] = Field(..., description="Analysis of competitors")
    customer_insights: Dict[str, str] = Field(..., description="Customer pain points and preferences")
    recommendations: List[str] = Field(..., description="Strategic recommendations")
    file_path: str = Field(..., description="Location of the market research report")


class MarketingStrategyOutput(BaseModel):
    target_audience_segments: List[str] = Field(..., description="Segmented target audiences")
    marketing_channels: List[str] = Field(..., description="Marketing channels to use")
    weekly_plan: Dict[str, List[str]] = Field(..., description="Weekly content plan")
    budget_allocation: float = Field(..., description="Budget allocation amount")
    kpis: Dict[str, str] = Field(..., description="Key performance indicators")
    file_path: str = Field(..., description="Location of the marketing strategy document")


class ContentCalendarOutput(BaseModel):
    topics_formats: Dict[str, str] = Field(..., description="Content topics and formats")
    publishing_schedule: Dict[str, str] = Field(..., description="Publishing schedule")
    key_campaigns: List[str] = Field(..., description="Key marketing campaigns")
    calendar_file_path: str = Field(..., description="Location of the content calendar file")


class PostDraftsOutput(BaseModel):
    social_media_posts: Dict[str, str] = Field(..., description="Social media post drafts")
    email_campaigns: Dict[str, str] = Field(..., description="Email campaign drafts")
    drafts_file_path: str = Field(..., description="Location of the drafted posts")


class ScriptReelsShortsOutput(BaseModel):
    scripts: Dict[str, str] = Field(..., description="Video scripts for reels and shorts")
    file_path: str = Field(..., description="Location of the scripts for reels and shorts")


class ContentResearchBlogOutput(BaseModel):
    topics: List[str] = Field(..., description="Blog topics")
    supporting_data: Dict[str, str] = Field(..., description="Supporting data for topics")
    keywords: List[str] = Field(..., description="SEO keywords")
    research_file_path: str = Field(..., description="Location of blog research report")


class DraftBlogsOutput(BaseModel):
    blog_titles: List[str] = Field(..., description="Blog post titles")
    blog_content: Dict[str, str] = Field(..., description="Full blog content")
    draft_file_path: str = Field(..., description="Location of drafted blog files")


class SEOOptimizationOutput(BaseModel):
    optimized_content: Dict[str, str] = Field(..., description="SEO optimized content")
    keywords_used: List[str] = Field(..., description="Keywords used")
    seo_score: Dict[str, int] = Field(..., description="SEO scores")
    file_path: str = Field(..., description="Location of SEO optimized content")


# -------------------------------
# Marketing Crew Definition
# -------------------------------

@CrewBase
class TheMarketingCrew():
    """The marketing crew is responsible for creating and executing marketing strategies"""
    
    agents_config = 'config/agent.yaml'
    tasks_config = 'config/task.yaml'

    @agent
    def head_of_marketing(self) -> Agent:
        return Agent(
            config=self.agents_config['head_of_marketing'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(timeout=30),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool(),
            ],
            llm=get_llm_with_fallback(),
            reasoning=False,
            inject_data=True,
            verbose=True,
            allow_delegation=False,  # Simplified
            max_iter=20,  # Increased for completion
            max_rpm=20,
            respect_context_window=True
        )
    
    @agent
    def content_creator_social_media(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator_social_media'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(timeout=30),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            llm=get_llm_with_fallback(),
            reasoning=False,
            inject_data=True,
            verbose=True,
            allow_delegation=False,  # Simplified
            max_iter=15,  # Increased
            max_rpm=20,
            respect_context_window=True
        )
    
    @agent
    def content_writer_blogs(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer_blogs'],
            tools=[
                SerperDevTool(),
                DirectoryReadTool('resources/research'),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            llm=get_llm_with_fallback(),
            reasoning=False,
            inject_data=True,
            verbose=True,
            allow_delegation=False,  # Simplified
            max_iter=15,  # Increased
            max_rpm=20,
            respect_context_window=True
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],
            tools=[
                SerperDevTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool(),
            ],
            llm=get_llm_with_fallback(),
            reasoning=False,
            inject_data=True,
            verbose=True,
            allow_delegation=False,  # Simplified
            max_iter=15,  # Increased
            max_rpm=20,
            respect_context_window=True
        )
    
    # -------------------------------
    # Task Definitions
    # -------------------------------
    
    @task
    def market_research(self) -> Task:
        return Task(
            config=self.tasks_config['market_research'],
            agent=self.head_of_marketing(),
            # output_json=MarketResearchOutput,  # Removed for stability
            context=[],
        )

    @task
    def marketing_strategy(self) -> Task:
        return Task(
            config=self.tasks_config['marketing_strategy'],
            agent=self.head_of_marketing(),
            # output_json=MarketingStrategyOutput,  # Removed for stability
            context=[self.market_research()],
        )

    @task
    def content_calendar(self) -> Task:
        return Task(
            config=self.tasks_config['content_calendar'],
            agent=self.content_creator_social_media(),
            # output_json=ContentCalendarOutput,  # Removed for stability
            context=[self.marketing_strategy()],
        )

    @task
    def prepare_post_drafts(self) -> Task:
        return Task(
            config=self.tasks_config['post_draft'],
            agent=self.content_creator_social_media(),
            # output_json=PostDraftsOutput,  # Removed for stability
            context=[self.content_calendar()],
        )

    @task
    def script_reels_shorts(self) -> Task:
        return Task(
            config=self.tasks_config['script_reels_shorts'],
            agent=self.content_creator_social_media(),
            # output_json=ScriptReelsShortsOutput,  # Removed for stability
            context=[self.content_calendar()],
        )

    @task
    def content_research_blog(self) -> Task:
        return Task(
            config=self.tasks_config['content_research_blog'],
            agent=self.content_writer_blogs(),
            # output_json=ContentResearchBlogOutput,  # Removed for stability
            context=[self.marketing_strategy()],
        )

    @task
    def draft_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['draft_blogs'],
            agent=self.content_writer_blogs(),
            # output_json=DraftBlogsOutput,  # Removed for stability
            context=[self.content_research_blog()],
        )

    @task
    def seo_optimization(self) -> Task:
        return Task(
            config=self.tasks_config['seo_optimization'],
            agent=self.seo_specialist(),
            # output_json=SEOOptimizationOutput,  # Removed for stability
            context=[self.draft_blogs()],
        )
    
    @crew
    def marketingcrew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=False,
            max_rpm=20,  # Increased
            memory=False,
            cache=True,
            full_output=True,
        )


# -------------------------------
# Main Execution
# -------------------------------

def main():
    """Main execution function with error handling"""
    
    print("=" * 80)
    print("🚀 MARKETING CREW - AI-POWERED MARKETING AUTOMATION")
    print("=" * 80)
    
    # Setup directories
    setup_directories()
    
    # Define inputs
    inputs = {
        "product_name": "AI Powered Excel Automation Tool",
        "target_audience": "Small and Medium Enterprises (SMEs)",
        "product_description": "A tool that automates repetitive tasks in Excel using AI",
        "budget": "Rs. 50,000",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }
    
    print("\n📋 Project Configuration:")
    print(f"   Product: {inputs['product_name']}")
    print(f"   Target Audience: {inputs['target_audience']}")
    print(f"   Budget: {inputs['budget']}")
    print(f"   Date: {inputs['current_date']}")
    print("\n" + "=" * 80)
    
    try:
        # Initialize crew
        print("\n🔧 Initializing Marketing Crew...")
        crew = TheMarketingCrew()
        
        # Execute crew
        print("\n▶️  Starting crew execution...\n")
        result = crew.marketingcrew().kickoff(inputs=inputs)
        
        # Display results
        print("\n" + "=" * 80)
        print("✅ MARKETING CREW EXECUTION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        print("\n📊 Results Summary:")
        print(f"   Tasks Completed: {len(crew.tasks)}")
        print(f"   Output Files Generated: Check 'resources/' directory")
        
        print("\n📁 Generated Files:")
        print("   • resources/research/market_research_report.md")
        print("   • resources/research/marketing_strategy.json")
        print("   • resources/drafts/content_calendar.md")
        print("   • resources/drafts/posts/draft_posts.json")
        print("   • resources/drafts/reels/scripts.json")
        print("   • resources/research/blog_research.md")
        print("   • resources/drafts/blogs/draft_blogs.json")
        print("   • resources/seo_optimized/seo_content.json")
        
        print("\n" + "=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n⚠️ Primary execution failed: {e}")
        print("🔄 Attempting with fallback LLM...\n")
        
        try:
            # Retry with fallback by reinitializing
            global llm
            llm = fallback_llm
            
            crew = TheMarketingCrew()
            result = crew.marketingcrew().kickoff(inputs=inputs)
            
            print("\n" + "=" * 80)
            print("✅ COMPLETED WITH FALLBACK LLM!")
            print("=" * 80)
            return result
            
        except Exception as fallback_error:
            print("\n" + "=" * 80)
            print("❌ ERROR OCCURRED EVEN WITH FALLBACK")
            print("=" * 80)
            print(f"\nError Type: {type(fallback_error).__name__}")
            print(f"Error Message: {str(fallback_error)}")
            print("\n💡 Troubleshooting Tips:")
            print("   1. Check if Gemini API key is valid in .env file")
            print("   2. Verify Serper API key is set correctly")
            print("   3. Ensure stable internet connection")
            print("   4. Try waiting a few minutes if rate limited")
            print("   5. Check Gemini API status: https://status.cloud.google.com/")
            print("\n" + "=" * 80)
            
            # Save error log
            with open('error_log.txt', 'w') as f:
                f.write(f"Error Type: {type(fallback_error).__name__}\n")
                f.write(f"Error Message: {str(fallback_error)}\n")
                f.write(f"Timestamp: {datetime.now()}\n")
            
            print("\n📝 Error details saved to 'error_log.txt'")
            return None


if __name__ == "__main__":
    result = main()
    
    if result:
        print("\n🎉 All tasks completed successfully!")
        print("📦 Check the 'resources' folder for all generated content.")
    else:
        print("\n⚠️  Execution did not complete successfully.")
        print("📝 Check error_log.txt for details.")