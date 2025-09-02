#!/usr/bin/env python3
"""
Workshop Landing Page Generator using Universal Merger Output Format
Generates HTML landing pages for each workshop found, using images from the data
"""

import sys
import os
import argparse
import json
import re
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'base_class'))
from unified_prompt_tester import UnifiedPromptTester, BaseDataOrganizer

class WorkshopLandingPageGeneratorDataOrganizer(BaseDataOrganizer):
    """Organizes posts data to generate HTML landing pages for workshops"""
    
    def __init__(self, json_file=None):
        """Initialize with optional JSON file name"""
        super().__init__(json_file)
        self.analysis_purpose = "Generate HTML landing pages for each workshop found, using images from the data"
        self.test_name = "workshop_landing_page_generator"
        self.max_posts_to_process = 20  # Focus on workshop content
        self.max_content_length = 500  # Limit content length per post
        self.max_replies = 5  # Limit number of replies per post
    
    def organize_data(self, posts):
        """Organize posts data to find workshop content for landing page generation"""
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
                    'images': post.get('images', []),  # Keep all images for landing pages
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
        
        # Collect all unique images for landing pages
        all_images = []
        for post in limited_workshop_posts:
            all_images.extend(post.get('images', []))
        
        # Remove duplicates while preserving order
        unique_images = []
        seen = set()
        for img in all_images:
            if img not in seen:
                unique_images.append(img)
                seen.add(img)
        

        
        organized_data = {
            "total_posts": len(posts),
            "hebrew_posts": len(hebrew_posts),
            "workshop_posts": limited_workshop_posts,
            "workshop_themes": top_themes,
            "pricing_posts": pricing_posts[:10],  # Limit pricing posts
            "contact_posts": contact_posts[:10],  # Limit contact posts
            "available_images": unique_images[:20],  # Images are pre-validated by universal merger
            "workshop_keywords_found": len(workshop_posts),
            "content_summary": {
                "total_hebrew_content": len(hebrew_posts),
                "workshop_related_content": len(workshop_posts),
                "pricing_mentions": len(pricing_posts),
                "contact_mentions": len(contact_posts),
                "workshop_percentage": (len(workshop_posts) / len(hebrew_posts) * 100) if hebrew_posts else 0,
                "posts_analyzed": len(limited_workshop_posts),
                "posts_truncated": len(workshop_posts) - len(limited_workshop_posts),
                "total_images_available": len(unique_images)
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
**WORKSHOP LANDING PAGE GENERATOR - UNIVERSAL MERGER FORMAT**

You are analyzing Hebrew social media content to generate HTML landing pages for each workshop found.

**DATA FORMAT:**
The data includes posts with the following structure:
- `content`: Main post content (truncated to 500 chars if longer)
- `social_network`: Platform (instagram, facebook, tiktok)
- `post_time`: Timestamp
- `likes_count`, `comments_count`, `views`, `plays`, `shares`, `saves`: Engagement metrics
- `hashtags`: Array of hashtags (limited to 10)
- `replies_data`: Array of comment/reply texts (limited to 5 replies, 200 chars each)
- `images`: Array of image URLs (available for landing pages)
- `videos`: Array of video URLs (limited to 2)
- `available_images`: Array of all unique images from workshop posts

**TASK:**
Generate individual HTML landing pages for each workshop/class found in the data.

**REQUIREMENTS:**
1. **Identify Workshops**: Find all distinct workshops, classes, courses, and educational offerings
2. **Extract Details**: For each workshop, extract:
   - Workshop name/title
   - Description and content
   - Pricing information
   - Dates and schedules
   - Registration/booking details
   - Contact information
3. **Generate HTML**: Create a complete HTML landing page for each workshop
4. **Use Images**: Incorporate relevant images from the `available_images` array (all images have been pre-validated by the universal merger)
5. **Modern Design**: Create professional, responsive landing pages

**HTML STRUCTURE REQUIREMENTS:**
Each landing page should include:
- Modern, responsive HTML5 structure
- CSS styling (embedded or inline)
- Hebrew RTL support
- Professional color scheme
- Mobile-friendly design
- Call-to-action buttons
- Image galleries
- Contact forms or information
- Pricing sections
- Registration/booking sections

**OUTPUT FORMAT:**
Provide a comprehensive analysis with HTML landing pages in the following structure:

## WORKSHOP LANDING PAGES ANALYSIS

### WORKSHOPS IDENTIFIED:
[List all workshops found with brief descriptions]

### LANDING PAGE 1: [Workshop Name]
```html
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Workshop Name]</title>
    <style>
        /* Modern CSS styling */
    </style>
</head>
<body>
    <!-- Complete landing page HTML -->
</body>
</html>
```

### LANDING PAGE 2: [Workshop Name]
[Continue for each workshop found...]

### IMAGE GALLERY:
[List all images used in the landing pages with their URLs]

### DESIGN NOTES:
[Explain design choices, color schemes, and layout decisions]

**DESIGN GUIDELINES:**
- Use modern, clean design principles
- Ensure Hebrew text displays correctly (RTL)
- Include engaging visuals from the available images (all pre-validated by universal merger)
- Make pricing and registration information prominent
- Use professional color schemes (blues, greens, or brand colors)
- Include social proof (likes, comments, engagement metrics)
- Make pages mobile-responsive
- Include clear call-to-action buttons
- Use high-quality images from the data (broken URLs filtered by universal merger)
- If no valid images are available, use placeholder images with appropriate styling
"""

        instructions = """
1. Analyze Hebrew posts to identify distinct workshops and classes
2. Extract comprehensive details for each workshop (name, description, pricing, dates, contact)
3. Generate complete HTML landing pages for each workshop
4. Use images from the available_images array in the landing pages (all images are pre-validated by universal merger)
5. Create modern, responsive HTML5 pages with embedded CSS
6. Ensure Hebrew RTL support and proper text display
7. Include professional design elements and color schemes
8. Add call-to-action buttons for registration/booking
9. Incorporate social proof and engagement metrics
10. Make pages mobile-friendly and accessible
11. Use high-quality images to showcase workshops (broken URLs have been filtered out)
12. Include contact information and registration details
13. Create engaging, conversion-focused landing pages
14. If no valid images are available, use placeholder images with appropriate styling
15. All images in available_images array have been tested for accessibility and will work properly
"""
        
        return prompt, instructions

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Workshop Landing Page Generator')
    parser.add_argument('--json-file', '-j', 
                       default='processed_posts.json',
                       help='JSON file name to load from data folder (default: processed_posts.json)')
    parser.add_argument('--list-files', '-l', 
                       action='store_true',
                       help='List available JSON files in data folder')
    return parser.parse_args()

def main():
    """Main function to run the workshop landing page generator test"""
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
        
        print("🎨 Starting Workshop Landing Page Generator Test...")
        print(f"📁 Using data file: {args.json_file}")
        
        # Create data organizer with specified JSON file
        organizer = WorkshopLandingPageGeneratorDataOrganizer(json_file=args.json_file)
        
        # Run the test
        organizer.run_test()
        
        print("✅ Workshop Landing Page Generator Test completed!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
