#!/usr/bin/env python3
"""
Cake Landing Page Generator Test using Unified Framework
Prompt: "Create a simple landing page based on cake-related posts, replies, and engagement stats"
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'base_class'))
from unified_prompt_tester import UnifiedPromptTester, BaseDataOrganizer

class CakeLandingPageDataOrganizer(BaseDataOrganizer):
    """Organizes posts data to generate cake landing pages"""
    
    def __init__(self):
        self.analysis_purpose = "Create a simple landing page based on cake-related posts, replies, and engagement stats"
        self.test_name = "cake_landing_page"
        self.max_posts_to_process = 100
    
    def organize_data(self, posts):
        """Organize posts data to generate cake landing pages"""
        # Limit posts to prevent context overflow
        if len(posts) > self.max_posts_to_process:
            posts = posts[:self.max_posts_to_process]
        
        organized_data = {
            "total_posts": len(posts),
            "cake_content": {},
            "engagement_metrics": {},
            "landing_page_elements": {}
        }
        
        # Filter for cake-related content
        cake_posts = []
        cake_videos = []
        cake_images = []
        
        for post in posts:
            content = post.get('content', '')
            metadata = post.get('metadata', {})
            
            # Check if post is cake-related
            cake_keywords = ['עוגה', 'עוגיות', 'שוקולד', 'בישול', 'מתכון', 'cake', 'chocolate', 'baking', 'recipe']
            is_cake_related = any(keyword in content.lower() for keyword in cake_keywords)
            
            if is_cake_related:
                # Basic metrics
                likes = metadata.get('likes_count', 0) or 0
                views = metadata.get('views', 0) or 0
                shares = metadata.get('shares', 0) or 0
                comments = metadata.get('comments_count', 0) or 0
                replies = len(post.get('replies', [])) if post.get('replies') else 0
                
                cake_post = {
                    "content": content,
                    "engagement": {
                        "likes": likes,
                        "views": views,
                        "shares": shares,
                        "comments": comments,
                        "replies": replies,
                        "total": likes + views + shares + comments + replies
                    },
                    "has_video": 'video_url' in post and post['video_url'],
                    "has_image": 'image_url' in post and post['image_url']
                }
                
                cake_posts.append(cake_post)
                
                # Track media content
                if cake_post['has_video']:
                    cake_videos.append(cake_post)
                if cake_post['has_image']:
                    cake_images.append(catch_post)
        
        # Calculate engagement metrics
        total_likes = sum(post['engagement']['likes'] for post in cake_posts)
        total_views = sum(post['engagement']['views'] for post in cake_posts)
        total_shares = sum(post['engagement']['shares'] for post in cake_posts)
        total_comments = sum(post['engagement']['comments'] for post in cake_posts)
        total_replies = sum(post['engagement']['replies'] for post in cake_posts)
        total_saves = sum(post['engagement'].get('saves', 0) for post in cake_posts)
        total_plays = sum(post['engagement'].get('plays', 0) for post in cake_posts)
        
        # Find top performing cake content
        top_performing_content = sorted(cake_posts, key=lambda x: x['engagement']['total'], reverse=True)[:5]
        
        # Categorize content
        content_categories = {
            "recipes": len([p for p in cake_posts if 'מתכון' in p['content'] or 'recipe' in p['content'].lower()]),
            "chocolate": len([p for p in cake_posts if 'שוקולד' in p['content'] or 'chocolate' in p['content'].lower()]),
            "baking_tips": len([p for p in cake_posts if 'טיפ' in p['content'] or 'tip' in p['content'].lower()]),
            "decorations": len([p for p in cake_posts if 'עיצוב' in p['content'] or 'decoration' in p['content'].lower()]),
            "general": len([p for p in cake_posts if not any(word in p['content'] for word in ['מתכון', 'recipe', 'שוקולד', 'chocolate', 'טיפ', 'tip', 'עיצוב', 'decoration'])])
        }
        
        organized_data["cake_content"] = {
            "total_cake_posts": len(cake_posts),
            "videos": len(cake_videos),
            "images": len(cake_images),
            "top_performing_content": top_performing_content,
            "content_categories": content_categories
        }
        
        organized_data["engagement_metrics"] = {
            "total_likes": total_likes,
            "total_views": total_views,
            "total_shares": total_shares,
            "total_comments": total_comments,
            "total_replies": total_replies,
            "total_saves": total_saves,
            "total_plays": total_plays,
            "average_engagement_per_post": round((total_likes + total_views + total_shares + total_comments + total_replies) / len(cake_posts), 1) if cake_posts else 0
        }
        
        organized_data["landing_page_elements"] = {
            "hero_content": top_performing_content[0] if top_performing_content else None,
            "featured_posts": top_performing_content[:3] if len(top_performing_content) >= 3 else top_performing_content,
            "content_themes": list(content_categories.keys()),
            "engagement_highlights": {
                "most_liked": max(cake_posts, key=lambda x: x['engagement']['likes']) if cake_posts else None,
                "most_shared": max(cake_posts, key=lambda x: x['engagement']['shares']) if cake_posts else None,
                "most_commented": max(cake_posts, key=lambda x: x['engagement']['comments']) if cake_posts else None
            }
        }
        
        print(f"📊 Organized data for cake landing page generation:")
        print(f"   - Total posts analyzed: {len(posts)}")
        print(f"   - Cake-related posts found: {len(cake_posts)}")
        print(f"   - Top cake engagement scores: {[post['engagement']['total'] for post in top_performing_content[:5]]}")
        print(f"   - Cake categories: {content_categories}")
        print(f"   - Total cake replies: {total_replies}")
        
        return organized_data
    
    def get_prompt(self):
        """Get the prompt for cake landing page generation"""
        prompt = """
