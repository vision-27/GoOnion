import google.generativeai as genai
from typing import List, Dict, Callable, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json
import re
import inspect
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment. Check your .env file.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

@dataclass
class TravelRequest:
    from_location: str = ""
    to_location: str = ""
    preferred_dates: List[str] = None
    flexible_dates: bool = False
    duration_days: int = 0
    time_preference: str = ""  # day/night/mixed
    interests: List[str] = None
    budget_range: str = ""  # low/medium/high
    accommodation_type: str = ""  # hotel/hostel/apartment
    transport_preference: str = ""  # flight/train/car

class BaseAgent:
    """Base agent class with common functionality."""
    
    def __init__(self, name: str, system_prompt: str, tools: List[Callable]):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = {}
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.history = {"calls": [], "responses": []}
        
        for tool in tools:
            self.tools[tool.__name__] = tool
    
    def _parse_function_calls(self, text: str) -> List[Dict]:
        """Extract function calls from the model's response."""
        calls = []
        pattern = r'CALL_FUNCTION:\s*(\w+)\((.*?)\)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for func_name, params_str in matches:
            if func_name in self.tools:
                params = self._parse_parameters(params_str)
                calls.append({"function": func_name, "parameters": params})
        
        return calls
    
    def _parse_parameters(self, params_str: str) -> Dict[str, Any]:
        """Parse function parameters from string."""
        params = {}
        if not params_str.strip():
            return params
        
        try:
            # Simple parameter parsing
            param_dict = eval(f"dict({params_str})")
            return param_dict
        except:
            # Fallback parsing
            param_pairs = [p.strip() for p in params_str.split(',')]
            for pair in param_pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Try to parse lists and convert types
                    if value.startswith('[') and value.endswith(']'):
                        try:
                            params[key] = eval(value)
                        except:
                            params[key] = value
                    else:
                        params[key] = value
        
        return params
    
    def _execute_function(self, function_name: str, **kwargs) -> Any:
        """Execute a function and return results."""
        if function_name not in self.tools:
            return {"error": f"Function '{function_name}' not found"}
        
        try:
            result = self.tools[function_name](**kwargs)
            self.history["calls"].append({
                "function": function_name, 
                "parameters": kwargs, 
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            return result
        except Exception as e:
            error_result = {"error": f"Error executing {function_name}: {str(e)}"}
            self.history["calls"].append({
                "function": function_name, 
                "parameters": kwargs, 
                "error": error_result,
                "timestamp": datetime.now().isoformat()
            })
            return error_result
    
    def query(self, prompt: str, max_iterations: int = 3) -> str:
        """Query the agent with function calling capability."""
        conversation_history = ""
        current_message = prompt
        
        for iteration in range(max_iterations):
            full_prompt = f"""System: {self.system_prompt}

Available Functions:
{self._get_function_descriptions()}

Instructions for function calling:
- When you need to use a function, write: CALL_FUNCTION: function_name(param1="value1", param2=["item1", "item2"])
- Use proper Python syntax for parameters
- After calling functions, provide a comprehensive response

{conversation_history}

User: {current_message}"""
            
            try:
                response = self.model.generate_content(full_prompt)
                response_text = response.text
                self.history["responses"].append(response_text)
                
                # Check for function calls
                function_calls = self._parse_function_calls(response_text)
                
                if function_calls:
                    # Execute function calls
                    function_results = []
                    for call in function_calls:
                        result = self._execute_function(call["function"], **call["parameters"])
                        function_results.append(f"Function {call['function']} returned: {json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)}")
                    
                    # Add to conversation history for next iteration
                    conversation_history += f"\nAssistant: {response_text}\n"
                    conversation_history += f"Function Results:\n" + "\n".join(function_results) + "\n"
                    current_message = "Based on the function results above, provide a comprehensive response to the original request."
                    
                    continue
                else:
                    return response_text
                    
            except Exception as e:
                return f"Error generating response: {str(e)}"
        
        return "Maximum iterations reached. Please try a simpler request."
    
    def _get_function_descriptions(self) -> str:
        """Get descriptions of available functions."""
        descriptions = []
        for name, func in self.tools.items():
            doc = func.__doc__ or "No description available"
            sig = inspect.signature(func)
            params = []
            for param_name, param in sig.parameters.items():
                param_type = getattr(param.annotation, '__name__', str(param.annotation)) if param.annotation != param.empty else "any"
                params.append(f"{param_name}: {param_type}")
            
            descriptions.append(f"Function: {name}({', '.join(params)})\nDescription: {doc}")
        
        return "\n\n".join(descriptions)

# ======================
# INTELLIGENT ANALYSIS TOOLS
# ======================

def analyze_weather_and_seasons(location: str, travel_month: str) -> Dict:
    """Analyze weather and seasonal conditions for a location using AI knowledge."""
    prompt = f"""Analyze the weather and travel conditions for {location} in {travel_month}.

Consider:
1. Typical temperature ranges
2. Rainfall patterns
3. Tourist seasons (high/low)
4. Special weather phenomena
5. Best activities for that time
6. What to pack
7. Any weather-related travel advisories

Provide practical advice for travelers visiting {location} in {travel_month}."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # Parse the response into structured data
        analysis_text = response.text
        
        return {
            "location": location,
            "month": travel_month,
            "analysis": analysis_text,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Weather analysis failed: {str(e)}"}

def recommend_best_travel_dates(location: str, flexible_window_months: int = 6) -> Dict:
    """Recommend the best times to visit a location throughout the year."""
    prompt = f"""As a travel expert, recommend the best times to visit {location} within the next {flexible_window_months} months.

Consider:
1. Weather conditions
2. Tourist crowds and prices
3. Local festivals and events
4. Seasonal attractions
5. Travel costs (flights, accommodation)
6. Natural phenomena (cherry blossoms, northern lights, etc.)

Rank the months from best to worst for travel, explaining your reasoning for each ranking."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        return {
            "location": location,
            "recommendations": response.text,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "window_months": flexible_window_months
        }
    except Exception as e:
        return {"error": f"Date recommendation failed: {str(e)}"}

def find_flight_options(origin: str, destination: str, travel_date: str, budget_range: str) -> Dict:
    """Find flight options and provide realistic travel advice."""
    prompt = f"""As a travel booking expert, provide comprehensive flight information for:
- Route: {origin} to {destination}
- Date: {travel_date}
- Budget: {budget_range}

Include:
1. Typical flight duration and routes
2. Major airlines that serve this route
3. Expected price ranges for {budget_range} budget
4. Best booking strategies and timing
5. Alternative airports to consider
6. Layover cities and connection options
7. Peak vs off-peak pricing factors
8. Tips for finding deals

Provide realistic, current market insights."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        return {
            "route": f"{origin} → {destination}",
            "date": travel_date,
            "budget": budget_range,
            "flight_analysis": response.text,
            "search_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Flight search failed: {str(e)}"}

def find_accommodation_options(location: str, dates: List[str], accommodation_type: str, budget_range: str) -> Dict:
    """Find accommodation options with expert insights."""
    prompt = f"""As a travel accommodation expert, provide detailed advice for staying in {location}:

Details:
- Location: {location}
- Dates: {', '.join(dates)}
- Type: {accommodation_type}
- Budget: {budget_range}

Include:
1. Best neighborhoods to stay in
2. Typical prices for {budget_range} budget
3. Recommended accommodation types and brands
4. Booking platforms and strategies
5. What amenities to expect
6. Safety and location considerations
7. Transportation access from different areas
8. Local tips for finding deals

Provide practical, actionable accommodation advice."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        return {
            "location": location,
            "dates": dates,
            "accommodation_type": accommodation_type,
            "budget": budget_range,
            "accommodation_analysis": response.text,
            "search_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Accommodation search failed: {str(e)}"}

