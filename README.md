# Smart Component Search Engine

A sophisticated, context-aware search engine and personalized recommendation system to help engineers and buyers quickly find the right electronic parts, even with partial or imprecise information.

## Features

### 🔍 Intelligent Search Engine
- **AI-Enhanced Queries**: Uses Google Gemini AI to enhance user search queries for better results
- **Fuzzy Matching**: Implements fuzzy string matching to handle typos and partial information
- **Context Awareness**: Takes into account project context (e.g., "IoT project", "audio circuit")
- **Real-time Search**: Integrates with Mouser Electronics API for live part data

### 🤖 AI-Powered Recommendations
- **Smart Recommendations**: AI-generated suggestions based on search results
- **Personalized Suggestions**: User-specific recommendations based on search history
- **Part Compatibility**: Analyzes compatibility between different components
- **Alternative Suggestions**: Suggests cost-effective and higher-quality alternatives

### 🎯 Advanced Features
- **Similar Parts Discovery**: Find similar components to a reference part
- **Detailed Part Information**: Complete specifications, pricing, and availability
- **User Profiles**: Personalized experience based on search patterns
- **Modern Web Interface**: Beautiful, responsive UI with real-time search

## Technology Stack

- **Backend**: Python 3.8+
- **Web Framework**: Flask
- **AI Integration**: Google Gemini API
- **Search API**: Mouser Electronics API, Tried implementing ElevenLabs API
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Fuzzy Matching**: FuzzyWuzzy, Levenshtein

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys** (already configured in the code):
   - Mouser API Key: `d99c4255-03a1-495a-8a37-c317fa862ab2`
   - Gemini API Key: `AIzaSyDcGNx1RsNgWOC9K-7bH40fdnRqm4vqtTs`

## Usage

### Running the Web Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Search for parts**:
   - Enter your search query (e.g., "Arduino Uno", "LM358", "10k resistor")
   - Add context if needed (e.g., "for IoT project", "audio amplifier")
   - Click Search to get AI-enhanced results

### Using the Python API

```python
from mouser_search_engine import MouserSearchApp

# Initialize the application
app = MouserSearchApp(
    mouser_api_key="your_mouser_api_key",
    gemini_api_key="your_gemini_api_key"
)

# Search for parts
results = app.search_parts(
    query="Arduino Uno",
    user_id="user123",
    context="prototyping project"
)

# Get part details
part_details = app.get_part_details("Arduino Uno")

# Find similar parts
similar_parts = app.find_similar_parts("Arduino Uno")
```

### Running Tests

```bash
python test_mouser_search.py
```

## Project Structure

```
mouser-search-engine/
├── .env                      # Has API keys
├── app.py                    # Main app deployed by streamlit
├── chatbot.py                # Script which runs Gemini AI using API
├── requirements.txt          # Python dependencies
└── README.md                 # Readme files
```

## API Endpoints

### Web API Endpoints

- `POST /search` - Perform intelligent search
- `GET /part/<part_number>` - Get detailed part information
- `GET /similar/<part_number>` - Find similar parts
- `GET /recommendations` - Get personalized recommendations
- `POST /set-user` - Set user ID for personalization

### Request/Response Examples

**Search Request**:
```json
{
    "query": "Arduino Uno",
    "context": "prototyping project"
}
```

**Search Response**:
```json
{
    "original_query": "Arduino Uno",
    "enhanced_query": "Arduino Uno R3 microcontroller board",
    "total_found": 15,
    "results": [
        {
            "part_number": "A000066",
            "manufacturer": "Arduino",
            "description": "Arduino Uno R3 Microcontroller Board",
            "category": "Development Boards",
            "price": 25.00,
            "stock": 150,
            "datasheet_url": "https://...",
            "image_url": "https://...",
            "specifications": {...}
        }
    ],
    "recommendations": [
        "Consider Arduino Nano for smaller form factor projects",
        "Arduino Mega 2560 offers more I/O pins for complex projects"
    ],
    "personalized_recommendations": [
        "Popular in Microcontrollers: ESP32 - WiFi & Bluetooth Module"
    ]
}
```

## Key Components

### 1. MouserAPIClient
- Handles communication with Mouser Electronics API
- Searches for electronic parts and components
- Extracts pricing, availability, and specification data

### 2. GeminiAIAssistant
- Enhances search queries using Google Gemini AI
- Generates intelligent recommendations
- Analyzes part compatibility and relationships

### 3. IntelligentSearchEngine
- Implements fuzzy matching algorithms
- Manages search history and user preferences
- Combines multiple search strategies for optimal results

### 4. RecommendationEngine
- Creates personalized user profiles
- Generates recommendations based on search patterns
- Tracks user preferences and favorite categories

### 5. MouserSearchApp
- Main application orchestrator
- Combines all components for seamless operation
- Provides unified API for all search functionality

## Features in Detail

### AI-Enhanced Search
The system uses Google Gemini AI to understand user intent and enhance search queries. For example:
- Input: "Arduino Uno"
- Enhanced: "Arduino Uno R3 microcontroller board with ATmega328P"

### Fuzzy Matching
Implements intelligent string matching to handle:
- Typos and misspellings
- Partial part numbers
- Alternative naming conventions
- Abbreviations and acronyms

### Context Awareness
Takes project context into account:
- "Arduino Uno for IoT project" → Suggests WiFi modules, sensors
- "LM358 for audio circuit" → Focuses on audio-specific applications
- "10k resistor for voltage divider" → Suggests precision resistors

### Personalized Recommendations
Learns from user behavior:
- Tracks favorite manufacturers
- Identifies preferred categories
- Suggests based on search history
- Adapts to user preferences over time

## Customization

### Adding New Search Strategies
Extend the `IntelligentSearchEngine` class to add custom search algorithms:

```python
def custom_search_strategy(self, query: str) -> List[ElectronicPart]:
    # Implement your custom search logic
    pass
```

### Modifying AI Prompts
Customize the AI behavior by modifying prompts in `GeminiAIAssistant`:

```python
def enhance_search_query(self, user_query: str, context: str = "") -> str:
    prompt = f"""
    Your custom prompt here...
    """
```

### Adding New Recommendation Types
Extend the `RecommendationEngine` to add new recommendation strategies:

```python
def get_custom_recommendations(self, user_id: str) -> List[str]:
    # Implement custom recommendation logic
    pass
```

## Troubleshooting

### Common Issues

1. **API Connection Errors**:
   - Verify API keys are correct
   - Check internet connectivity
   - Ensure API quotas are not exceeded

2. **No Search Results**:
   - Try different search terms
   - Check spelling and formatting
   - Use more specific part numbers

3. **Slow Performance**:
   - Reduce search result limits
   - Optimize fuzzy matching thresholds
   - Cache frequently accessed data

### Debug Mode
Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run the test suite to verify functionality
3. Review the API documentation
4. Check the logs for error messages

## Future Enhancements

- [ ] Machine learning-based recommendation system
- [ ] Integration with additional component databases
- [ ] Advanced filtering and sorting options
- [ ] Mobile application
- [ ] Batch search functionality
- [ ] Export search results to CSV/Excel
- [ ] Integration with CAD software
- [ ] Real-time price alerts
- [ ] Component lifecycle tracking
- [ ] Multi-language support

## Contributors
Neha Upadhye
Nihal Malavalli Lokesh
Kumar Mantha
