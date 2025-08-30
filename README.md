# Custom Prompt Framework 🚀

A powerful framework for creating and running custom AI prompts that analyze social media data and generate insights, stories, and analyses.

## 🎯 What This Framework Does

This framework allows you to create **custom prompts** that:
- Analyze social media posts and engagement data
- Generate creative content (stories, analyses, landing pages)
- Process data efficiently while keeping vector stores manageable
- Provide structured AI responses based on your specific requirements

## 📊 Data Structure

### **Cleaned JSON Format**

The framework now works with cleaned and optimized JSON files that contain only essential fields:

#### **processed_posts.json** (Facebook Posts)
```json
{
  "post_time": "2025-08-30T23:21:44.414318+00",
  "content": "Post text content in Hebrew/English",
  "social_network": "facebook",
  "likes_count": 9,
  "comments_count": 0,
  "views": 0,
  "plays": 0,
  "shares": 0,
  "saves": 0,
  "video_url": "",
  "replies_data": []
}
```

#### **processed_posts1.json** (TikTok Posts)
```json
{
  "post_time": "2021-02-16 17:04:13+00",
  "content": "Post text content in Hebrew/English",
  "social_network": "tiktok",
  "likes_count": 48400,
  "comments_count": 671,
  "views": 933600,
  "plays": 933600,
  "shares": 1280,
  "saves": 3216,
  "video_url": "https://www.tiktok.com/@user/video/123456789",
  "replies_data": []
}
```

### **Data Cleaning Results**

- **processed_posts.json**: 200 posts → 132 posts with content (65% size reduction)
- **processed_posts1.json**: 2025 posts → 384 posts with content (93% size reduction)
- **Removed**: Verbose metadata, empty content posts, redundant fields
- **Kept**: Essential engagement stats, post content, timestamps, social network info

## 🛠️ How to Ask for New Custom Prompts

### **Method 1: Direct Request**
Simply ask me: *"Make a custom prompt that [describe what you want]"*

**Examples:**
- *"Make a custom prompt to generate a 100-word Hebrew story about the post writer"*
- *"Create a custom prompt that analyzes viral content conspiracy theories"*
- *"Make a custom prompt to generate cake landing pages"*

### **Method 2: Detailed Specification**
Provide more specific details about what you want:

```
I want a custom prompt that:
- Analyzes [specific data aspect]
- Generates [type of output]
- Uses [specific format/style]
- Focuses on [particular topic]
- Limits data to [number] posts for efficiency
```

### **Method 3: Creative Inspiration**
Ask for something wild or creative:
- *"Make another crazy custom prompt"*
- *"Create something outrageous"*
- *"Make a fun and entertaining prompt"*

## 📁 Current Custom Prompts

### **1. Post Generator** 📝
- **Purpose**: Generate new social media posts based on analyzed data patterns
- **Output**: Creative post suggestions with engagement optimization tips
- **File**: `custom_prompts/post_generator.py`

### **2. Cake Landing Page Generator** 🎂
- **Purpose**: Create landing pages based on cake-related posts and engagement stats
- **Output**: Complete landing page structure with content strategy recommendations
- **File**: `custom_prompts/cake_landing_page.py`

## 🚀 How to Run Custom Prompts

### **Step 1: Navigate to the Project**
```bash
cd /path/to/custom_prompt
```

### **Step 2: Run Any Custom Prompt**
```bash
python custom_prompts/[prompt_name].py
```

**Examples:**
```bash
python custom_prompts/post_generator.py
python custom_prompts/cake_landing_page.py
```

### **Step 3: View Results**
Results are automatically saved to the `results/` folder:
- `[prompt_name]_ai_response.txt` - AI-generated content
- Vector store IDs for future reference

## 🎨 Custom Prompt Structure

Every custom prompt follows this structure:

```python
class [Name]DataOrganizer(BaseDataOrganizer):
    def __init__(self):
        self.analysis_purpose = "What this prompt does"
        self.test_name = "prompt_name"
        self.max_posts_to_process = X  # Limit for efficiency
    
    def organize_data(self, posts):
        # Data processing logic
        # Returns structured data for AI analysis
    
    def get_prompt(self):
        # Returns the prompt and instructions for the AI
```

## 💡 Tips for Requesting Custom Prompts

### **Be Specific About:**
1. **Purpose**: What do you want the prompt to accomplish?
2. **Output Format**: How should the results be structured?
3. **Data Focus**: What aspects of the data should be analyzed?
4. **Efficiency**: How many posts should be processed?
5. **Creativity Level**: Do you want something serious or entertaining?

### **Good Request Examples:**
- *"Create a custom prompt that analyzes food-related posts and generates recipe suggestions"*
- *"Make a custom prompt that creates Instagram captions based on post performance"*
- *"Build a custom prompt that analyzes engagement patterns and predicts viral content"*

### **Avoid:**
- Vague requests like "make something cool"
- Requests that don't specify the output format
- Asking for prompts that would process too much data

## 🔧 Technical Requirements

- **Python 3.7+**
- **OpenAI API Key** (configured in `config.env`)
- **Social media data** in cleaned JSON format:
  - `data/processed_posts.json` (Facebook posts)
  - `data/processed_posts1.json` (TikTok posts)
- **Base framework** in `base_class/unified_prompt_tester.py`

## 📊 Data Processing Limits

To keep vector stores manageable and avoid token limits:
- **Standard prompts**: Process 250 posts maximum
- **Efficient prompts**: Process 5-20 posts for focused analysis
- **Heavy analysis**: Process 1000+ posts (use with caution)

## 🎭 Creative Prompt Ideas

Here are some fun custom prompts you could request:

1. **Emoji Translator** - Translates posts into emoji-only versions
2. **Content Fortune Teller** - Predicts future post performance
3. **Hashtag Detective** - Analyzes hashtag effectiveness
4. **Post Poetry Generator** - Turns posts into poems
5. **Engagement Horoscope** - Creates horoscopes based on post data
6. **Content Recipe Book** - Generates "recipes" for viral content
7. **Post Personality Quiz** - Creates quizzes based on content analysis
8. **Social Media Tarot** - Generates tarot readings from post data

## 🚨 Troubleshooting

### **Common Issues:**
- **Token Limit Exceeded**: Reduce `max_posts_to_process` in the prompt
- **API Key Error**: Check `config.env` file exists and contains valid key
- **File Not Found**: Ensure cleaned JSON files exist in `data/` folder
- **Import Errors**: Check Python path and dependencies

### **Solutions:**
- Limit data processing to smaller post counts
- Verify environment configuration
- Check file paths and permissions
- Ensure all dependencies are installed

## 🤝 Getting Help

When asking for custom prompts, provide:
1. **Clear description** of what you want
2. **Specific requirements** for output format
3. **Data processing limits** if efficiency is important
4. **Creative direction** if you want something fun/entertaining

## 📈 Future Enhancements

Potential improvements for the framework:
- **Batch processing** for multiple prompts
- **Custom output formats** (JSON, CSV, HTML)
- **Interactive prompt builder** interface
- **Prompt templates** for common use cases
- **Performance analytics** for prompt effectiveness

---

**Ready to create your own custom prompt?** Just ask me with a clear description of what you want, and I'll build it for you! 🚀✨