def get_traffic_and_transport_insights(location: str, time_preference: str) -> Dict:
    """Get transportation and traffic insights for a destination."""
    prompt = f"""As a local transportation expert for {location}, provide comprehensive transport information:

Focus on:
1. Public transportation systems (metro, buses, trains)
2. Typical traffic patterns during {time_preference} time
3. Best ways to get around the city
4. Transportation costs and payment methods
5. Rush hour patterns and timing
6. Walkability of different areas
7. Taxi/rideshare availability and costs
8. Transportation apps and tools for travelers
9. Safety considerations for different transport modes

Provide practical advice for tourists visiting {location}."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        return {
            "location": location,
            "time_preference": time_preference,
            "transport_analysis": response.text,
            "analysis_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Transport analysis failed: {str(e)}"}

def create_optimized_route(location: str, interests: List[str], duration_days: int, time_preference: str) -> Dict:
    """Create an optimized travel route based on interests and time constraints."""
    interests_str = ", ".join(interests)
    
    prompt = f"""As a local tour guide expert for {location}, create an optimized {duration_days}-day itinerary:

Requirements:
- Duration: {duration_days} days
- Interests: {interests_str}
- Time preference: {time_preference} activities
- Minimize travel time between locations
- Maximize experiences within time constraints

Create a detailed day-by-day itinerary including:
1. Morning, afternoon, and evening activities
2. Recommended timing for each activity
3. Transportation between locations
4. Meal recommendations that fit the schedule
5. Rest periods and flexible time
6. Alternative options in case of weather/closures
7. Estimated costs and booking requirements
8. Local insider tips

