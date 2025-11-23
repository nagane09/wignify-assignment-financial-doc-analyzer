## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent

# Properly instantiate the CrewAI professional agents
try:
    financial_analyst = Agent(name="FinancialAnalyst")
    investment_advisor = Agent(name="InvestmentAdvisor")
    risk_assessor = Agent(name="RiskAssessor")
    verifier = Agent(name="Verifier")
except Exception as e:
    print(f"Error initializing CrewAI agents: {e}")
    # Fallback to None if initialization fails
    financial_analyst = None
    investment_advisor = None
    risk_assessor = None
    verifier = None
