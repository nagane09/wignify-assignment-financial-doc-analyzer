FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install PyPDF2

COPY requirements.txt .

# Install safe dependencies
RUN grep -v -E 'crewai|crewai-tools|embedchain|gptcache|alembic|mako|schema|pysbd|langchain-openai|docker|beautifulsoup4|langchain-google-genai' requirements.txt > requirements_base.txt \
    && pip install --no-cache-dir -r requirements_base.txt

# Install CrewAI core
RUN pip install --no-cache-dir crewai==0.130.0

# Force install final conflicting deps (no dependency resolution)
RUN pip install --no-cache-dir --no-deps crewai-tools==0.47.1 \
    && pip install --no-cache-dir --no-deps embedchain==0.1.114 \
    && pip install --no-cache-dir --no-deps gptcache==0.1.44 \
    && pip install --no-cache-dir --no-deps alembic==1.13.1 \
    && pip install --no-cache-dir --no-deps schema==0.7.5 \
    && pip install --no-cache-dir mako==1.3.2 \
    && pip install --no-cache-dir pysbd==0.3.4 \
    && pip install --no-cache-dir langchain-openai==0.1.7 \
    && pip install --no-cache-dir docker==7.1.0 \
    && pip install --no-cache-dir beautifulsoup4==4.12.3 \
    && pip install --no-cache-dir langchain-google-genai==0.0.11

COPY . .

RUN mkdir -p data

EXPOSE 8000
