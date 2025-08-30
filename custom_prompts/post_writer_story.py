#!/usr/bin/env python3
"""
Post Writer Story Generator using Unified Framework
Prompt: "Generate a 100-word story about the post writer based on longest posts content"
Updated for new cleaned JSON format
"""

import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'base_class'))
from unified_prompt_tester import UnifiedPromptTester, BaseDataOrganizer

class PostWriterStoryDataOrganizer(BaseDataOrganizer):
    """Organizes posts data to generate a story about the post writer based on longest content"""
    
    def __init__(self, json_file=None):
        """Initialize with optional JSON file name"""
        super().__init__(json_file)
        self.analysis_purpose = "Generate a 100-word story about the post writer based on longest posts content"
        self.test_name = "post_writer_story"
        self.max_posts_to_process = 50  # Focus on quality over quantity
    
    def organize_data(self, posts):
        """Organize posts data to understand the post writer's personality and style"""
        # Limit posts to prevent context overflow
        if len(posts) > self.max_posts_to_process:
            posts = posts[:self.max_posts_to_process]
        
        organized_data = {
            "total_posts": len(posts),
            "longest_posts": [],
            "writer_personality": {},
            "content_themes": {},
            "writing_style": {}
        }
        
        # Find the longest posts (most detailed content)
        post_lengths = []
        for post in posts:
            content = post.get('content', '')
            if content:
                word_count = len(content.split())
                post_lengths.append({
                    "content": content,
                    "word_count": word_count,
                    "post_time": post.get('post_time', ''),
                    "social_network": post.get('social_network', ''),
                    "engagement": post.get('likes_count', 0) + post.get('comments_count', 0) + post.get('shares', 0)
                })
        
        # Sort by word count and get top 10 longest posts
        longest_posts = sorted(post_lengths, key=lambda x: x['word_count'], reverse=True)[:10]
        
        # Analyze writing style and themes
        all_content = ' '.join([p['content'] for p in longest_posts])
        
        # Identify common themes
        themes = {
            "politics": all_content.count('ממשלה') + all_content.count('פוליטיקה') + all_content.count('מדינה'),
            "family": all_content.count('משפחה') + all_content.count('ילדים') + all_content.count('הורים'),
            "work": all_content.count('עבודה') + all_content.count('קריירה') + all_content.count('מקצוע'),
            "emotions": all_content.count('רגשות') + all_content.count('אהבה') + all_content.count('כעס'),
            "daily_life": all_content.count('יומיום') + all_content.count('חיים') + all_content.count('שגרה'),
            "social_issues": all_content.count('חברה') + all_content.count('צדק') + all_content.count('שוויון'),
            "personal_growth": all_content.count('צמיחה') + all_content.count('שינוי') + all_content.count('התפתחות')
        }
        
        # Analyze writing style characteristics
        writing_style = {
            "avg_word_count": sum(p['word_count'] for p in longest_posts) / len(longest_posts) if longest_posts else 0,
            "question_usage": sum(1 for p in longest_posts if '?' in p['content']),
            "exclamation_usage": sum(1 for p in longest_posts if '!' in p['content']),
            "emoji_usage": sum(1 for char in all_content if ord(char) > 127),
            "personal_pronouns": all_content.count('אני') + all_content.count('לי') + all_content.count('שלי'),
            "reflective_tone": all_content.count('חושב') + all_content.count('מרגיש') + all_content.count('נראה')
        }
        
        # Determine writer personality traits
        personality_traits = []
        if themes["politics"] > 5:
            personality_traits.append("politically engaged")
        if themes["family"] > 3:
            personality_traits.append("family-oriented")
        if themes["work"] > 3:
            personality_traits.append("career-focused")
        if themes["emotions"] > 5:
            personality_traits.append("emotionally expressive")
        if themes["daily_life"] > 10:
            personality_traits.append("observant of daily life")
        if themes["social_issues"] > 5:
            personality_traits.append("socially conscious")
        if themes["personal_growth"] > 3:
            personality_traits.append("growth-minded")
        
        if writing_style["personal_pronouns"] > 20:
            personality_traits.append("self-reflective")
        if writing_style["reflective_tone"] > 10:
            personality_traits.append("thoughtful")
        if writing_style["question_usage"] > 3:
            personality_traits.append("inquisitive")
        
        organized_data["longest_posts"] = longest_posts
        organized_data["content_themes"] = themes
        organized_data["writing_style"] = writing_style
        organized_data["writer_personality"] = {
            "traits": personality_traits,
            "primary_themes": sorted(themes.items(), key=lambda x: x[1], reverse=True)[:3],
            "writing_characteristics": writing_style
        }
        
        print(f"📊 Organized data for post writer story generation:")
        print(f"   - Total posts analyzed: {len(posts)}")
        print(f"   - Longest posts found: {len(longest_posts)}")
        print(f"   - Average word count of longest posts: {round(writing_style['avg_word_count'], 1)}")
        print(f"   - Writer personality traits: {', '.join(personality_traits[:5])}")
        print(f"   - Top themes: {', '.join([theme for theme, count in themes.items() if count > 5])}")
        
        return organized_data
    
    def get_prompt(self):
        """Get the prompt for post writer story generation"""
        prompt = """
You are a creative storyteller and social media analyst. Your task is to analyze the provided social media posts and create a compelling 100-word story about the person who wrote these posts.

**STORY CREATION OBJECTIVES:**
1. Analyze the longest and most detailed posts to understand the writer's personality
2. Identify recurring themes, writing style, and personal characteristics
3. Create a 100-word story that captures the essence of who this person is
4. Make the story engaging, relatable, and true to the writer's voice
5. Write the story in Hebrew with proper line breaks for poetic flow

**STORY REQUIREMENTS:**
- **Exact length**: 100 words (no more, no less)
- **Language**: Write the story in Hebrew (עברית)
- **Style**: Creative narrative that feels personal and authentic
- **Voice**: Should reflect the writer's actual personality and writing style
- **Content**: Based on themes and patterns found in their posts
- **Emotion**: Capture the emotional tone and depth of their writing
- **Format**: Use line breaks to create poetic flow and readability

**ANALYSIS FOCUS:**
- **Longest posts**: Focus on posts with the highest word count for detailed insights
- **Writing patterns**: Analyze question usage, personal pronouns, emotional expressions
- **Content themes**: Identify recurring topics (politics, family, work, emotions, etc.)
- **Personal voice**: Understand how they express themselves and what matters to them
- **Engagement style**: How they interact with their audience

**STORY STRUCTURE:**
- **Opening**: Introduce the writer in an engaging way
- **Body**: Show their personality through their writing and themes
- **Conclusion**: Give a sense of who they are as a person
- **Tone**: Match the emotional depth and style of their posts
- **Line breaks**: Use strategic line breaks to enhance the story's flow

**OUTPUT FORMAT:**
1. **Writer Analysis**: Brief summary of what you discovered about the writer
2. **Key Personality Traits**: 3-5 main characteristics identified
3. **The 100-Word Story (Hebrew)**: The creative story about the post writer in Hebrew with line breaks
4. **English Translation**: English version of the Hebrew story
5. **Story Explanation**: Why you chose these elements and how they reflect the data

**CREATIVE APPROACH:**
- Use the writer's own words and themes when possible
- Create a narrative that feels like it could be about them
- Balance creativity with authenticity to the data
- Make the story engaging and memorable
- Capture both their public persona and personal depth
- Write in beautiful, flowing Hebrew with natural line breaks
- Ensure the Hebrew text is grammatically correct and culturally appropriate
"""
        
        instructions = """
1. Thoroughly analyze the longest posts to understand the writer's personality
2. Identify key themes, writing patterns, and personal characteristics
3. Create a compelling 100-word story that captures their essence
4. Base the story on actual content patterns and themes from their posts
5. Make the story feel authentic and true to who they appear to be
6. Use creative storytelling while staying grounded in the data
7. Ensure the story is exactly 100 words
8. Write the story in Hebrew with proper line breaks for poetic flow
9. Provide an English translation of the Hebrew story
10. Provide clear analysis of why the story reflects their personality
"""
        
        return prompt, instructions

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Post Writer Story Generator')
    parser.add_argument('--json-file', '-j', 
                       default='processed_posts.json',
                       help='JSON file name to load from data folder (default: processed_posts.json)')
    parser.add_argument('--list-files', '-l', 
                       action='store_true',
                       help='List available JSON files in data folder')
    return parser.parse_args()

def main():
    """Main function to run the post writer story generator test"""
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
        
        print("🔍 Starting Post Writer Story Generator Test...")
        print(f"📁 Using data file: {args.json_file}")
        
        # Create data organizer with specified JSON file
        organizer = PostWriterStoryDataOrganizer(json_file=args.json_file)
        
        # Run the test
        organizer.run_test()
        
        print("✅ Post Writer Story Generator Test completed!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
