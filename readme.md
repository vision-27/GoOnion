# 🌍 AI Multi-Agent Travel Planner

An intelligent, interactive travel planning system powered by Google's Gemini AI that uses specialized expert agents to create personalized travel itineraries.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Agent Specialists](#agent-specialists)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Example Conversation](#example-conversation)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The AI Travel Planner is a sophisticated multi-agent system that replaces static travel data with dynamic, intelligent analysis. Instead of pre-programmed responses, it uses Google's Gemini AI to provide real-time insights about destinations, weather patterns, cultural events, and travel logistics.

### Why This Approach?

- **🧠 Dynamic Knowledge**: Uses real AI knowledge instead of static databases
- **👥 Expert Specialization**: Each agent focuses on specific travel domains
- **💬 Natural Interaction**: Conversational interface that adapts to your needs
- **🎨 Personalized Planning**: Tailored recommendations based on your interests
- **🔄 Interactive Refinement**: Modify and improve your plan through conversation

## ✨ Features

### Core Capabilities
- **Interactive Conversation Flow** - Natural dialogue for gathering preferences
- **Flexible Date Planning** - Handles both flexible and fixed travel dates
- **Multi-Agent Coordination** - Specialized experts working together
- **Real-Time Analysis** - Dynamic insights using current AI knowledge
- **Personalized Itineraries** - Custom plans based on your interests and budget
- **Plan Modifications** - Interactive editing and refinements
- **Comprehensive Output** - Detailed analysis from multiple expert perspectives

### Additional Services
- **📋 Travel Checklists** - Personalized packing and preparation lists
- **💰 Budget Analysis** - Detailed cost breakdowns and money-saving tips
- **💾 Plan Export** - Save your complete itinerary to a file
- **🎯 Quick Demo Mode** - Test the system with sample data
- **🌤️ Weather Integration** - Seasonal analysis and timing recommendations

## 🤖 Agent Specialists

### 1. Weather & Seasonal Expert
- **Purpose**: Analyzes climate patterns and seasonal travel conditions
- **Capabilities**: 
  - Best time to visit recommendations
  - Weather-based activity suggestions
  - Seasonal pricing and crowd analysis
  - Climate-appropriate packing advice

### 2. Flight & Accommodation Expert  
- **Purpose**: Provides booking insights and accommodation advice
- **Capabilities**:
  - Flight route analysis and pricing strategies
  - Accommodation recommendations by area
  - Booking timing and platform suggestions
  - Budget optimization tips

### 3. Route & Transportation Expert
- **Purpose**: Optimizes local transportation and itinerary routing
- **Capabilities**:
  - Public transport guidance
  - Traffic pattern analysis
  - Efficient route planning
  - Time optimization strategies

### 4. Local Attractions & Culture Expert
- **Purpose**: Discovers attractions, activities, and cultural experiences
- **Capabilities**:
  - Interest-based attraction matching
  - Hidden gems and local favorites
  - Cultural event discovery
  - Experience timing and logistics

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key
- Internet connection for AI model access

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/ai-travel-planner.git
cd ai-travel-planner
```

### Step 2: Install Dependencies
```bash
pip install google-generativeai python-dotenv
```

### Step 3: Set Up Environment
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🔑 Configuration

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | ✅ Yes |

## 💻 Usage

### Basic Usage

```bash
python travel_planner.py
```

### Quick Demo Mode

For testing purposes, you can run a quick demo:

```python
# In the main script, uncomment this line:
quick_start_demo()
```

### Interactive Planning Session

1. **Start the Application**
   ```bash
   python travel_planner.py
   ```

2. **Follow the Prompts**
   - Enter your departure and destination cities
   - Choose flexible or fixed dates
   - Specify your interests and preferences
   - Review expert recommendations

3. **Refine Your Plan**
   - Ask for modifications
   - Get additional details
   - Request specific information

4. **Export Your Plan**
   - Save to a text file
   - Get travel checklists
   - View budget breakdowns

## 🗣️ Example Conversation

```
🌍 Welcome to the AI Travel Planner! 🌍

📍 Where are you traveling FROM? New York
📍 Where do you want to travel TO? Tokyo
📅 Are your travel dates flexible? yes

🎯 Perfect! Let me analyze the best times to visit Tokyo...

🌤️ Consulting weather experts...

🏆 EXPERT RECOMMENDATIONS:
The best time to visit Tokyo is during spring (March-May) for cherry 
blossoms and mild weather, or autumn (September-November) for pleasant 
temperatures and beautiful foliage. Avoid July-August due to extreme 
heat and humidity, and the rainy season in June...

Based on this analysis, which month sounds good to you? April

What specific dates in April? 2024-04-10, 2024-04-17

