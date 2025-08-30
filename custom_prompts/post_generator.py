#!/usr/bin/env python3
"""
Post Generator using Unified Framework
Prompt: "Generate new social media posts based on analyzed data patterns"
Updated for new cleaned JSON format with Hebrew content generation
"""

import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'base_class'))
from unified_prompt_tester import UnifiedPromptTester, BaseDataOrganizer

class PostGeneratorDataOrganizer(BaseDataOrganizer):
    """Organizes posts data to generate new social media content"""
    
    def __init__(self, json_file=None):
        """Initialize with optional JSON file name"""
        super().__init__(json_file)
        self.analysis_purpose = "Generate new social media posts based on analyzed data patterns"
        self.test_name = "post_generator"
        self.max_posts_to_process = 100  # Process more posts for better pattern analysis
    
    def organize_data(self, posts):
        """Organize posts data to understand content patterns and engagement"""
        # Limit posts to prevent context overflow
        if len(posts) > self.max_posts_to_process:
            posts = posts[:self.max_posts_to_process]
        
        organized_data = {
            "total_posts": len(posts),
            "content_patterns": {},
            "engagement_metrics": {},
            "social_networks": {},
            "topics_themes": {},
            "writing_styles": {}
        }
        
        # Analyze content patterns and engagement
        total_likes = 0
        total_views = 0
        total_shares = 0
        total_comments = 0
        total_plays = 0
        total_saves = 0
        
        social_networks = {}
        content_lengths = []
        question_posts = 0
        exclamation_posts = 0
        
        for post in posts:
            # New format: fields are directly on the post object
            content = post.get('content', '')
            social_network = post.get('social_network', 'unknown')
            
            # Basic metrics - directly from post object
            likes = post.get('likes_count', 0) or 0
            views = post.get('views', 0) or 0
            shares = post.get('shares', 0) or 0
            comments = post.get('comments_count', 0) or 0
            plays = post.get('plays', 0) or 0
            saves = post.get('saves', 0) or 0
            video_url = post.get('video_url', '')
            
            # Accumulate metrics
            total_likes += likes
            total_views += views
            total_shares += shares
            total_comments += comments
            total_plays += plays
            total_saves += saves
            
            # Track social networks
            if social_network not in social_networks:
                social_networks[social_network] = 0
            social_networks[social_network] += 1
            
            # Content analysis
            if content:
                content_lengths.append(len(content.split()))
                if '?' in content:
                    question_posts += 1
                if '!' in content:
                    exclamation_posts += 1
            
            # Calculate engagement score
            engagement = likes + views + shares + comments + plays + saves
            
            # Store post with engagement score
            post['engagement'] = engagement
        
        # Sort posts by engagement
        posts_by_engagement = sorted(posts, key=lambda x: x.get('engagement', 0), reverse=True)
        top_engaging_posts = posts_by_engagement[:20]
        
        # Calculate averages
        avg_likes = total_likes / len(posts) if posts else 0
        avg_views = total_views / len(posts) if posts else 0
        avg_shares = total_shares / len(posts) if posts else 0
        avg_comments = total_comments / len(posts) if posts else 0
        avg_plays = total_plays / len(posts) if posts else 0
        avg_saves = total_saves / len(posts) if posts else 0
        avg_content_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        
        # Organize the data
        organized_data["content_patterns"] = {
            "avg_content_length": round(avg_content_length, 1),
            "question_posts": question_posts,
            "exclamation_posts": exclamation_posts,
            "total_posts_with_content": len([p for p in posts if p.get('content')])
        }
        
        organized_data["engagement_metrics"] = {
            "avg_likes": round(avg_likes, 1),
            "avg_views": round(avg_views, 1),
            "avg_shares": round(avg_shares, 1),
            "avg_comments": round(avg_comments, 1),
            "avg_plays": round(avg_plays, 1),
            "avg_saves": round(avg_saves, 1),
            "total_engagement": total_likes + total_views + total_shares + total_comments + total_plays + total_saves
        }
        
        organized_data["social_networks"] = social_networks
        organized_data["top_engaging_posts"] = top_engaging_posts[:10]  # Top 10 most engaging posts
        
        print(f"📊 Organized data for post generation:")
        print(f"   - Total posts analyzed: {len(posts)}")
        print(f"   - Social networks: {', '.join(social_networks.keys())}")
        print(f"   - Average engagement: {round(organized_data['engagement_metrics']['total_engagement'] / len(posts), 1)}")
        print(f"   - Top engaging posts: {len(top_engaging_posts[:10])}")
        print(f"   - Average content length: {round(avg_content_length, 1)} words")
        
        return organized_data
    
    def get_prompt(self):
        """Get the prompt for post generation"""
        prompt = """
You are a social media content strategist and data analyst specializing in Hebrew content. Your task is to analyze the provided social media posts data and generate insights and recommendations for creating engaging Hebrew content.

**ANALYSIS OBJECTIVES:**
1. Identify successful content patterns from the data
2. Understand what drives engagement (likes, views, shares, comments, plays, saves)
3. Generate new Hebrew post ideas that follow successful patterns
4. Provide optimization tips for better performance
5. Consider differences between social networks (Facebook, TikTok, etc.)

**ENGAGEMENT METRICS TO ANALYZE:**
- **Likes**: Measure of content appreciation
- **Views**: Content reach and visibility
- **Shares**: Content virality and audience engagement
- **Comments**: Audience interaction and discussion
- **Plays**: Video content engagement (TikTok)
- **Saves**: Content value and bookmarking behavior

**CONTENT PATTERNS TO IDENTIFY:**
- **Length**: Optimal content length for each platform
- **Tone**: Question-based vs. statement-based content
- **Style**: Use of exclamations, emojis, personal pronouns
- **Topics**: What themes generate the most engagement
- **Timing**: When posts perform best

**HEBREW CONTENT REQUIREMENTS:**
- **Language**: All generated posts must be in Hebrew (עברית)
- **Grammar**: Ensure proper Hebrew grammar and spelling
- **Cultural Context**: Use appropriate Hebrew expressions and cultural references
- **Hashtags**: Include Hebrew hashtags and relevant English hashtags
- **Tone**: Match the authentic Hebrew voice and style of the original posts

**OUTPUT REQUIREMENTS:**
1. **Data Summary**: Key statistics and insights from the analysis
2. **Engagement Analysis**: What drives high engagement based on the data
3. **Hebrew Content Strategy**: 5-7 specific Hebrew post ideas following successful patterns
4. **Platform Optimization**: Tips for each social network identified
5. **Performance Metrics**: What to track and measure for success

**HEBREW POST FORMAT:**
For each post idea, provide:
- **Post Content**: Complete post text in Hebrew
- **Target Platform**: Which social network this post is optimized for
- **Engagement Strategy**: Why this post should perform well
- **Hebrew Hashtags**: 3-5 relevant Hebrew hashtags
- **English Hashtags**: 2-3 relevant English hashtags for broader reach
- **Emoji Suggestions**: Appropriate emojis to include
- **Expected Performance**: Predicted engagement level

**CREATIVE APPROACH:**
- Base all recommendations on actual data patterns
- Provide specific, actionable Hebrew content ideas
- Consider platform-specific best practices
- Focus on engagement drivers identified in the data
- Suggest measurable improvements
- Use authentic Hebrew language and cultural expressions
- Ensure posts feel natural and engaging for Hebrew-speaking audiences
"""
        
        instructions = """
1. Analyze the engagement metrics to identify what drives success
2. Examine content patterns in high-performing posts
3. Generate specific Hebrew post ideas based on successful patterns
4. Provide platform-specific optimization tips
5. Create actionable recommendations for content improvement
6. Base all suggestions on the actual data provided
7. Focus on measurable engagement factors
8. Consider the social network context for each recommendation
9. Write all post content in proper Hebrew with correct grammar
10. Include both Hebrew and English hashtags for maximum reach
11. Ensure cultural appropriateness for Hebrew-speaking audiences
"""
        
        return prompt, instructions

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Post Generator')
    parser.add_argument('--json-file', '-j', 
                       default='processed_posts.json',
                       help='JSON file name to load from data folder (default: processed_posts.json)')
    parser.add_argument('--list-files', '-l', 
                       action='store_true',
                       help='List available JSON files in data folder')
    return parser.parse_args()

def main():
    """Main function to run the post generator test"""
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
        
        print("🔍 Starting Post Generator Test...")
        print(f"📁 Using data file: {args.json_file}")
        
        # Create data organizer with specified JSON file
        organizer = PostGeneratorDataOrganizer(json_file=args.json_file)
        
        # Run the test
        organizer.run_test()
        
        print("✅ Post Generator Test completed!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