You are a professional web developer and content creator specializing in food-related landing pages. Your task is to create a simple landing page based on cake-related posts, replies, and engagement stats from the provided data.

**LANDING PAGE OBJECTIVES:**
1. Create a compelling landing page for cake-related content
2. Use actual engagement data to highlight successful content
3. Design a page that converts social media followers into customers
4. Focus on the most engaging cake content and themes

**LANDING PAGE REQUIREMENTS:**
- Create a complete landing page structure with all required sections
- Use actual data from the provided cake posts analysis
- Include compelling headlines and content sections
- Provide specific design and UX recommendations
- Focus on creating a page that converts followers into customers

**CONTENT SECTIONS REQUIRED:**
1. **Hero Section**: Compelling headline and main value proposition
2. **Featured Content**: Showcase top-performing cake posts
3. **Content Categories**: Organize by cake types and themes
4. **Engagement Proof**: Display actual engagement metrics
5. **Call-to-Action**: Clear next steps for visitors
6. **Social Proof**: Highlight successful content and engagement

**DATA INTEGRATION REQUIREMENTS:**
- Use actual engagement metrics (likes, views, shares, comments, replies)
- Feature the top 3-5 most engaging cake posts
- Include real content categories found in the data
- Display actual engagement statistics
- Reference specific successful content examples

**DESIGN RECOMMENDATIONS:**
- Provide specific design suggestions for each section
- Recommend color schemes and visual elements
- Suggest layout and navigation improvements
- Include mobile responsiveness considerations
- Recommend content optimization strategies

**OUTPUT FORMAT:**
1. **Landing Page Structure**: Complete page layout with sections
2. **Content Recommendations**: Specific content for each section
3. **Design Guidelines**: Visual and UX recommendations
4. **Conversion Strategy**: How to turn visitors into customers
5. **Content Strategy**: Recommendations for maintaining engagement

**TONE:**
- Professional and conversion-focused
- Data-driven insights
- Actionable recommendations
- Focus on business outcomes
"""
        
        instructions = """
1. Analyze the provided cake-related data thoroughly for content performance and engagement patterns
2. Study the top 10 cake posts to understand successful content elements and categories
3. Identify audience preferences, engagement drivers, and interaction patterns
4. Create a complete landing page structure with all required sections
5. Include compelling headlines, content sections, and CTAs based on data insights
6. Provide specific design and UX recommendations for optimal conversion
7. Include content strategy recommendations for maintaining engagement
8. Focus on creating a page that converts social media followers into customers
"""
        
        return prompt, instructions

def main():
    """Main function to run the cake landing page generator test"""
    try:
        print("🔍 Starting Cake Landing Page Generator Test...")
        
        # Create data organizer
        organizer = CakeLandingPageDataOrganizer()
        
        # Run the test
        organizer.run_test()
        
        print("✅ Cake Landing Page Generator Test completed!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
