#!/usr/bin/env python3
"""
Opening Sentences Generator using Unified Framework
Prompt: "Suggest 3 opening sentences if you will meet this person according to most active posts content"
Generates personalized conversation starters based on social media analysis
"""

import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'base_class'))
from unified_prompt_tester import UnifiedPromptTester, BaseDataOrganizer

class OpeningSentencesDataOrganizer(BaseDataOrganizer):
    """Organizes posts data to generate opening sentences for meeting the person"""
    
    def __init__(self, json_file=None):
        """Initialize with optional JSON file name"""
        super().__init__(json_file)
        self.analysis_purpose = "Suggest 3 opening sentences if you will meet this person according to most active posts content"
        self.test_name = "opening_sentences"
        self.max_posts_to_process = 30  # Focus on most relevant posts
    
    def organize_data(self, posts):
        """Organize posts data to identify most active content and themes"""
        # Sort posts by engagement (likes + comments) to find most active
        for post in posts:
            post['engagement_score'] = post.get('likes_count', 0) + post.get('comments_count', 0)
        
        # Get top 10 most engaging posts
        top_posts = sorted(posts, key=lambda x: x.get('engagement_score', 0), reverse=True)[:10]
        
        # Get recent posts (last 20) to see current interests
        recent_posts = sorted(posts, key=lambda x: x.get('post_time', ''), reverse=True)[:20]
        
        # Analyze content themes from most active posts
        active_content = []
        for post in top_posts:
            content = post.get('content', '')
            if content:
                active_content.append({
                    'content': content[:200],  # First 200 chars
                    'engagement': post.get('engagement_score', 0),
                    'platform': post.get('social_network', ''),
                    'time': post.get('post_time', ''),
                    'likes': post.get('likes_count', 0),
                    'comments': post.get('comments_count', 0)
                })
        
        # Identify key themes and interests
        all_active_text = ' '.join([post.get('content', '') for post in top_posts if post.get('content')])
        
        themes = {
            "music": all_active_text.lower().count('music') + all_active_text.lower().count('song') + all_active_text.lower().count('concert'),
            "sports": all_active_text.lower().count('sport') + all_active_text.lower().count('game') + all_active_text.lower().count('team'),
            "politics": all_active_text.lower().count('politics') + all_active_text.lower().count('government') + all_active_text.lower().count('policy'),
            "family": all_active_text.lower().count('family') + all_active_text.lower().count('children') + all_active_text.lower().count('home'),
            "work": all_active_text.lower().count('work') + all_active_text.lower().count('career') + all_active_text.lower().count('business'),
            "travel": all_active_text.lower().count('travel') + all_active_text.lower().count('trip') + all_active_text.lower().count('vacation'),
            "food": all_active_text.lower().count('food') + all_active_text.lower().count('restaurant') + all_active_text.lower().count('cooking'),
            "technology": all_active_text.lower().count('tech') + all_active_text.lower().count('innovation') + all_active_text.lower().count('digital'),
            "fashion": all_active_text.lower().count('fashion') + all_active_text.lower().count('style') + all_active_text.lower().count('clothing'),
            "health": all_active_text.lower().count('health') + all_active_text.lower().count('fitness') + all_active_text.lower().count('wellness')
        }
        
        # Get top 3 themes
        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:3]
        
        organized_data = {
            "total_posts": len(posts),
            "most_active_posts": active_content,
            "top_themes": top_themes,
            "recent_posts": recent_posts[:5],  # Last 5 posts
            "engagement_summary": {
                "highest_engagement": max([post.get('engagement_score', 0) for post in posts]),
                "average_engagement": sum([post.get('engagement_score', 0) for post in posts]) / len(posts) if posts else 0
            }
        }
        
        return organized_data
    
    def get_prompt(self):
        """Get the prompt and instructions for the AI"""
        prompt = """
**OPENING SENTENCES GENERATOR**

You are analyzing social media data to create 3 natural, personalized opening sentences for meeting this person in real life.

**TASK:**
Generate exactly 3 opening sentences you could use when meeting this person, based on their most active and engaging social media content.

**ANALYSIS FOCUS:**
- **Most Active Posts**: Posts with highest likes + comments (most engaging)
- **Content Themes**: What topics they post about most frequently
- **Recent Activity**: What they've been discussing lately
- **Engagement Patterns**: What content gets the most response from their audience

**OPENING SENTENCE REQUIREMENTS:**
1. **First Sentence**: Reference their most popular/engaging content or main interest
2. **Second Sentence**: Comment on their recent activity or current focus
3. **Third Sentence**: Ask a question about their expertise or passion area

**CONVERSATION STYLE:**
- **Natural and Authentic**: Sound like a real person, not a script
- **Respectful**: Be appropriate for the context and their public persona
- **Specific**: Reference actual things from their social media
- **Engaging**: Make them want to respond and continue the conversation
- **Personal**: Show you've actually paid attention to their content

**OUTPUT FORMAT:**
Provide exactly 3 opening sentences, each on a new line, numbered 1-3:

1. [First opening sentence referencing their most engaging content]
2. [Second opening sentence about their recent activity]
3. [Third opening sentence asking about their expertise/passion]

**CREATIVE APPROACH:**
- Use their actual interests and recent activities
- Make the conversation feel natural and unforced
- Show genuine interest in what matters to them
- Create opportunities for them to share and engage
- Build on their communication style and preferences
"""

        instructions = """
1. Analyze their most engaging posts (highest likes + comments)
2. Identify their main content themes and interests
3. Look at their recent posts to understand current focus
4. Create 3 natural, authentic opening sentences
5. Reference specific things from their actual content
6. Make each sentence feel like a real conversation starter
7. Ensure the approach is respectful and appropriate
8. Focus on building genuine connection and interest
9. Use their actual interests and activities
10. Make it feel like you've actually followed their content
"""
        
        return prompt, instructions

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Opening Sentences Generator')
    parser.add_argument('--json-file', '-j', 
                       default='processed_posts.json',
                       help='JSON file name to load from data folder (default: processed_posts.json)')
    parser.add_argument('--list-files', '-l', 
                       action='store_true',
                       help='List available JSON files in data folder')
    return parser.parse_args()

def main():
    """Main function to run the opening sentences generator test"""
    try:
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
            return
        
        print("🔍 Starting Opening Sentences Generator Test...")
        print(f"📁 Using data file: {args.json_file}")
        
        # Create data organizer with specified JSON file
        organizer = OpeningSentencesDataOrganizer(json_file=args.json_file)
        
        # Run the test
        organizer.run_test()
        
        print("✅ Opening Sentences Generator Test completed!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