Make it practical and executable for a real traveler."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        return {
            "location": location,
            "duration_days": duration_days,
            "interests": interests,
            "time_preference": time_preference,
            "optimized_itinerary": response.text,
            "created_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Route optimization failed: {str(e)}"}

def find_attractions_and_activities(location: str, interests: List[str], duration_days: int) -> Dict:
    """Find attractions and activities based on specific interests."""
    interests_str = ", ".join(interests)
    
    prompt = f"""As a local expert for {location}, recommend the best attractions and activities for someone interested in {interests_str}.

For a {duration_days}-day trip, provide:
1. Must-see attractions for each interest category
2. Hidden gems and local favorites
3. Opening hours and best times to visit
4. Estimated visit duration for each attraction
5. Entry fees and booking requirements
6. Seasonal considerations
7. Photography and experience tips
8. Nearby restaurants and facilities
9. Accessibility information
10. How to avoid crowds

Prioritize based on the visitor's interests and practical logistics."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        return {
            "location": location,
            "interests": interests,
            "duration_days": duration_days,
            "attractions_guide": response.text,
            "search_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Attractions search failed: {str(e)}"}

def find_local_events_and_culture(location: str, dates: List[str], interests: List[str]) -> Dict:
    """Find local events, festivals, and cultural activities."""
    interests_str = ", ".join(interests)
    dates_str = ", ".join(dates)
    
    prompt = f"""As a local cultural expert for {location}, provide information about events and cultural activities during {dates_str}.

Focus on interests: {interests_str}

Include:
1. Seasonal festivals and events
2. Cultural performances and shows
3. Local markets and food events
4. Art exhibitions and galleries
5. Music venues and nightlife
6. Sports events and activities
7. Religious or traditional celebrations
8. Community events and workshops
9. Booking information and costs
10. Cultural etiquette and tips

Provide both scheduled events and ongoing cultural experiences."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        return {
            "location": location,
            "dates": dates,
            "interests": interests,
            "events_and_culture": response.text,
            "search_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Events search failed: {str(e)}"}

# ======================
# SPECIALIZED AGENTS
# ======================

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Weather and Seasonal Expert",
            system_prompt="""You are a weather and seasonal travel expert. You analyze climate patterns, 
            seasonal variations, and provide detailed weather-based travel recommendations. Use your 
            knowledge of global weather patterns, seasonal tourism, and climate data to give accurate advice.""",
            tools=[analyze_weather_and_seasons, recommend_best_travel_dates]
        )

class FlightHotelAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Flight and Accommodation Expert",
            system_prompt="""You are a flight and accommodation booking expert. You understand airline 
            routes, pricing patterns, hotel markets, and booking strategies. Provide realistic advice 
            about flights, hotels, and accommodation based on current market knowledge.""",
            tools=[find_flight_options, find_accommodation_options]
        )

class RouteAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Route and Transportation Expert",
            system_prompt="""You are a local transportation and route optimization expert. You understand 
            public transport, traffic patterns, and efficient routing. Create practical itineraries that 
            minimize travel time and maximize experiences.""",
            tools=[get_traffic_and_transport_insights, create_optimized_route]
        )

class AttractionsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Local Attractions and Culture Expert",
            system_prompt="""You are a local attractions and cultural activities expert. You know the 
            best attractions, hidden gems, cultural events, and local experiences. Provide insider 
            knowledge and practical tips for travelers.""",
            tools=[find_attractions_and_activities, find_local_events_and_culture]
        )

# ======================
# MAIN COORDINATOR
# ======================

class TravelPlannerCoordinator:
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.booking_agent = FlightHotelAgent()
        self.route_agent = RouteAgent()
        self.attractions_agent = AttractionsAgent()
        self.travel_request = TravelRequest()
        
    def start_conversation(self):
        """Start the interactive travel planning conversation."""
        print("🌍 Welcome to the AI Travel Planner! 🌍")
        print("I have a team of expert agents ready to plan your perfect trip.\n")
        
        return self.gather_basic_information()
    
    def gather_basic_information(self):
        """Gather basic travel information from user."""
        print("Let's start with the basics:\n")
        
        # Get origin and destination
        self.travel_request.from_location = input("📍 Where are you traveling FROM? (city, country): ").strip()
        self.travel_request.to_location = input("📍 Where do you want to travel TO? (city, country): ").strip()
        
        # Ask about date flexibility
        flexible = input("\n📅 Are your travel dates flexible? (yes/no): ").strip().lower()
        self.travel_request.flexible_dates = flexible in ['yes', 'y', 'yeah', 'sure']
        
        if self.travel_request.flexible_dates:
            return self.handle_flexible_dates()
        else:
            return self.handle_fixed_dates()
    
    def handle_flexible_dates(self):
        """Handle flexible date scenario with AI recommendations."""
        print("\n🎯 Perfect! Let me analyze the best times to visit your destination...")
        
        # Get weather-based recommendations
        print("🌤️  Consulting weather experts...")
        recommendations = self.weather_agent.query(
            f"What are the best months to visit {self.travel_request.to_location} considering weather, crowds, and costs? Please analyze the next 6 months."
        )
        
        print(f"\n🏆 EXPERT RECOMMENDATIONS:\n{recommendations}\n")
        
        # Let user choose
        month = input("Based on this analysis, which month sounds good to you? ").strip()
        
        # Get specific date
        dates = input(f"What specific dates in {month}? (YYYY-MM-DD, comma separated): ").strip()
        if dates:
            self.travel_request.preferred_dates = [d.strip() for d in dates.split(',')]
        
        return self.gather_preferences()
    
    def handle_fixed_dates(self):
        """Handle fixed date scenario with weather analysis."""
        dates = input("📅 What are your travel dates? (YYYY-MM-DD, comma separated): ").strip()
        self.travel_request.preferred_dates = [d.strip() for d in dates.split(',')]
        
        # Analyze weather for selected dates
        if self.travel_request.preferred_dates:
            travel_month = self.travel_request.preferred_dates[0].split('-')[1]
            month_names = ["", "January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"]
            month_name = month_names[int(travel_month)]
            
            print("🌤️  Analyzing weather for your dates...")
            weather_analysis = self.weather_agent.query(
                f"Analyze the weather conditions for {self.travel_request.to_location} in {month_name}. What should travelers expect?"
            )
            
            print(f"\n🌡️  WEATHER ANALYSIS:\n{weather_analysis}\n")
        
        return self.gather_preferences()
    
    def gather_preferences(self):
        """Gather detailed user preferences."""
        print("🎨 Now let's personalize your trip:\n")
        
        # Duration
        duration = input("⏱️  How many days will you stay? ").strip()
        try:
            self.travel_request.duration_days = int(duration)
        except:
            self.travel_request.duration_days = 3
        
        # Time preference
        time_pref = input("🌅 Do you prefer day activities, night activities, or mixed? (day/night/mixed): ").strip().lower()
        self.travel_request.time_preference = time_pref if time_pref in ['day', 'night', 'mixed'] else 'mixed'
        
        # Interests
        print("\n🎯 What are you interested in? (be specific - e.g., 'art museums, local food, historic architecture')")
        interests = input("Your interests: ").strip()
        self.travel_request.interests = [i.strip() for i in interests.split(',')]
        
        # Budget
        budget = input("\n💰 What's your budget range? (low/medium/high): ").strip().lower()
        self.travel_request.budget_range = budget if budget in ['low', 'medium', 'high'] else 'medium'
        
        # Accommodation
        accom = input("🏨 Preferred accommodation type? (hotel/hostel/apartment/any): ").strip().lower()
        self.travel_request.accommodation_type = accom if accom in ['hotel', 'hostel', 'apartment'] else 'hotel'
        
        return self.create_comprehensive_plan()
    
    def create_comprehensive_plan(self):
        """Create comprehensive travel plan using all expert agents."""
        print("\n🚀 Creating your personalized travel plan...")
        print("My expert agents are analyzing your requirements...\n")
        
        # 1. Flight Analysis
        print("✈️  Flight Expert analyzing routes and pricing...")
        flight_analysis = self.booking_agent.query(
            f"Find flight options from {self.travel_request.from_location} to {self.travel_request.to_location} "
            f"for {self.travel_request.preferred_dates[0]} with {self.travel_request.budget_range} budget."
        )
        
        # 2. Accommodation Analysis
        print("🏨 Accommodation Expert finding best places to stay...")
        accommodation_analysis = self.booking_agent.query(
            f"Find {self.travel_request.accommodation_type} accommodations in {self.travel_request.to_location} "
            f"for dates {', '.join(self.travel_request.preferred_dates)} with {self.travel_request.budget_range} budget."
        )
        
        # 3. Transportation & Route Analysis
        print("🗺️  Transportation Expert optimizing your routes...")
        transport_analysis = self.route_agent.query(
            f"Analyze transportation options in {self.travel_request.to_location} for {self.travel_request.time_preference} activities."
        )
        
        route_optimization = self.route_agent.query(
            f"Create an optimized {self.travel_request.duration_days}-day itinerary for {self.travel_request.to_location} "
            f"focusing on {', '.join(self.travel_request.interests)} with {self.travel_request.time_preference} preference."
        )
        
        # 4. Attractions Analysis
        print("🎨 Attractions Expert finding perfect activities...")
        attractions_analysis = self.attractions_agent.query(
            f"Find the best attractions and activities in {self.travel_request.to_location} for someone interested in "
            f"{', '.join(self.travel_request.interests)} for a {self.travel_request.duration_days}-day trip."
        )
        
        events_analysis = self.attractions_agent.query(
            f"Find local events, festivals, and cultural activities in {self.travel_request.to_location} "
            f"during {', '.join(self.travel_request.preferred_dates)} that match interests: {', '.join(self.travel_request.interests)}."
        )
        
        return self.present_comprehensive_plan(
            flight_analysis, accommodation_analysis, transport_analysis, 
            route_optimization, attractions_analysis, events_analysis
        )
    
    def present_comprehensive_plan(self, flight_analysis, accommodation_analysis, 
                                 transport_analysis, route_optimization, 
                                 attractions_analysis, events_analysis):
        """Present the final comprehensive travel plan."""
        print("\n" + "="*80)
        print("🎉 YOUR PERSONALIZED TRAVEL PLAN 🎉")
        print("="*80)
        
        # Trip Overview
        print(f"\n📋 TRIP OVERVIEW")
        print(f"From: {self.travel_request.from_location}")
        print(f"To: {self.travel_request.to_location}")
        print(f"Dates: {', '.join(self.travel_request.preferred_dates)}")
        print(f"Duration: {self.travel_request.duration_days} days")
        print(f"Budget: {self.travel_request.budget_range}")
        print(f"Interests: {', '.join(self.travel_request.interests)}")
        
        # Expert Analyses
        print(f"\n✈️  FLIGHT EXPERT ANALYSIS:")
        print("─" * 40)
        print(flight_analysis)
        
        print(f"\n🏨 ACCOMMODATION EXPERT ANALYSIS:")
        print("─" * 40)
        print(accommodation_analysis)
        
        print(f"\n🚌 TRANSPORTATION EXPERT ANALYSIS:")
        print("─" * 40)
        print(transport_analysis)
        
        print(f"\n🗺️  OPTIMIZED ITINERARY:")
        print("─" * 40)
        print(route_optimization)
        
        print(f"\n🎨 ATTRACTIONS & ACTIVITIES:")
        print("─" * 40)
        print(attractions_analysis)
        
        print(f"\n🎉 LOCAL EVENTS & CULTURE:")
        print("─" * 40)
        print(events_analysis)
        
        # Additional tips
        self.generate_final_tips()
        
        # Ask for modifications
        modify = input(f"\n🤔 Would you like me to modify or expand any part of this plan? (yes/no): ").strip().lower()
        if modify in ['yes', 'y']:
            return self.handle_plan_modifications()
        else:
            print(f"\n🎯 Perfect! Have an amazing trip! Safe travels! 🧳✈️")
            return True
    
    def generate_final_tips(self):
        """Generate personalized final tips."""
        print(f"\n💡 PERSONALIZED TRAVEL TIPS:")
        print("─" * 40)
        
        tips_prompt = f"""As a travel expert, provide final travel tips for someone visiting {self.travel_request.to_location} 
        from {self.travel_request.from_location} with interests in {', '.join(self.travel_request.interests)} 
        on a {self.travel_request.budget_range} budget. Include practical advice about money, safety, 
        communication, and cultural considerations."""
        
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            tips = model.generate_content(tips_prompt)
            print(tips.text)
        except Exception as e:
            print("• Download offline maps and translation apps")
            print("• Check visa requirements and passport validity")
            print("• Notify banks of your travel dates")
            print("• Get travel insurance")
            print("• Research local customs and etiquette")
    
    def handle_plan_modifications(self):
        """Handle user requests for plan modifications."""
        print(f"\n🔧 What would you like me to modify or get more details about?")
        modification_request = input("Tell me what you'd like to change or learn more about: ").strip()
        
        if modification_request:
            print(f"\n🔄 Let me get more specific information...")
            
            # Route the request to the most appropriate agent
            if any(word in modification_request.lower() for word in ['flight', 'airline', 'price', 'route']):
                response = self.booking_agent.query(f"Regarding travel from {self.travel_request.from_location} to {self.travel_request.to_location}: {modification_request}")
            elif any(word in modification_request.lower() for word in ['hotel', 'accommodation', 'stay', 'room']):
                response = self.booking_agent.query(f"Regarding accommodation in {self.travel_request.to_location}: {modification_request}")
            elif any(word in modification_request.lower() for word in ['transport', 'route', 'itinerary', 'schedule']):
                response = self.route_agent.query(f"Regarding transportation and routes in {self.travel_request.to_location}: {modification_request}")
            elif any(word in modification_request.lower() for word in ['attraction', 'activity', 'event', 'culture']):
                response = self.attractions_agent.query(f"Regarding attractions and activities in {self.travel_request.to_location}: {modification_request}")
            elif any(word in modification_request.lower() for word in ['weather', 'climate', 'season', 'time']):
                response = self.weather_agent.query(f"Regarding weather and timing for {self.travel_request.to_location}: {modification_request}")
            else:
                # General query - use the most appropriate agent or coordinate
                response = f"Let me address your question: {modification_request}"
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(f"As a travel expert, please answer this question about traveling to {self.travel_request.to_location}: {modification_request}")
                response = response.text
            
            print(f"\n📝 UPDATED INFORMATION:")
            print("─" * 40)
            print(response)
            
            # Ask if they want more changes
            more_changes = input(f"\n🔄 Any other modifications needed? (yes/no): ").strip().lower()
            if more_changes in ['yes', 'y']:
                return self.handle_plan_modifications()
        
        print(f"\n🎯 Your personalized travel plan is complete! Have an amazing trip! 🧳✈️")
        return True

