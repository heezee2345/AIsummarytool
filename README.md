# AI English Summary Assistant for Teachers

**An intelligent summarization tool for Korean high school English teachers**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Project Overview

This tool is an AI-powered English text summarization support system designed specifically for **Korean high school English teachers**. It assists teachers in creating summaries of English passages from CSAT exams, mock tests, and textbooks, while providing curriculum-aligned feedback.

## Key Features

### Curriculum-Aligned Analysis
- **Grade 10**: 2022 Revised National Curriculum standards
- **Grades 11-12**: 2015 Revised National Curriculum standards
- Automatic vocabulary level adjustment by grade

### AI-Powered Feedback System
- GPT-4 based intelligent summary analysis
- Personalized feedback based on curriculum standards
- Comparative analysis with AI-generated model summaries

### Real-time Vocabulary Assessment
- Analysis based on Korea's Ministry of Education Basic Vocabulary (7,000 words)
- Grade-appropriate vocabulary level evaluation
- Identification of challenging vocabulary items

### Specialized for Korean Education
- Optimized for CSAT, mock exam, and EBS textbook passages
- Korean educational context integration
- Teacher workflow optimization

## Technical Architecture

### Core Components

1. **main_app.py** - Main Streamlit application interface
2. **ai_services.py** - OpenAI GPT integration and AI services
3. **vocabulary_loader.py** - Ministry of Education vocabulary processing
4. **sheets_service.py** - Google Sheets integration for data collection
5. **data_config.py** - Configuration and survey questions
6. **utils.py** - Utility functions

### Data Collection
- **TAM (Technology Acceptance Model)** based survey system
- Real-time data storage in Google Sheets
- Anonymous participant tracking
- Research ethics compliant data handling

## Installation and Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Google Cloud Platform account (for Google Sheets integration)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/your-username/ai-english-summary-tool.git
cd ai-english-summary-tool
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create `.streamlit/secrets.toml`:
```toml
[openai]
api_key = "your-openai-api-key"

[gcp_service_account]
type = "service_account"
project_id = "your-gcp-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"

[google_sheets]
spreadsheet_id = "your-google-spreadsheet-id"
```

4. **Run the application**
```bash
streamlit run main_app.py
```

### Cloud Deployment (Streamlit Community Cloud)

1. **Fork this repository** to your GitHub account

2. **Set up Google Cloud Platform**
   - Create a new GCP project
   - Enable Google Sheets API and Google Drive API
   - Create a service account and download JSON credentials
   - Create a Google Spreadsheet and share it with the service account

3. **Deploy to Streamlit Community Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Add secrets in App Settings > Secrets (use the same format as above)

4. **Configure the application**
   - Set up OpenAI API key in Streamlit secrets
   - Configure Google Cloud credentials
   - Test the deployment

## Usage Guide

### For Teachers

1. **Teacher Information Input**
   - Enter teaching grade level, school type, and experience
   - Input English passage text
   - Specify source type and curriculum standards

2. **Summary Creation**
   - Write a 15-20 word summary of the passage
   - Review AI-extracted keywords for guidance
   - Receive real-time word count feedback

3. **AI Analysis and Feedback**
   - Compare your summary with AI-generated model summary
   - Receive curriculum-aligned feedback
   - Review vocabulary level analysis

4. **Research Participation (Optional)**
   - Complete TAM-based survey questionnaire
   - Contribute to educational AI tool research

### For Researchers

- Access collected survey data through Google Sheets
- Monitor usage statistics and user feedback
- Analyze teacher acceptance of AI educational tools

## Data and Privacy

### Data Collection
- **Teacher Information**: Grade level, school type, teaching experience (anonymized)
- **Usage Data**: Summary completion, feedback interaction, vocabulary analysis usage
- **Survey Responses**: TAM questionnaire responses for research purposes
- **Text Data**: Input passages and summaries (not permanently stored)

### Privacy Protection
- All participant data is anonymized with unique IDs
- No personally identifiable information is collected
- Data is used solely for academic research purposes
- Participants can withdraw from the study at any time

## Research Context

This tool is part of a research study investigating:
- Korean English teachers' acceptance of AI educational tools
- Effectiveness of AI-assisted summary writing instruction
- Impact of curriculum-aligned AI feedback on teaching practices

**Research Framework**: Technology Acceptance Model (TAM)
**Target Population**: Korean high school English teachers
**Study Focus**: AI tool adoption in English education

## Technical Dependencies

```
streamlit==1.28.0
openai==1.3.0
gspread==5.12.0
google-auth==2.23.0
google-auth-oauthlib==1.0.0
google-auth-httplib2==0.1.1
```

## File Structure

```
ai-english-summary-tool/
├── main_app.py                 # Main Streamlit application
├── ai_services.py             # OpenAI integration and AI services
├── vocabulary_loader.py       # Vocabulary processing and analysis
├── sheets_service.py          # Google Sheets data collection
├── data_config.py            # Configuration and survey questions
├── utils.py                  # Utility functions
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
└── data/
    └── moe_basic_vocabulary.txt  # Ministry of Education vocabulary list
```

## Configuration Options

### Streamlit Secrets Configuration

**Required Settings:**
- `openai.api_key`: OpenAI API key for GPT services
- `gcp_service_account`: Google Cloud service account credentials
- `google_sheets.spreadsheet_id`: Target Google Spreadsheet ID

**Optional Settings:**
- `debug_mode`: Enable detailed error logging (default: false)
- `show_admin_stats`: Display usage statistics (default: false)
- `show_admin_panel`: Show admin controls (default: false)

## API Integration

### OpenAI GPT-4 Integration
- **Keyword Extraction**: Identifies key terms from English passages
- **Summary Generation**: Creates model summaries for comparison
- **Feedback Provision**: Generates curriculum-aligned feedback
- **Translation Services**: Provides Korean translations for keywords

### Google Sheets Integration
- **Automatic Data Storage**: Real-time survey response collection
- **Participant Tracking**: Anonymous ID generation and management
- **Research Data Export**: Easy access to collected research data
- **Backup Systems**: Redundant data storage for reliability

## Contributing

### Development Guidelines
1. Follow Python PEP 8 style guidelines
2. Add type hints where appropriate
3. Include docstrings for all functions
4. Test all features before submitting pull requests

### Research Ethics
- Ensure all data collection complies with research ethics standards
- Maintain participant anonymity in all code changes
- Respect privacy and confidentiality requirements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Research Team

**Principal Investigator**: [Your Name]
**Institution**: [Your Institution]
**Contact**: [Your Email]

## Acknowledgments

- Korean Ministry of Education for vocabulary standards
- OpenAI for GPT-4 API access
- Streamlit Community for hosting platform
- Participating teachers for valuable feedback


**Note**: This tool is designed specifically for the Korean educational context and curriculum standards. Adaptation may be required for use in other educational systems.
