# SEO Brief Automator (Refactored)

A step-by-step AI-powered content brief generator for finance professionals, built with Flask and OpenAI.

## Features

### Step-by-Step Workflow
1. **SERP Collection**: Automatically scrape top 10 Google search results using Selenium
2. **UGC Research**: Generate user-generated content brief using customizable prompts
3. **SERP Analysis**: Analyze scraped URLs with structured content analysis
4. **Final Output**: Combine all research into downloadable brief files

### Key Features
- **Automated Prompt Population**: User inputs from Step 1 automatically populate prompts in subsequent steps
- **Editable Prompts**: Customize UGC and SERP analysis prompts as needed
- **Real-time Progress**: Live status updates for each step
- **API Request Limiting**: Built-in protection against OpenAI API quota limits
- **Downloadable Results**: JSON and HTML output formats

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key in `config/config.py`
4. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. **Step 1**: Enter your focus keyword, topic/theme, buyer persona, and content ID
2. **Step 2**: Review/edit the UGC prompt (auto-populated with your inputs) and generate UGC brief
3. **Step 3**: Review/edit the SERP analysis prompt (includes scraped URLs) and generate SERP brief
4. **Step 4**: Download the combined final brief

## Project Structure

```
seo-brief-automator/
├── app.py                 # Main Flask application (refactored)
├── templates/
│   └── index.html        # Main UI template (refactored)
├── src/
│   ├── serp_scraper.py   # Selenium-based SERP scraping
│   ├── ugc_researcher.py # UGC research and AI analysis
│   ├── brief_generator.py # Brief generation and file output
│   └── ...
├── config/
│   └── config.py         # Configuration settings
├── output/               # Generated brief files
└── requirements.txt      # Python dependencies
```

## API Endpoints

- `GET /` - Main application interface
- `POST /start-step1` - Start SERP collection
- `POST /start-step2` - Start UGC research
- `POST /start-step3` - Start SERP analysis
- `POST /start-step4` - Combine and generate final brief
- `GET /status` - Get current job status
- `GET /download/<filename>` - Download generated files

## Configuration

Update `config/config.py` with your OpenAI API key:
```python
OPENAI_API_KEY = "your-openai-api-key-here"
```

## Dependencies

- Flask
- OpenAI
- Selenium
- BeautifulSoup
- Requests
- WebDriver Manager

## License

MIT License 