#!/usr/bin/env python3
"""
Unified Prompt Tester Framework
A unified framework for testing custom AI prompts with social media data
"""

import os
import json
import openai
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.config import Settings
import uuid
from datetime import datetime

# Load environment variables
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.env')
load_dotenv(config_path)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class BaseDataOrganizer(ABC):
    """Abstract base class for data organization strategies"""
    
    @abstractmethod
    def organize_data(self, posts):
        """Organize posts data according to specific strategy"""
        pass
    
    @abstractmethod
    def get_prompt(self):
        """Get the prompt and instructions for the AI"""
        pass
    
    def run_test(self):
        """Run the complete test using the unified framework"""
        try:
            print(f"🚀 Starting {self.test_name} test...")
            
            # Load posts data
            posts = self._load_posts()
            if not posts:
                print("❌ No posts data found!")
                return
            
            print(f"📊 Loaded {len(posts)} posts for analysis")
            
            # Organize data according to strategy
            organized_data = self.organize_data(posts)
            
            # Create vector store
            vector_store_id = self._create_vector_store(organized_data)
            
            # Get prompt and instructions
            prompt, instructions = self.get_prompt()
            
            # Run AI analysis
            ai_response = self._run_ai_analysis(prompt, instructions, vector_store_id)
            
            # Save results
            self._save_results(ai_response, vector_store_id)
            
            print(f"✅ {self.test_name} test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error in {self.test_name} test: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_posts(self):
        """Load posts data from JSON file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed_posts.json')
            if not os.path.exists(data_path):
                print(f"❌ Data file not found: {data_path}")
                return []
            
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filter out posts with unknown networks
            filtered_posts = []
            for post in data:
                network = post.get('network', '').lower()
                if network not in ['unknown', '']:
                    filtered_posts.append(post)
            
            print(f"📊 Loaded {len(filtered_posts)} posts (filtered from {len(data)} total)")
            return filtered_posts
            
        except Exception as e:
            print(f"❌ Error loading posts: {e}")
            return []
    
    def _create_vector_store(self, organized_data):
        """Create a vector store for the organized data"""
        try:
            # Create results directory if it doesn't exist
            results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            # Generate unique ID for this test
            test_id = str(uuid.uuid4())[:8]
            vector_store_id = f"{self.test_name}_{test_id}"
            
            # Convert organized data to text for vector storage
            data_text = json.dumps(organized_data, ensure_ascii=False, indent=2)
            
            # For now, we'll just save the data text to a file
            # In a full implementation, you'd use a proper vector database
            vector_file = os.path.join(results_dir, f"{vector_store_id}_data.json")
            with open(vector_file, 'w', encoding='utf-8') as f:
                json.dump(organized_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Created vector store: {vector_store_id}")
            return vector_store_id
            
        except Exception as e:
            print(f"❌ Error creating vector store: {e}")
            return f"{self.test_name}_error"
    
    def _run_ai_analysis(self, prompt, instructions, vector_store_id):
        """Run AI analysis using OpenAI API"""
        try:
            print("🤖 Running AI analysis...")
            
            # Load the organized data for context
            results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
            vector_file = os.path.join(results_dir, f"{vector_store_id}_data.json")
            
            with open(vector_file, 'r', encoding='utf-8') as f:
                organized_data = json.load(f)
            
            # Create the full prompt with data context
            full_prompt = f"""
{prompt}

**ANALYSIS DATA:**
{json.dumps(organized_data, ensure_ascii=False, indent=2)}

**INSTRUCTIONS:**
{instructions}

Please analyze the provided data and provide a comprehensive response following the requirements above.
"""
            
            # Make API call to OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional data analyst and content creator. Analyze the provided data thoroughly and provide detailed, actionable insights."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            print("✅ AI analysis completed successfully!")
            return ai_response
            
        except Exception as e:
            print(f"❌ Error in AI analysis: {e}")
            return f"Error in AI analysis: {str(e)}"
    
    def _save_results(self, ai_response, vector_store_id):
        """Save AI response and results"""
        try:
            results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
            
            # Save AI response
            response_file = os.path.join(results_dir, f"{self.test_name}_ai_response.txt")
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(f"Test: {self.test_name}\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Vector Store ID: {vector_store_id}\n")
                f.write("=" * 50 + "\n\n")
                f.write(ai_response)
            
            print(f"💾 Results saved to: {response_file}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")

class UnifiedPromptTester:
    """Main class for running unified prompt tests"""
    
    def __init__(self):
        self.data_organizers = {}
    
    def register_organizer(self, name, organizer):
        """Register a data organizer"""
        if isinstance(organizer, BaseDataOrganizer):
            self.data_organizers[name] = organizer
            print(f"✅ Registered organizer: {name}")
        else:
            print(f"❌ Invalid organizer: {name} must inherit from BaseDataOrganizer")
    
    def run_test(self, organizer_name):
        """Run a specific test"""
        if organizer_name in self.data_organizers:
            self.data_organizers[organizer_name].run_test()
        else:
            print(f"❌ Organizer not found: {organizer_name}")
            print(f"Available organizers: {list(self.data_organizers.keys())}")
    
    def list_tests(self):
        """List all available tests"""
        print("📋 Available tests:")
        for name, organizer in self.data_organizers.items():
            print(f"  - {name}: {organizer.analysis_purpose}")
    
    def run_all_tests(self):
        """Run all registered tests"""
        print("🚀 Running all tests...")
        for name in self.data_organizers:
            print(f"\n{'='*50}")
            self.run_test(name)

# Example usage
if __name__ == "__main__":
    print("🔧 Unified Prompt Tester Framework")
    print("This is the base framework for custom prompt testing.")
    print("Import this module to create custom data organizers.")
