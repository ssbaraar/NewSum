# Learning Implantation 1

Welcome to Learning Implantation 1, a demonstration project designed to explore and showcase the integration of asynchronous data fetching, RSS feed parsing, OpenAI summarization, and a lightweight backend service using Python and Sanic. This project extracts articles from various environmental and tech-oriented news sources, uses OpenAI's language model to summarize them, and allows you to personalize and filter content according to your interests.

## Table of Contents
1. [Introduction](#introduction)
2. [Tech Stack and Key Libraries](#tech-stack-and-key-libraries)
3. [Features](#features)
4. [Use Cases](#use-cases)
5. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Environment Variables](#environment-variables)
6. [Project Structure](#project-structure)
7. [API Endpoints](#api-endpoints)
8. [URL Redirects](#url-redirects)
   - [Permanent Redirects](#permanent-redirects)
   - [Temporary Redirects](#temporary-redirects)
   - [Custom Redirects](#custom-redirects)
9. [Learnings and Insights](#learnings-and-insights)
10. [Future Improvements](#future-improvements)

## Introduction

In this project, we aim to push the boundaries of data ingestion, transformation, and presentation. It's not just another RSS aggregator; rather, it's an intelligent assistant that filters and summarizes large volumes of textual content from multiple online sources. This helps you quickly grasp key insights, discover trends, and deepen your understanding of the sustainability and tech landscapes—all in a fraction of the time it would take to read every article manually.

## Tech Stack and Key Libraries

- **Programming Language**: Python
- **Framework**: Sanic for fast, asynchronous Python web servers
- **Async HTTP Client**: aiohttp for non-blocking requests
- **RSS Feed Parsing**: feedparser for easy RSS/Atom feed parsing
- **HTML Parsing**: BeautifulSoup for HTML content extraction
- **Environment Management**: python-dotenv for loading environment variables
- **Date Parsing**: dateutil for robust date/time handling
- **OpenAI Integration**: OpenAI Python Library to generate summaries using GPT-based models

## Features

1. **Multiple News Source Integration**: Aggregates content from various sustainability and technology-focused RSS feeds.
2. **Intelligent Summarization**: Utilizes OpenAI's GPT-3.5-Turbo model to summarize articles into concise 2-3 sentence overviews.
3. **Customizable Filtering**: Personalize your reading experience by selecting preferred sources and keywords to filter relevant content.
4. **'Read Later' Functionality**: Save articles for future reading directly from the API endpoints.
5. **Asynchronous Operations**: Harnesses async/await patterns to simultaneously fetch multiple feeds, significantly improving performance and reducing wait times.

## Use Cases

- **Sustainability Insights Portal**: Businesses or NGOs focused on sustainability can quickly scan relevant industry news to make informed decisions.
- **Research Aggregator for Students and Academics**: Students and researchers can streamline their literature review process by filtering and summarizing articles from various reliable sources.
- **Executive Briefing Services**: Curate a personalized, keyword-focused briefing that keeps stakeholders informed about emerging trends without requiring them to read full-length articles.
- **Competitive Intelligence and Market Analysis**: Organizations can track competitor news, emerging technologies, and industry shifts, all summarized in a few digestible sentences.

## Getting Started

### Prerequisites
- Python 3.7+
- A valid OpenAI API Key
- Basic understanding of Python and async I/O operations.

### Installation

1. Clone the Repository:
```bash
git clone https://github.com/yourusername/learning-implantation-1.git
cd learning-implantation-1
```

2. Create a Virtual Environment (optional but recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file at the project root with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
REDIRECT_CONFIG=path/to/redirects.json  # Add this for redirect configuration
```

Make sure not to commit this file to version control for security reasons.

## Project Structure

```
.
├── app.py             # The main Sanic application and route definitions
├── data.json          # JSON file containing articles, preferences, and read-later items
├── redirects.json     # Configuration file for URL redirects
├── templates/         # Directory for templates (if you integrate HTML front-ends)
├── .env               # Environment variables (not tracked by git)
├── .venv/             # Virtual environment files (optional)
├── requirements.txt   # Python dependencies
└── (other database and configuration files)
```

## API Endpoints

- **GET /**
  - Returns filtered articles based on current preferences (sources & keywords).
- **POST /save_preferences**
  - Updates your preferred sources and keywords and triggers a fresh scrape.
- **GET /all_articles**
  - Retrieves all articles filtered by your chosen sources and keywords.
- **GET /read_later**
  - Returns the list of articles you've saved for future reading.
- **POST /add_to_read_later**
  - Adds a specific article to your "read later" list.
- **POST /remove_from_read_later**
  - Removes a specific article from your "read later" list.

## URL Redirects

The project includes a flexible URL redirection system to handle various routing scenarios. Configure redirects in the `redirects.json` file.

### Permanent Redirects (301)
```json
{
  "permanent": {
    "/old-articles": "/all_articles",
    "/preferences": "/save_preferences",
    "/archive/*": "/read_later"
  }
}
```

### Temporary Redirects (302)
```json
{
  "temporary": {
    "/beta/*": "/experimental/*",
    "/latest": "/all_articles?sort=date",
    "/trending": "/all_articles?sort=popularity"
  }
}
```

### Custom Redirects

You can implement custom redirect logic in `app.py`:

```python
@app.route('/redirect/<path:path>')
async def custom_redirect(request, path):
    redirect_map = {
        'tech': '/all_articles?category=technology',
        'env': '/all_articles?category=environment',
        'saved': '/read_later'
    }
    return redirect(redirect_map.get(path, '/'))
```

To implement redirects:

1. Create a `redirects.json` file:
```json
{
  "permanent": {
    "/old-path": "/new-path"
  },
  "temporary": {
    "/temp-path": "/current-path"
  }
}
```

2. Add the middleware in `app.py`:
```python
@app.middleware('request')
async def handle_redirects(request):
    path = request.path
    if path in redirects['permanent']:
        return redirect(redirects['permanent'][path], status=301)
    if path in redirects['temporary']:
        return redirect(redirects['temporary'][path], status=302)
```

## Learnings and Insights

This project is not only about code—it's about understanding the ecosystem of content aggregation and the importance of concise information. By integrating OpenAI's language model, we learned how to transform long-form journalism into executive summaries that facilitate quicker decision-making. Additionally, through asynchronous data fetching, we've explored how modern web frameworks like Sanic can handle multiple I/O-bound tasks concurrently, improving scalability and responsiveness.

## Future Improvements

- **Enhanced Front-End**: Integrate a sleek UI to interact with the backend and visualize summaries and filters more intuitively.
- **Extended Personalization**: Allow more granular user preferences, including scoring algorithms to rank articles by relevance.
- **Caching and Performance Optimization**: Implement caching strategies to reduce the load on external APIs and improve response times.
- **Enhanced Summarization**: Experiment with different summarization prompts and models for higher accuracy and relevance.
- **Advanced Redirect Management**: Implement a UI for managing redirects and support for regex patterns in redirect rules.

If you have any questions, need clarifications, or suggestions for improvement, feel free to ask!
