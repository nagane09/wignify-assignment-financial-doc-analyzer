## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai_tools.tools.serper_dev_tool import SerperDevTool

## Creating search tool (Still useful as a standalone tool instance)
search_tool = SerperDevTool()