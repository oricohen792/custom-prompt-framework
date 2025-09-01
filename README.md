# Social Media Analysis Pipeline

A comprehensive tool for fetching, merging, and analyzing social media data from Facebook, Instagram, and TikTok using Apify scrapers.

## 🚀 Overview

This pipeline allows you to:
1. **Fetch** social media posts from multiple platforms
2. **Merge** data into unified formats
3. **Analyze** content using custom AI prompts
4. **Generate** insights and stories from the data

## 📁 Project Structure

```
custom_prompt/
├── fetchers/                 # Social media data fetchers
│   ├── facebook_fetcher.py  # Facebook posts scraper
│   ├── insta_fetcher.py     # Instagram posts scraper
│   ├── tiktok_fetcher.py    # TikTok videos scraper
│   └── universal_merger.py  # Data merger and processor
├── custom_prompts/           # AI analysis prompts
│   ├── post_writer_story.py # Story generation from posts
│   └── workshop_finder.py   # Workshop/event finder
├── rawdata/                  # Raw scraped data storage
├── data/                     # Processed and merged data
├── results/                  # Analysis results and outputs
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

### Step 3: Run Custom Prompts

#### Generate Stories from Posts
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

### Example 1: Analyze "kfironitta"
```bash
# 1. Fetch data from all platforms
python fetchers/facebook_fetcher.py kfironitta
python fetchers/insta_fetcher.py kfironitta
python fetchers/tiktok_fetcher.py kfironitta

# 2. Merge all data
python fetchers/universal_merger.py

# 3. Generate story analysis
python custom_prompts/post_writer_story.py --json-file data/kfironitta_analysis.json
```

### Example 2: Analyze "cristianoronaldo"
```bash
# 1. Fetch data
python fetchers/facebook_fetcher.py cristianoronaldo
python fetchers/insta_fetcher.py cristianoronaldo
python fetchers/tiktok_fetcher.py cristianoronaldo

# 2. Merge data
python fetchers/universal_merger.py

# 3. Find workshops/events
python custom_prompts/workshop_finder.py --json-file data/cristianoronaldo_analysis.json
```

## 🔧 Custom Prompts

### Creating New Analysis Prompts
1. Create a new Python file in `custom_prompts/`
2. Use the base class structure from existing prompts
3. Implement your analysis logic
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
        self.prompt = "Your custom analysis prompt here"
    
    def analyze_data(self, data):
        # Your analysis logic here
        return "Analysis results"

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
```

### Custom Data Processing
```bash
# Process specific date ranges
python fetchers/universal_merger.py --date-from 2025-01-01 --date-to 2025-01-31

# Filter by platform
python fetchers/universal_merger.py --platforms instagram facebook
```

## 📝 Output Examples

### Story Generation Output
```
📖 Story Analysis for @kfironitta

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

**Happy Social Media Analysis! 🚀**