# ======================
# UTILITY FUNCTIONS
# ======================

def save_travel_plan(travel_request: TravelRequest, plan_content: str):
    """Save the travel plan to a file."""
    filename = f"travel_plan_{travel_request.to_location.replace(' ', '_').replace(',', '')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("🌍 AI TRAVEL PLANNER - PERSONALIZED ITINERARY 🌍\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("TRIP DETAILS:\n")
            f.write(f"From: {travel_request.from_location}\n")
            f.write(f"To: {travel_request.to_location}\n")
            f.write(f"Dates: {', '.join(travel_request.preferred_dates or ['TBD'])}\n")
            f.write(f"Duration: {travel_request.duration_days} days\n")
            f.write(f"Budget: {travel_request.budget_range}\n")
            f.write(f"Accommodation: {travel_request.accommodation_type}\n")
            f.write(f"Interests: {', '.join(travel_request.interests or [])}\n")
            f.write(f"Time preference: {travel_request.time_preference}\n\n")
            
            f.write("DETAILED PLAN:\n")
            f.write("="*40 + "\n")
            f.write(plan_content)
        
        print(f"\n💾 Travel plan saved to: {filename}")
        return filename
    
    except Exception as e:
        print(f"❌ Error saving travel plan: {str(e)}")
        return None

