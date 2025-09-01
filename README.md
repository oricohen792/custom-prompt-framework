# Social Media Analysis, Suggestion & Action Pipeline

A comprehensive tool for fetching, merging, analyzing, suggesting actions, and executing strategies from social media data across Facebook, Instagram, and TikTok using Apify scrapers.

## 🚀 Overview

This pipeline allows you to:
1. **Fetch** social media posts from multiple platforms
2. **Merge** data into unified formats
3. **Analyze** content using custom AI prompts
4. **Suggest** strategic actions and recommendations
5. **Act** on insights with automated or guided responses
6. **Generate** actionable insights and stories from the data

## 📁 Project Structure

```
custom_prompt/
├── fetchers/                 # Social media data fetchers
│   ├── facebook_fetcher.py  # Facebook posts scraper
│   ├── insta_fetcher.py     # Instagram posts scraper
│   ├── tiktok_fetcher.py    # TikTok videos scraper
│   └── universal_merger.py  # Data merger and processor
├── custom_prompts/           # AI analysis, suggestion & action prompts
│   ├── post_writer_story.py # Story generation from posts
│   ├── workshop_finder.py   # Workshop/event finder
│   └── action_suggester.py  # Strategic action recommendations
├── rawdata/                  # Raw scraped data storage
├── data/                     # Processed and merged data
├── results/                  # Analysis results and action plans
└── config.env               # Configuration file
```

## ⚙️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `config.env` file with your API keys:
```env
APIFY_API_TOKEN=your_apify_token_here
OPENAI_API_KEY=your_openai_key_here
```

## 🔄 Complete Pipeline

### Step 1: Fetch Social Media Data

#### Facebook Posts
```bash
# Fetch posts for a specific user
python fetchers/facebook_fetcher.py username

# Example: Fetch posts for "kfironitta"
python fetchers/facebook_fetcher.py kfironitta
```

#### Instagram Posts
```bash
# Fetch posts for a specific user
python fetchers/insta_fetcher.py username

# Example: Fetch posts for "kfironitta"
python fetchers/insta_fetcher.py kfironitta
```

#### TikTok Videos
```bash
# Fetch videos for a specific user
python fetchers/tiktok_fetcher.py username

# Example: Fetch videos for "kfironitta"
python fetchers/tiktok_fetcher.py kfironitta
```

**Output:** Raw JSON files saved in `rawdata/` folder with timestamps.

### Step 2: Merge Data

#### Automatic Batch Processing
```bash
# Merge all available raw data files
python fetchers/universal_merger.py

# This will:
# - Scan rawdata/ folder for all JSON files
# - Group files by username
# - Merge all platforms for each username
# - Create unified data files in data/ folder
```

#### Manual Single File Processing
```bash
# Merge specific files
python fetchers/universal_merger.py --input-file rawdata/facebook_posts_user.json
```

**Output:** Merged JSON files in `data/` folder with unified structure.

### Step 3: Analyze, Suggest & Act

#### Generate Stories and Insights
```bash
# Analyze merged data and create stories
python custom_prompts/post_writer_story.py --json-file data/username_analysis.json

# Example: Analyze "kfironitta" data
python custom_prompts/post_writer_story.py --json-file data/kfironitta_analysis.json
```

#### Find Workshops and Events
```bash
# Search for workshops and events in posts
python custom_prompts/workshop_finder.py --json-file data/username_analysis.json
```

#### Get Strategic Action Recommendations
```bash
# Get actionable insights and strategic recommendations
python custom_prompts/action_suggester.py --json-file data/username_analysis.json

# This will:
# - Analyze content patterns and engagement
# - Suggest optimal posting times and content types
# - Recommend engagement strategies
# - Provide action items for improvement
```

## 📊 Data Structure

### Raw Data Format
Each platform fetcher creates timestamped JSON files:
```
rawdata/
├── facebook_posts_username_YYYYMMDD_HHMMSS.json
├── instagram_posts_username_YYYYMMDD_HHMMSS.json
└── tiktok_videos_username_YYYYMMDD_HHMMSS.json
```

### Merged Data Format
The universal merger creates unified files:
```
data/
└── username_analysis.json
```

**Structure:**
```json
[
  {
    "social_network": "instagram",
    "post_id": "12345",
    "text": "Post content...",
    "timestamp": "2025-01-01T00:00:00.000Z",
    "likes": 100,
    "comments": 25,
    "shares": 5
  }
]
```

## 🎯 Complete Workflow Examples

### Example 1: Analyze, Suggest & Act for "kfironitta"
```bash
# 1. Fetch data from all platforms
python fetchers/facebook_fetcher.py kfironitta
python fetchers/insta_fetcher.py kfironitta
python fetchers/tiktok_fetcher.py kfironitta

# 2. Merge all data
python fetchers/universal_merger.py

# 3. Generate story analysis
python custom_prompts/post_writer_story.py --json-file data/kfironitta_analysis.json

# 4. Get strategic recommendations
python custom_prompts/action_suggester.py --json-file data/kfironitta_analysis.json

# 5. Find business opportunities
python custom_prompts/workshop_finder.py --json-file data/kfironitta_analysis.json
```

