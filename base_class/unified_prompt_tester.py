#!/usr/bin/env python3
"""
Unified Prompt Tester Framework
A unified framework for testing custom AI prompts with social media data
"""

import os
import json
import openai
import argparse
import sys
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from openai import OpenAI
import uuid
from datetime import datetime

# Load environment variables
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.env')
load_dotenv(config_path)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class BaseDataOrganizer(ABC):
    """Abstract base class for data organization strategies"""
    
    def __init__(self, json_file=None):
        """Initialize with optional JSON file name"""
        self.json_file = json_file or 'processed_posts.json'
    
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
            ai_response = self._run_ai_analysis(prompt, instructions, vector_store_id, organized_data)
            
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
            # Use the specified JSON file or default to processed_posts.json
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', self.json_file)
            if not os.path.exists(data_path):
                print(f"❌ Data file not found: {data_path}")
                print(f"💡 Available files in data folder:")
                self._list_available_data_files()
                return []
            
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Accept all posts for now
            filtered_posts = data
            
            print(f"📊 Loaded {len(filtered_posts)} posts from {self.json_file} (filtered from {len(data)} total)")
            return filtered_posts
            
        except Exception as e:
            print(f"❌ Error loading posts from {self.json_file}: {e}")
            return []
    
    def _list_available_data_files(self):
        """List available JSON files in the data folder"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            if os.path.exists(data_dir):
                json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
                if json_files:
                    for file in json_files:
                        print(f"   - {file}")
                else:
                    print("   No JSON files found in data folder")
            else:
                print(f"   Data folder not found: {data_dir}")
        except Exception as e:
            print(f"   Error listing data files: {e}")
    
    def _create_vector_store(self, organized_data):
        """Create a vector store for the organized data"""
        try:
            # Create results directory if it doesn't exist
            results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            # Generate unique ID for this test
            test_id = str(uuid.uuid4())[:8]
            vector_store_id = f"{self.test_name}_{test_id}"
            
            # Don't save JSON files - just return the ID
            print(f"💾 Created vector store ID: {vector_store_id}")
            return vector_store_id
            
        except Exception as e:
            print(f"❌ Error creating vector store: {e}")
            return f"{self.test_name}_error"
    
    def _run_ai_analysis(self, prompt, instructions, vector_store_id, organized_data):
        """Run AI analysis using OpenAI API"""
        try:
            print("🤖 Running AI analysis...")
            
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
            
            # Create filename with JSON data source included
            json_name = os.path.splitext(self.json_file)[0]  # Remove .json extension
            response_file = os.path.join(results_dir, f"{self.test_name}_{json_name}_ai_response.txt")
            
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(f"Test: {self.test_name}\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Vector Store ID: {vector_store_id}\n")
                f.write(f"Data Source: {self.json_file}\n")
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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Unified Prompt Tester Framework')
    parser.add_argument('--json-file', '-j', 
                       default='processed_posts.json',
                       help='JSON file name to load from data folder (default: processed_posts.json)')
    parser.add_argument('--list-files', '-l', 
                       action='store_true',
                       help='List available JSON files in data folder')
    return parser.parse_args()

# Example usage
if __name__ == "__main__":
    args = parse_arguments()
    
    if args.list_files:
        # List available data files
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        if os.path.exists(data_dir):
            json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
            if json_files:
                print("📁 Available JSON files in data folder:")
                for file in json_files:
                    print(f"   - {file}")
            else:
                print("📁 No JSON files found in data folder")
        else:
            print(f"📁 Data folder not found: {data_dir}")
    else:
        print("🔧 Unified Prompt Tester Framework")
        print(f"Default JSON file: {args.json_file}")
        print("This is the base framework for custom prompt testing.")
        print("Import this module to create custom data organizers.")
        print("\nUsage examples:")
        print("  python unified_prompt_tester.py --json-file processed_posts1.json")
        print("  python unified_prompt_tester.py --list-files")
