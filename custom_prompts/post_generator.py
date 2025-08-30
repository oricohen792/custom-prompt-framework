#!/usr/bin/env python3
"""
Post Generator Test using Unified Framework
Prompt: "Generate new social media posts based on analyzed data patterns"
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'base_class'))
from unified_prompt_tester import UnifiedPromptTester, BaseDataOrganizer

class PostGeneratorDataOrganizer(BaseDataOrganizer):
    """Organizes posts data to generate new social media posts based on patterns"""
    
    def __init__(self):
        self.analysis_purpose = "Generate new social media posts based on analyzed data patterns"
        self.test_name = "post_generator"
        self.max_posts_to_process = 100
    
    def organize_data(self, posts):
        """Organize posts data to generate new social media posts"""
        # Limit posts to prevent context overflow
        if len(posts) > self.max_posts_to_process:
            posts = posts[:self.max_posts_to_process]
        
        organized_data = {
            "total_posts": len(posts),
            "content_patterns": {},
            "engagement_insights": {},
            "post_suggestions": {}
        }
        
        # Analyze content patterns
        content_types = []
        hashtag_patterns = []
        emoji_usage = []
        engagement_metrics = []
        
        for post in posts:
            content = post.get('content', '')
            metadata = post.get('metadata', {})
            
            # Basic metrics
            likes = metadata.get('likes_count', 0) or 0
            views = metadata.get('views', 0) or 0
            shares = metadata.get('shares', 0) or 0
            comments = metadata.get('comments_count', 0) or 0
            
            # Content analysis
            content_types.append({
                "content": content,
                "word_count": len(content.split()),
                "hashtag_count": content.count('#'),
                "emoji_count": sum(1 for char in content if ord(char) > 127),
                "has_question": '?' in content,
                "has_exclamation": '!' in content,
                "has_video": 'video_url' in post and post['video_url'],
                "engagement": likes + views + shares + comments
            })
            
            # Track hashtag patterns
            if '#' in content:
                hashtag_patterns.append(content.count('#'))
            
            # Track emoji usage
            emoji_count = sum(1 for char in content if ord(char) > 127)
            emoji_usage.append(emoji_count)
            
            # Track engagement
            engagement_metrics.append({
                "likes": likes,
                "views": views,
                "shares": shares,
                "comments": comments,
                "total": likes + views + shares + comments
            })
        
        # Calculate averages and patterns
        avg_word_count = sum(p['word_count'] for p in content_types) / len(content_types)
        avg_hashtags = sum(hashtag_patterns) / len(hashtag_patterns) if hashtag_patterns else 0
        avg_emojis = sum(emoji_usage) / len(emoji_usage) if emoji_usage else 0
        
        # Find top performing content
        top_performers = sorted(content_types, key=lambda x: x['engagement'], reverse=True)[:10]
        
        organized_data["content_patterns"] = {
            "average_word_count": round(avg_word_count, 1),
            "average_hashtags": round(avg_hashtags, 1),
            "average_emojis": round(avg_emojis, 1),
            "question_usage": sum(1 for p in content_types if p['has_question']),
            "exclamation_usage": sum(1 for p in content_types if p['has_exclamation']),
            "video_usage": sum(1 for p in content_types if p['has_video'])
        }
        
        organized_data["engagement_insights"] = {
            "top_performing_posts": top_performers,
            "engagement_distribution": {
                "high": len([e for e in engagement_metrics if e['total'] > 1000]),
                "medium": len([e for e in engagement_metrics if 100 <= e['total'] <= 1000]),
                "low": len([e for e in engagement_metrics if e['total'] < 100])
            }
        }
        
        print(f"📊 Organized data for post generation:")
        print(f"   - Total posts analyzed: {len(posts)}")
        print(f"   - Average word count: {round(avg_word_count, 1)}")
        print(f"   - Average hashtags: {round(avg_hashtags, 1)}")
        print(f"   - Average emojis: {round(avg_emojis, 1)}")
        print(f"   - Top performing posts: {len(top_performers)}")
        
        return organized_data
    
    def get_prompt(self):
        """Get the prompt for post generation"""
        prompt = """
You are a social media content strategist and post generator. Your task is to analyze the provided social media data and generate new, engaging post suggestions based on the patterns you discover.

**ANALYSIS OBJECTIVES:**
1. Identify successful content patterns from the data
2. Understand what drives engagement (likes, views, shares, comments)
3. Generate new post ideas that follow successful patterns
4. Provide optimization tips for better performance

**CONTENT GENERATION REQUIREMENTS:**
- Generate 5 new post ideas based on successful patterns
- Each post should follow the engagement patterns you identify
- Include hashtag suggestions based on data analysis
- Provide emoji usage recommendations
- Suggest optimal content length and structure

**POST ANALYSIS REQUIREMENTS:**
- Examine top-performing posts for common characteristics
- Identify hashtag patterns that drive engagement
- Analyze emoji usage and its impact on engagement
- Understand question vs. statement effectiveness
- Determine optimal content length for engagement

**OUTPUT FORMAT:**
1. **Content Pattern Analysis**: Summary of what makes posts successful
2. **Engagement Insights**: Key findings about what drives engagement
3. **New Post Suggestions**: 5 creative post ideas with explanations
4. **Optimization Tips**: Specific recommendations for better performance
5. **Hashtag Strategy**: Suggested hashtag combinations based on data

**POST SUGGESTIONS FORMAT:**
For each of the 5 new posts, provide:
- **Post Content**: Complete post text (Hebrew/English as appropriate)
- **Engagement Strategy**: Why this post should perform well
- **Hashtag Recommendations**: 3-5 relevant hashtags
- **Emoji Suggestions**: Appropriate emojis to include
- **Expected Performance**: Predicted engagement level

**TONE:**
- Creative and engaging
- Data-driven insights
- Actionable recommendations
- Focus on engagement optimization
"""
        
        instructions = """
1. Analyze the provided data thoroughly for content patterns and engagement drivers
2. Identify what makes top-performing posts successful
3. Generate 5 new post ideas that follow successful patterns
4. Provide specific hashtag and emoji recommendations
5. Include engagement optimization tips
6. Base all suggestions on actual data patterns
7. Focus on creating engaging, shareable content
8. Provide actionable insights for content creators
"""
        
        return prompt, instructions

def main():
    """Main function to run the post generator test"""
    try:
        print("🔍 Starting Post Generator Test...")
        
        # Create data organizer
        organizer = PostGeneratorDataOrganizer()
        
        # Run the test
        organizer.run_test()
        
        print("✅ Post Generator Test completed!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