def get_travel_checklist(destination: str, duration_days: int, season: str) -> str:
    """Generate a travel checklist."""
    prompt = f"""Create a comprehensive travel checklist for a {duration_days}-day trip to {destination} during {season}.

Include:
1. Documents needed (passport, visa, etc.)
2. Packing essentials for the season
3. Health and safety preparations
4. Technology and communication needs
5. Money and banking considerations
6. Pre-travel preparations
7. Emergency contacts and backup plans

Make it practical and actionable."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating checklist: {str(e)}"

def estimate_total_budget(travel_request: TravelRequest, expert_analyses: Dict) -> str:
    """Estimate total travel budget based on expert analyses."""
    prompt = f"""As a travel budget expert, estimate the total cost for this trip:

Trip Details:
- Destination: {travel_request.from_location} to {travel_request.to_location}
- Duration: {travel_request.duration_days} days
- Budget range: {travel_request.budget_range}
- Accommodation: {travel_request.accommodation_type}
- Interests: {', '.join(travel_request.interests or [])}

Provide:
1. Flight cost estimates
2. Accommodation cost per night and total
3. Daily food and dining costs
4. Activities and attractions costs
5. Local transportation costs
6. Shopping and miscellaneous expenses
7. Total estimated budget range
8. Money-saving tips specific to this destination