🎨 Now let's personalize your trip:
⏱️ How many days will you stay? 7
🌅 Do you prefer day activities, night activities, or mixed? mixed
🎯 What are you interested in? art, food, traditional culture, temples
💰 What's your budget range? medium
🏨 Preferred accommodation type? hotel

🚀 Creating your personalized travel plan...
```

## 📁 Project Structure

```
ai-travel-planner/
├── travel_planner.py          # Main application file
├── .env                       # Environment variables (create this)
├── .env.example              # Example environment file
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── examples/                 # Example usage and demos
│   ├── sample_conversation.md
│   └── demo_outputs/
├── docs/                     # Additional documentation
│   ├── agent_details.md
│   ├── customization.md
│   └── troubleshooting.md
└── saved_plans/              # Directory for exported travel plans
```

## ⚙️ How It Works

### 1. Multi-Agent Architecture
Each specialist agent is initialized with:
- **Domain-specific system prompts**
- **Specialized tool functions**
- **Knowledge area expertise**

### 2. Dynamic Function Calling
```python
# Agents can call specialized functions
def analyze_weather_and_seasons(location: str, travel_month: str) -> Dict:
    """Analyze weather using AI knowledge, not static data"""
    
def create_optimized_route(location: str, interests: List[str], duration_days: int) -> Dict:
    """Create routes using real local knowledge"""
```

### 3. Intelligent Coordination
The coordinator routes user queries to appropriate agents:
- Weather questions → Weather Agent
- Flight queries → Booking Agent  
- Route planning → Route Agent
- Activity suggestions → Attractions Agent

### 4. Conversational Memory
Each agent maintains conversation history for context-aware responses.

## 🎨 Customization

### Adding New Agents

```python
class RestaurantAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Restaurant & Dining Expert",
            system_prompt="You are a restaurant and dining specialist...",
            tools=[find_restaurants, analyze_food_scene]
        )
```

### Modifying Agent Behavior

Edit the `system_prompt` in each agent's initialization:

```python
class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Weather and Seasonal Expert",
            system_prompt="""Your custom prompt here...""",
            tools=[analyze_weather_and_seasons, recommend_best_travel_dates]
        )
```

### Adding New Tools

Create new analysis functions:

```python
def analyze_local_transportation(city: str, mobility_needs: str) -> Dict:
    """Analyze transportation options for specific mobility needs"""
    prompt = f"Analyze accessible transportation in {city} for {mobility_needs}"
    # Implementation here
```

## 🔧 Troubleshooting

### Common Issues

#### API Key Problems
```
Error: GEMINI_API_KEY not found in environment
```
**Solution**: Check that your `.env` file exists and contains your API key:
```env
GEMINI_API_KEY=your_actual_key_here
```

#### Import Errors
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Solution**: Install required dependencies:
```bash
pip install google-generativeai python-dotenv
```

#### Rate Limiting
If you encounter rate limits, the system will gracefully handle errors and provide fallback responses.

### Debugging Mode

Enable verbose logging by modifying the model initialization:

```python
# In BaseAgent.__init__()
self.model = genai.GenerativeModel("gemini-pro", verbose=True)
```

### Performance Tips

- **Batch Questions**: Ask related questions together
- **Be Specific**: Detailed queries get better responses
- **Use Context**: Reference previous answers in follow-ups

## 🤝 Contributing

We welcome contributions! Here are ways to help:

### Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Enhancement
- **New Agent Types**: Restaurant, Adventure, Business Travel specialists
- **Integration APIs**: Real-time data from travel services
- **UI Development**: Web interface or mobile app
- **Advanced Features**: Group travel, multi-city trips
- **Localization**: Support for different languages and regions

### Bug Reports
Use GitHub Issues to report bugs. Include:
- Error messages
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## 📊 Performance & Limitations

### What Works Well
- **Dynamic Responses**: Fresh insights for any destination
- **Personalization**: Tailored to individual preferences  
- **Comprehensive Coverage**: Multiple travel aspects addressed
- **Interactive Refinement**: Easily modify plans through conversation

### Current Limitations
- **API Dependency**: Requires internet connection and API access
- **Response Time**: AI processing can take a few seconds
- **Knowledge Cutoff**: Based on Gemini's training data timeline
- **No Real-time Bookings**: Provides guidance, not actual reservations

### Future Enhancements
- Integration with booking platforms
- Real-time price and availability data
- Mobile application development
- Offline mode with cached responses

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for providing the AI capabilities
- **Travel community** for inspiring comprehensive travel planning
- **Open source contributors** who make projects like this possible

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/ai-travel-planner/issues)
- **Discussions**: [Join community discussions](https://github.com/yourusername/ai-travel-planner/discussions)
- **Documentation**: Check the `docs/` folder for detailed guides

---

**Happy Travels! 🧳✈️**

*Transform your travel planning experience with the power of AI-driven expert insights.*
