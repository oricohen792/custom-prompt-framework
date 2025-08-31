#!/usr/bin/env python3
"""
Workshop Finder using Unified Framework
Prompt: "Find and analyze workshops that the person suggests in their social network"
Updated for new cleaned JSON format
"""

import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'base_class'))
from unified_prompt_tester import UnifiedPromptTester, BaseDataOrganizer

class WorkshopFinderDataOrganizer(BaseDataOrganizer):
    """Organizes posts data to find workshops suggested by the person in their network"""
    
    def __init__(self, json_file=None):
        """Initialize with optional JSON file name"""
        super().__init__(json_file)
        self.analysis_purpose = "Find and analyze workshops that the person suggests in their social network"
        self.test_name = "workshop_finder"
        self.max_posts_to_process = 100  # Process more posts to find workshop mentions
    
    def organize_data(self, posts):
        """Organize posts data to identify workshop suggestions and recommendations"""
        # Limit posts to prevent context overflow
        if len(posts) > self.max_posts_to_process:
            posts = posts[:self.max_posts_to_process]
        
        organized_data = {
            "total_posts": len(posts),
            "workshop_mentions": [],
            "workshop_categories": {},
            "recommendation_patterns": {},
            "network_analysis": {},
            "workshop_details": {}
        }
        
        # Keywords related to workshops and learning
        workshop_keywords = [
            'סדנה', 'workshop', 'קורס', 'course', 'הדרכה', 'training',
            'למידה', 'learning', 'הכשרה', 'education', 'השתלמות', 'seminar',
            'מפגש', 'meeting', 'אירוע', 'event', 'הרצאה', 'lecture',
            'תרגול', 'practice', 'ניסיון', 'experience', 'מיומנות', 'skill'
        ]
        
        # Keywords for recommendations and suggestions
        recommendation_keywords = [
            'מומלץ', 'recommended', 'אני ממליץ', 'I recommend', 'שווה', 'worth it',
            'נהדר', 'great', 'מעולה', 'excellent', 'חובה', 'must', 'צריך', 'should',
            'אני אוהב', 'I love', 'אני נהנה', 'I enjoy', 'מוצלח', 'successful'
        ]
        
        workshop_mentions = []
        workshop_categories = {}
        recommendation_patterns = {}
        
        for post in posts:
            content = post.get('content', '')
            if not content:
                continue
                
            # Check for workshop-related content
            workshop_found = False
            workshop_type = None
            
            # Look for workshop keywords
            for keyword in workshop_keywords:
                if keyword.lower() in content.lower():
                    workshop_found = True
                    # Categorize the workshop type
                    if any(word in content.lower() for word in ['בישול', 'cooking', 'מתכון', 'recipe']):
                        workshop_type = 'cooking'
                    elif any(word in content.lower() for word in ['טכנולוגיה', 'technology', 'תכנות', 'programming']):
                        workshop_type = 'technology'
                    elif any(word in content.lower() for word in ['אמנות', 'art', 'יצירה', 'creativity']):
                        workshop_type = 'art'
                    elif any(word in content.lower() for word in ['ספורט', 'sport', 'כושר', 'fitness']):
                        workshop_type = 'fitness'
                    elif any(word in content.lower() for word in ['עסקים', 'business', 'יזמות', 'entrepreneurship']):
                        workshop_type = 'business'
                    elif any(word in content.lower() for word in ['בריאות', 'health', 'תזונה', 'nutrition']):
                        workshop_type = 'health'
                    else:
                        workshop_type = 'general'
                    break
            
            if workshop_found:
                # Check if it's a recommendation
                is_recommendation = any(keyword in content for keyword in recommendation_keywords)
                
                # Extract workshop details
                workshop_info = {
                    "content": content,
                    "post_time": post.get('post_time', ''),
                    "social_network": post.get('social_network', ''),
                    "engagement": post.get('likes_count', 0) + post.get('comments_count', 0) + post.get('shares', 0),
                    "is_recommendation": is_recommendation,
                    "workshop_type": workshop_type,
                    "word_count": len(content.split())
                }
                
                workshop_mentions.append(workshop_info)
                
                # Count workshop types
                if workshop_type not in workshop_categories:
                    workshop_categories[workshop_type] = 0
                workshop_categories[workshop_type] += 1
                
                # Count recommendation patterns
                if is_recommendation:
                    if 'positive' not in recommendation_patterns:
                        recommendation_patterns['positive'] = 0
                    recommendation_patterns['positive'] += 1
                else:
                    if 'informational' not in recommendation_patterns:
                        recommendation_patterns['informational'] = 0
                    recommendation_patterns['informational'] += 1
        
        # Analyze network patterns
        network_analysis = {
            "total_workshop_mentions": len(workshop_mentions),
            "recommendation_ratio": len([w for w in workshop_mentions if w['is_recommendation']]) / len(workshop_mentions) if workshop_mentions else 0,
            "most_engaged_workshop": max(workshop_mentions, key=lambda x: x['engagement']) if workshop_mentions else None,
            "average_engagement": sum(w['engagement'] for w in workshop_mentions) / len(workshop_mentions) if workshop_mentions else 0
        }
        
        # Extract specific workshop details
        workshop_details = {
            "cooking_workshops": [w for w in workshop_mentions if w['workshop_type'] == 'cooking'],
            "technology_workshops": [w for w in workshop_mentions if w['workshop_type'] == 'technology'],
            "art_workshops": [w for w in workshop_mentions if w['workshop_type'] == 'art'],
            "fitness_workshops": [w for w in workshop_mentions if w['workshop_type'] == 'fitness'],
            "business_workshops": [w for w in workshop_mentions if w['workshop_type'] == 'business'],
            "health_workshops": [w for w in workshop_mentions if w['workshop_type'] == 'health'],
            "general_workshops": [w for w in workshop_mentions if w['workshop_type'] == 'general']
        }
        
        organized_data["workshop_mentions"] = workshop_mentions
        organized_data["workshop_categories"] = workshop_categories
        organized_data["recommendation_patterns"] = recommendation_patterns
        organized_data["network_analysis"] = network_analysis
        organized_data["workshop_details"] = workshop_details
        
        print(f"🔍 Workshop Finder Analysis Results:")
        print(f"   - Total posts analyzed: {len(posts)}")
        print(f"   - Workshop mentions found: {len(workshop_mentions)}")
        print(f"   - Workshop categories: {', '.join([f'{cat}: {count}' for cat, count in workshop_categories.items()])}")
        print(f"   - Recommendations: {recommendation_patterns.get('positive', 0)} positive, {recommendation_patterns.get('informational', 0)} informational")
        print(f"   - Most engaged workshop: {network_analysis['most_engaged_workshop']['engagement'] if network_analysis['most_engaged_workshop'] else 0} interactions")
        
        return organized_data
    
    def get_prompt(self):
        """Get the prompt for workshop finding and analysis"""
        prompt = """
You are a social media analyst and workshop discovery specialist. Your task is to analyze the provided social media posts and identify workshops that the person suggests, recommends, or mentions in their network.

**WORKSHOP DISCOVERY OBJECTIVES:**
1. Find all mentions of workshops, courses, training sessions, and learning opportunities
2. Identify which workshops the person actively recommends to their network
3. Analyze the types of workshops they suggest and their preferences
4. Understand their role in workshop discovery and sharing
5. Provide actionable insights about workshop opportunities in their network

**ANALYSIS REQUIREMENTS:**
- **Workshop Identification**: Find all posts mentioning workshops, courses, training, etc.
- **Recommendation Analysis**: Determine which workshops they actively recommend
- **Category Classification**: Categorize workshops by type (cooking, technology, art, fitness, business, health, etc.)
- **Network Impact**: Analyze how they share workshop information with their network
- **Engagement Patterns**: Understand which workshop posts get the most engagement
- **Personal Preferences**: Identify what types of workshops they value most

**WORKSHOP CATEGORIES TO LOOK FOR:**
- **Cooking/Food**: Cooking classes, recipe workshops, food preparation
- **Technology**: Programming courses, tech workshops, digital skills
- **Art/Creativity**: Art classes, creative workshops, design courses
- **Fitness/Health**: Exercise classes, wellness workshops, nutrition courses
- **Business**: Entrepreneurship workshops, business skills, professional development
- **Personal Development**: Life skills, communication, leadership workshops
- **General Learning**: Educational events, seminars, knowledge sharing

**RECOMMENDATION PATTERNS TO ANALYZE:**
- **Active Recommendations**: Posts where they explicitly recommend workshops
- **Personal Experiences**: Sharing their own workshop experiences
- **Network Sharing**: Introducing workshops to their followers
- **Value Assessment**: How they evaluate and rate workshops
- **Engagement**: How their network responds to workshop suggestions

**OUTPUT FORMAT:**
1. **Workshop Discovery Summary**: Overview of workshops found and analyzed
2. **Workshop Categories Breakdown**: Detailed breakdown by workshop type
3. **Top Workshop Recommendations**: Most strongly recommended workshops
4. **Network Sharing Patterns**: How they share workshop information
5. **Personal Workshop Preferences**: What types of workshops they value most
6. **Actionable Insights**: Workshop opportunities and recommendations for their network

**ANALYSIS FOCUS:**
- **Content Analysis**: Look for workshop-related keywords and phrases
- **Recommendation Strength**: Assess how strongly they recommend workshops
- **Network Engagement**: Understand audience response to workshop content
- **Personal Connection**: How workshops relate to their interests and expertise
- **Sharing Patterns**: When and how they share workshop information
- **Value Proposition**: What makes workshops worth sharing in their network
"""
        
        instructions = """
1. Thoroughly analyze all posts to find workshop mentions and recommendations
2. Categorize workshops by type and identify the person's preferences
3. Analyze recommendation patterns and network sharing behavior
4. Identify the most valuable workshop opportunities they suggest
5. Understand their role in workshop discovery and network education
6. Provide clear insights about workshop opportunities in their network
7. Focus on actionable recommendations and valuable learning opportunities
8. Analyze engagement patterns to understand network interest
9. Identify trends in workshop types and sharing frequency
10. Provide a comprehensive overview of workshop discovery in their network
"""
        
        return prompt, instructions

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Workshop Finder')
    parser.add_argument('--json-file', '-j', 
                       default='processed_posts.json',
                       help='JSON file name to load from data folder (default: processed_posts.json)')
    parser.add_argument('--list-files', '-l', 
                       action='store_true',
                       help='List available JSON files in data folder')
    return parser.parse_args()

def main():
    """Main function to run the workshop finder test"""
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
        
        print("🔍 Starting Workshop Finder Test...")
        print(f"📁 Using data file: {args.json_file}")
        
        # Create data organizer with specified JSON file
        organizer = WorkshopFinderDataOrganizer(json_file=args.json_file)
        
        # Run the test
        organizer.run_test()
        
        print("✅ Workshop Finder Test completed!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