Give realistic price ranges in USD."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error estimating budget: {str(e)}"

# ======================
# ENHANCED MAIN EXECUTION
# ======================

def main():
    """Enhanced main function with additional features."""
    try:
        print("🚀 Starting AI Travel Planner...")
        
        coordinator = TravelPlannerCoordinator()
        
        # Start the conversation
        plan_completed = coordinator.start_conversation()
        
        if plan_completed:
            # Additional services
            print(f"\n🎁 BONUS SERVICES:")
            print("─" * 30)
            
            # Travel checklist
            checklist_request = input("📋 Would you like a personalized travel checklist? (yes/no): ").strip().lower()
            if checklist_request in ['yes', 'y']:
                print("\n📋 TRAVEL CHECKLIST:")
                print("─" * 30)
                
                # Determine season from dates
                season = "current season"  # Default
                if coordinator.travel_request.preferred_dates:
                    try:
                        month = int(coordinator.travel_request.preferred_dates[0].split('-')[1])
                        if month in [12, 1, 2]:
                            season = "winter"
                        elif month in [3, 4, 5]:
                            season = "spring"
                        elif month in [6, 7, 8]:
                            season = "summer"
                        else:
                            season = "autumn"
                    except:
                        pass
                
                checklist = get_travel_checklist(
                    coordinator.travel_request.to_location, 
                    coordinator.travel_request.duration_days,
                    season
                )
                print(checklist)
            
            # Budget estimate
            budget_request = input(f"\n💰 Would you like a detailed budget breakdown? (yes/no): ").strip().lower()
            if budget_request in ['yes', 'y']:
                print("\n💰 BUDGET BREAKDOWN:")
                print("─" * 30)
                
                budget_analysis = estimate_total_budget(coordinator.travel_request, {})
                print(budget_analysis)
            
            # Save plan option
            save_request = input(f"\n💾 Would you like to save your travel plan to a file? (yes/no): ").strip().lower()
            if save_request in ['yes', 'y']:
                # Compile all information into a comprehensive plan
                plan_content = f"""
TRAVEL REQUEST SUMMARY:
{coordinator.travel_request.__dict__}

AGENT CONSULTATION HISTORY:
Weather Agent Calls: {len(coordinator.weather_agent.history['calls'])}
Booking Agent Calls: {len(coordinator.booking_agent.history['calls'])}
Route Agent Calls: {len(coordinator.route_agent.history['calls'])}
Attractions Agent Calls: {len(coordinator.attractions_agent.history['calls'])}

Generated by AI Travel Planner on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                save_travel_plan(coordinator.travel_request, plan_content)
        
        print(f"\n✨ Thank you for using AI Travel Planner!")
        print("🌍 Wishing you safe travels and amazing adventures! 🧳")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 Travel planning cancelled. Feel free to come back anytime!")
        print("🌍 The world is waiting for you!")
        
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        print("🔧 Please try running the planner again.")
        print("💡 If the problem persists, check your GEMINI_API_KEY in your .env file.")

def quick_start_demo():
    """Quick demo version for testing."""
    print("🌍 AI Travel Planner - Quick Demo Mode")
    print("="*40)
    
    # Create a sample travel request
    demo_request = TravelRequest(
        from_location="Sydney",
        to_location="Hong Kong",
        preferred_dates=["2025-06-15", "2025-06-18"],
        duration_days=3,
        interests=["nightlife", "food", "beach"],
        budget_range="medium",
        accommodation_type="hotel",
        time_preference="mixed"
    )
    
    coordinator = TravelPlannerCoordinator()
    coordinator.travel_request = demo_request
    
    print("Running demo with sample data...")
    print(f"Trip: {demo_request.from_location} → {demo_request.to_location}")
    print(f"Duration: {demo_request.duration_days} days")
    print(f"Interests: {', '.join(demo_request.interests)}")
    
    # Run a quick analysis
    print("\n🔍 Getting quick recommendations...")
    
    # Call the agent with explicit parameters including duration_days
    attractions_analysis = coordinator.attractions_agent.query(
        f"Create a {demo_request.duration_days}-day itinerary for {demo_request.to_location} "
        f"focusing on {', '.join(demo_request.interests)}. The trip is exactly {demo_request.duration_days} days long, "
        f"not more, not less. Provide recommendations that fit within {demo_request.duration_days} days only."
    )
    
    print(f"\n🎨 SAMPLE {demo_request.duration_days}-DAY ATTRACTIONS ANALYSIS:")
    print("─" * 40)
    print(attractions_analysis)
    
    print(f"\n✅ Demo completed! Run main() for the full interactive experience.")

if __name__ == "__main__":
    # Uncomment the next line for a quick demo
    #quick_start_demo()
    
    # Run the full interactive planner
    main()