### Example 2: Strategic Analysis for "cristianoronaldo"
```bash
# 1. Fetch data
python fetchers/facebook_fetcher.py cristianoronaldo
python fetchers/insta_fetcher.py cristianoronaldo
python fetchers/tiktok_fetcher.py cristianoronaldo

# 2. Merge data
python fetchers/universal_merger.py

# 3. Analyze engagement patterns
python custom_prompts/post_writer_story.py --json-file data/cristianoronaldo_analysis.json

# 4. Get brand strategy recommendations
python custom_prompts/action_suggester.py --json-file data/cristianoronaldo_analysis.json
```

## 🔧 Custom Prompts

### Creating New Analysis, Suggestion & Action Prompts
1. Create a new Python file in `custom_prompts/`
2. Use the base class structure from existing prompts
3. Implement your analysis, suggestion, or action logic
4. Use the merged JSON data as input

### Example Custom Prompt Structure
```python
#!/usr/bin/env python3
import json
import argparse
from base_class.unified_prompt_tester import UnifiedPromptTester

class MyCustomAnalyzer(UnifiedPromptTester):
    def __init__(self):
        super().__init__()
        self.prompt = "Your custom analysis, suggestion, or action prompt here"
    
    def analyze_data(self, data):
        # Your analysis logic here
        return "Analysis results"
    
    def suggest_actions(self, analysis):
        # Your suggestion logic here
        return "Action recommendations"
    
    def execute_actions(self, suggestions):
        # Your action execution logic here
        return "Action results"

if __name__ == "__main__":
    analyzer = MyCustomAnalyzer()
    analyzer.run()
```

## 📈 Data Analysis Features

### Instagram Data
- ✅ **Complete conversations** with comments and replies
- ✅ **Post content** and hashtags
- ✅ **User interactions** and engagement
- ✅ **Media information** and URLs

### Facebook Data
- ✅ **Post content** and shared posts
- ✅ **Engagement metrics** (likes, comments, shares)
- ❌ **Comment content** (only counts available)
- ❌ **Reply content** (not captured by scraper)

### TikTok Data
- ✅ **Video metadata** and descriptions
- ✅ **Engagement metrics** (likes, views, shares)
- ❌ **Comment content** (only counts available)

## 🎯 Action & Suggestion Capabilities

### Strategic Recommendations
- **Content Strategy:** Optimal posting times, content types, hashtags
- **Engagement Tactics:** Response strategies, community building
- **Growth Opportunities:** Audience expansion, platform optimization
- **Business Insights:** Market trends, competitor analysis

### Automated Actions
- **Response Templates:** Pre-written responses for common scenarios
- **Engagement Scheduling:** Optimal timing for interactions
- **Content Planning:** Data-driven content calendar suggestions
- **Performance Tracking:** Automated metrics and reporting

## 🚨 Troubleshooting

### Common Issues

#### 1. "Actor not found" Error
- Verify the Apify actor name in the fetcher
- Check your Apify API token
- Ensure the actor is public or you have access

#### 2. No Data Retrieved
- Check if the username exists on the platform
- Verify the platform is public
- Check API rate limits and quotas

#### 3. Merge Errors
- Ensure all JSON files are valid
- Check file naming conventions
- Verify file paths and permissions

### Debug Commands
```bash
# Check file structure
ls -la rawdata/
ls -la data/

# Validate JSON files
python -m json.tool rawdata/filename.json

# Check file sizes
du -h rawdata/*.json
```

## 🔄 Advanced Usage

### Batch Processing Multiple Users
```bash
# Create a script to process multiple users
for user in user1 user2 user3; do
    python fetchers/facebook_fetcher.py $user
    python fetchers/insta_fetcher.py $user
    python fetchers/tiktok_fetcher.py $user
done

# Merge all data
python fetchers/universal_merger.py

# Generate comprehensive analysis and actions
python custom_prompts/action_suggester.py --json-file data/all_users_analysis.json
```

### Custom Data Processing
```bash
# Process specific date ranges
python fetchers/universal_merger.py --date-from 2025-01-01 --date-to 2025-01-31

# Filter by platform
python fetchers/universal_merger.py --platforms instagram facebook
```

## 📝 Output Examples

### Story Analysis & Action Plan Output
```
📖 Analysis, Suggestion & Action Plan for @kfironitta

🎯 Account Overview:
- Platform: Instagram & Facebook
- Total Posts: 100
- Engagement Rate: 4.2%

📱 Content Themes:
- Business advice and entrepreneurship
- Personal development
- Political commentary
- Workshop announcements

💡 Key Insights:
- High engagement on business content
- Active community interaction
- Regular workshop promotions

🚀 Strategic Recommendations:
- Post business content on Tuesdays (highest engagement)
- Use more video content (2x engagement vs images)
- Engage with followers within 1 hour of posting
- Create weekly business tip series

📋 Action Items:
1. Schedule business posts for Tuesday mornings
2. Create 3 video posts this week
3. Set up 1-hour response time alerts
4. Plan business tip series content
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your custom prompts or improvements
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with detailed information

---

**Happy Social Media Analysis, Suggestion & Action! 🚀**
