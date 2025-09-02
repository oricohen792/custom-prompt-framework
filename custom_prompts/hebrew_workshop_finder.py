#!/usr/bin/env python3
"""
Hebrew Workshop Finder using Universal Merger Output Format
Prompt: "Find workshops the creator offer on the posts סדנאות שיעורים מחירים הזמנות תאריכים - תרחיב את המילים האילו משמעותי search only in hebrew"
Finds workshops, classes, prices, bookings, and dates offered by the creator
Works with universal merger output format including images, videos, and replies_data
"""

import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'base_class'))
from unified_prompt_tester import UnifiedPromptTester, BaseDataOrganizer

class HebrewWorkshopFinderDataOrganizer(BaseDataOrganizer):
    """Organizes posts data to find Hebrew workshop and educational offerings"""
    
    def __init__(self, json_file=None):
        """Initialize with optional JSON file name"""
        super().__init__(json_file)
        self.analysis_purpose = "Find workshops the creator offer on the posts סדנאות שיעורים מחירים הזמנות תאריכים - תרחיב את המילים האילו משמעותי search only in hebrew"
        self.test_name = "hebrew_workshop_finder"
        self.max_posts_to_process = 20  # Reduced to avoid token limits
        self.max_content_length = 500  # Limit content length per post
        self.max_replies = 5  # Limit number of replies per post
    
    def organize_data(self, posts):
        """Organize posts data to find Hebrew workshop content using universal merger format"""
        # Filter for Hebrew content (30%+ Hebrew characters)
        hebrew_posts = []
        for post in posts:
            content = post.get('content', '') or post.get('text', '') or post.get('caption', '')
            if self.is_hebrew_content(content):
                hebrew_posts.append(post)
        
        # Search for workshop-related keywords
        workshop_keywords = [
            'סדנאות', 'סדנה', 'workshop', 'workshops',
            'שיעורים', 'שיעור', 'lesson', 'lessons', 'class', 'classes',
            'מחירים', 'מחיר', 'price', 'prices', 'עלות', 'עלויות',
            'הזמנות', 'הזמנה', 'booking', 'bookings', 'רישום', 'רישומים',
            'תאריכים', 'תאריך', 'date', 'dates', 'מועד', 'מועדים',
            'קורס', 'קורסים', 'course', 'courses',
            'הרשמה', 'הרשמות', 'registration', 'registrations',
            'מחזור', 'מחזורים', 'cohort', 'cohorts',
            'הרצאה', 'הרצאות', 'lecture', 'lectures',
            'ייעוץ', 'ייעוצים', 'consultation', 'consultations',
            'אימון', 'אימונים', 'coaching', 'training'
        ]
        
        workshop_posts = []
        for post in hebrew_posts:
            content = post.get('content', '') or post.get('text', '') or post.get('caption', '')
            replies_data = post.get('replies_data', [])
            
            # Check main content and replies for workshop keywords
            all_text = content + ' ' + ' '.join(replies_data) if replies_data else content
            
            if any(keyword in all_text.lower() for keyword in workshop_keywords):
                # Truncate content to avoid token limits
                truncated_content = content[:self.max_content_length] + "..." if len(content) > self.max_content_length else content
                
                # Limit replies to avoid token limits
                limited_replies = replies_data[:self.max_replies] if len(replies_data) > self.max_replies else replies_data
                
                # Truncate individual replies
                truncated_replies = []
                for reply in limited_replies:
                    if len(reply) > 200:  # Limit reply length
                        truncated_replies.append(reply[:200] + "...")
                    else:
                        truncated_replies.append(reply)
                
                workshop_posts.append({
                    'content': truncated_content,
                    'platform': post.get('social_network', ''),
                    'time': post.get('post_time', ''),
                    'likes': post.get('likes_count', 0),
                    'comments': post.get('comments_count', 0),
                    'views': post.get('views', 0),
                    'plays': post.get('plays', 0),
                    'shares': post.get('shares', 0),
                    'saves': post.get('saves', 0),
                    'hashtags': post.get('hashtags', [])[:10],  # Limit hashtags
                    'replies_data': truncated_replies,
                    'images': post.get('images', [])[:3],  # Limit images
                    'videos': post.get('videos', [])[:2]   # Limit videos
                })
        
        # Analyze workshop themes
        all_workshop_text = ' '.join([post.get('content', '') for post in workshop_posts])
        all_replies_text = ' '.join([' '.join(post.get('replies_data', [])) for post in workshop_posts])
        combined_text = all_workshop_text + ' ' + all_replies_text
        
        workshop_themes = {
            "dance": combined_text.lower().count('ריקוד') + combined_text.lower().count('dance'),
            "music": combined_text.lower().count('מוזיקה') + combined_text.lower().count('music'),
            "art": combined_text.lower().count('אמנות') + combined_text.lower().count('art'),
            "fitness": combined_text.lower().count('כושר') + combined_text.lower().count('fitness'),
            "cooking": combined_text.lower().count('בישול') + combined_text.lower().count('cooking'),
            "photography": combined_text.lower().count('צילום') + combined_text.lower().count('photography'),
            "writing": combined_text.lower().count('כתיבה') + combined_text.lower().count('writing'),
            "business": combined_text.lower().count('עסקים') + combined_text.lower().count('business'),
            "marketing": combined_text.lower().count('שיווק') + combined_text.lower().count('marketing'),
            "digital": combined_text.lower().count('דיגיטלי') + combined_text.lower().count('digital'),
            "social_media": combined_text.lower().count('רשתות חברתיות') + combined_text.lower().count('social media'),
            "content_creation": combined_text.lower().count('יצירת תוכן') + combined_text.lower().count('content creation')
        }
        
        # Get top workshop themes
        top_themes = sorted(workshop_themes.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Extract pricing information
        pricing_keywords = ['₪', 'שקל', 'שקלים', 'מחיר', 'מחירים', 'עלות', 'תשלום', 'תשלומים', 'הנחה', 'הנחות']
        pricing_posts = []
        for post in workshop_posts:
            content = post.get('content', '') + ' ' + ' '.join(post.get('replies_data', []))
            if any(keyword in content for keyword in pricing_keywords):
                pricing_posts.append(post)
        
        # Extract contact information
        contact_keywords = ['@', 'טלפון', 'פלאפון', 'מייל', 'אימייל', 'whatsapp', 'ווטסאפ', 'לינק', 'קישור']
        contact_posts = []
        for post in workshop_posts:
            content = post.get('content', '') + ' ' + ' '.join(post.get('replies_data', []))
            if any(keyword in content.lower() for keyword in contact_keywords):
                contact_posts.append(post)
        
        # Prioritize and limit posts to avoid token limits
        # Sort by engagement (likes + comments + views) to get most relevant posts
        workshop_posts_sorted = sorted(workshop_posts, 
                                     key=lambda x: x['likes'] + x['comments'] + x['views'] + x['plays'], 
                                     reverse=True)
        
        # Limit to most relevant posts
        limited_workshop_posts = workshop_posts_sorted[:self.max_posts_to_process]
        
        organized_data = {
            "total_posts": len(posts),
            "hebrew_posts": len(hebrew_posts),
            "workshop_posts": limited_workshop_posts,
            "workshop_themes": top_themes,
            "pricing_posts": pricing_posts[:10],  # Limit pricing posts
            "contact_posts": contact_posts[:10],  # Limit contact posts
            "workshop_keywords_found": len(workshop_posts),
            "content_summary": {
                "total_hebrew_content": len(hebrew_posts),
                "workshop_related_content": len(workshop_posts),
                "pricing_mentions": len(pricing_posts),
                "contact_mentions": len(contact_posts),
                "workshop_percentage": (len(workshop_posts) / len(hebrew_posts) * 100) if hebrew_posts else 0,
                "posts_analyzed": len(limited_workshop_posts),
                "posts_truncated": len(workshop_posts) - len(limited_workshop_posts)
            }
        }
        
        return organized_data
    
    def is_hebrew_content(self, text):
        """Check if text contains 30%+ Hebrew characters"""
        if not text:
            return False
        
        hebrew_chars = sum(1 for char in text if '\u0590' <= char <= '\u05FF')
        total_chars = len(text)
        
        return (hebrew_chars / total_chars) >= 0.3 if total_chars > 0 else False
    
    def get_prompt(self):
        """Get the prompt and instructions for the AI"""
        prompt = """
**HEBREW WORKSHOP FINDER - UNIVERSAL MERGER FORMAT**

You are analyzing Hebrew social media content from the universal merger output format to find workshops, classes, and educational offerings.

**DATA FORMAT:**
The data includes posts with the following structure (optimized for token limits):
- `content`: Main post content (truncated to 500 chars if longer)
- `social_network`: Platform (instagram, facebook, tiktok)
- `post_time`: Timestamp
- `likes_count`, `comments_count`, `views`, `plays`, `shares`, `saves`: Engagement metrics
- `hashtags`: Array of hashtags (limited to 10)
- `replies_data`: Array of comment/reply texts (limited to 5 replies, 200 chars each)
- `images`: Array of image URLs (limited to 3)
- `videos`: Array of video URLs (limited to 2)

**NOTE:** Data has been filtered and truncated to focus on the most relevant workshop-related content while staying within token limits. Posts are prioritized by engagement metrics.

**TASK:**
Extract all information about workshops, classes, courses, and educational services offered by this creator.

**SEARCH FOR:**
- **סדנאות** (workshops) - any workshop or hands-on learning sessions
- **שיעורים** (lessons/classes) - individual or group lessons
- **מחירים** (prices) - pricing information for services
- **הזמנות** (bookings/reservations) - how to book or register
- **תאריכים** (dates) - workshop dates, schedules, or timelines

**EXPANDED SEARCH TERMS:**
- **סדנאות**: סדנה, סדנאות, workshop, workshops, קורס מעשי, שיעור מעשי, מחזור, מחזורים
- **שיעורים**: שיעור, שיעורים, lesson, lessons, class, classes, קורס, קורסים, הרצאה, הרצאות
- **מחירים**: מחיר, מחירים, price, prices, עלות, עלויות, תשלום, תשלומים, ₪, שקל, שקלים, הנחה, הנחות
- **הזמנות**: הזמנה, הזמנות, booking, bookings, רישום, רישומים, הרשמה, הרשמות, הרשמה מוקדמת
- **תאריכים**: תאריך, תאריכים, date, dates, מועד, מועדים, לוח זמנים, אחרי החגים
- **ייעוץ**: ייעוץ, ייעוצים, consultation, consultations, אימון, אימונים, coaching, training

**ANALYSIS REQUIREMENTS:**
1. **Content Analysis**: Analyze main content AND replies_data for workshop-related content
2. **Keyword Detection**: Find posts containing workshop, class, or educational keywords
3. **Information Extraction**: Extract specific details about offerings from content and replies
4. **Pricing Information**: Find any pricing or cost details (look for ₪, שקל, מחיר, etc.)
5. **Registration Details**: Find booking, registration, or contact information
6. **Schedule Information**: Find dates, times, or scheduling details
7. **Media Analysis**: Check if images/videos contain workshop-related content
8. **Engagement Analysis**: Note which workshop posts have high engagement

**OUTPUT FORMAT:**
Provide a comprehensive analysis in the following structure:

## WORKSHOP ANALYSIS RESULTS

### WORKSHOPS & CLASSES FOUND:
[List all workshops, classes, and educational offerings found with details]

### PRICING INFORMATION:
[Extract all pricing details, costs, payment options, and special offers]

### REGISTRATION & BOOKING:
[Find all booking methods, registration links, contact information, and early bird offers]

### SCHEDULES & DATES:
[Extract all dates, times, scheduling information, and upcoming sessions]

### CONTACT INFORMATION:
[Find contact details, phone numbers, email addresses, social media handles, and WhatsApp]

### WORKSHOP THEMES & FOCUS AREAS:
[Identify the main themes and subjects of the workshops offered]

### ENGAGEMENT ANALYSIS:
[Note which workshop posts have highest engagement and why]

### MEDIA CONTENT:
[Describe any relevant images or videos that showcase workshops]

### ADDITIONAL DETAILS:
[Any other relevant information about the educational offerings, special programs, or unique features]

**SEARCH METHODOLOGY:**
- Focus ONLY on Hebrew content (30%+ Hebrew characters)
- Analyze both main content AND replies_data for complete information
- Look for both explicit mentions and implied educational content
- Check hashtags for workshop-related terms
- Identify patterns in how they promote their services
- Look for recurring themes in their educational content
- Pay attention to engagement metrics to identify popular workshop content
- Extract actionable information for potential participants
"""

        instructions = """
1. Analyze Hebrew posts for workshop-related content (main content + replies_data)
2. Look for workshop keywords in Hebrew and English across all text fields
3. Extract pricing information and payment details (including ₪ symbols)
4. Find registration and booking methods in content and replies
5. Identify schedules and dates for workshops (including "אחרי החגים" references)
6. Look for contact information and social media handles in all text
7. Analyze workshop themes and educational focus areas
8. Check engagement metrics to identify popular workshop content
9. Provide comprehensive workshop offering summary with actionable details
10. Include all relevant details for workshop participation
11. Extract information from both main posts and comment replies
12. Look for early bird offers, special pricing, and registration deadlines
"""
        
        return prompt, instructions

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Hebrew Workshop Finder')
    parser.add_argument('--json-file', '-j', 
                       default='processed_posts.json',
                       help='JSON file name to load from data folder (default: processed_posts.json)')
    parser.add_argument('--list-files', '-l', 
                       action='store_true',
                       help='List available JSON files in data folder')
    return parser.parse_args()

def main():
    """Main function to run the Hebrew workshop finder test"""
    try:
        args = parse_arguments()
        
        if args.list_files:
            # List available data files
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            if os.path.exists(data_dir):
                json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
                if json_files:
                    print("📁 Available JSON files in data folder:")
                    for file in sorted(json_files):
                        file_path = os.path.join(data_dir, file)
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            file_size_mb = file_size / (1024 * 1024)
                            print(f"   - {file} ({file_size_mb:.2f} MB)")
                else:
                    print("📁 No JSON files found in data folder")
            else:
                print(f"📁 Data folder not found: {data_dir}")
            return
        
        print("🔍 Starting Hebrew Workshop Finder Test...")
        print(f"📁 Using data file: {args.json_file}")
        
        # Create data organizer with specified JSON file
        organizer = HebrewWorkshopFinderDataOrganizer(json_file=args.json_file)
        
        # Run the test
        organizer.run_test()
        
        print("✅ Hebrew Workshop Finder Test completed!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()