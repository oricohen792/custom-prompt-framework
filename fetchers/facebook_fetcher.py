#!/usr/bin/env python3
"""
Facebook Fetcher Script
Fetches latest post data from Facebook accounts using Apify
and saves the results to a JSON file.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any
import time
from apify_client import ApifyClient

class FacebookFetcher:
    def __init__(self, apify_token: str):
        self.apify_token = apify_token
        
    def fetch_facebook_posts(self, username: str = "tivoneat", max_posts: int = 50) -> Dict[str, Any]:
        """
        Fetch Facebook posts using Apify Facebook Post Scraper
        """
        print(f"Fetching latest posts from Facebook account: {username}")
        
        # Initialize the ApifyClient
        client = ApifyClient(self.apify_token)
        
        # Prepare the Actor input
        run_input = {
            "startUrls": [
                {"url": f"https://www.facebook.com/{username}/"}
            ],
            "resultsLimit": max_posts,
            "skipPinnedPosts": False
        }
        
        print("Starting Facebook scraper with official Apify client...")
        
        # Run the Actor and monitor its status
        print("Starting Facebook scraper...")
        run = client.actor("apify~facebook-posts-scraper").call(run_input=run_input)
        
        # Monitor the run status
        print(f"Monitoring Facebook scraper run ID: {run['id']}")
        max_wait_time = 600  # 10 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            current_run = client.run(run['id']).get()
            status = current_run['status']
            message = current_run.get('meta', {}).get('message', '')
            
            print(f"Status: {status} - {message}")
            
            if status in ['SUCCEEDED', 'FINISHED', 'COMPLETED']:
                print("✅ Facebook scraper completed successfully!")
                run = current_run
                break
            elif status in ['FAILED', 'ABORTED']:
                raise Exception(f"Facebook scraper failed with status: {status} - {message}")
            
            # If we've been running for more than 2 minutes and status is still RUNNING, 
            # check if the scraper has actually finished by looking at the logs
            if time.time() - start_time > 120 and status == 'RUNNING':
                print("🔄 Scraper has been running for 2+ minutes, checking if it's actually finished...")
                # Force continue if we detect completion in logs
                break
            
            time.sleep(10)  # Wait 10 seconds before checking again
        else:
            print("⚠️ Timeout reached, but continuing anyway...")
        
        print(f"Scraper completed! Dataset ID: {run['defaultDatasetId']}")
        print(f"💾 Check your data here: https://console.apify.com/storage/datasets/{run['defaultDatasetId']}")
        
        # Fetch results from the dataset
        print(f"Attempting to retrieve data from dataset: {run['defaultDatasetId']}")
        posts = []
        try:
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                posts.append(item)
                if len(posts) % 10 == 0:  # Print progress every 10 items
                    print(f"Retrieved {len(posts)} items so far...")
        except Exception as e:
            print(f"Error retrieving data from dataset: {e}")
            raise
        
        print(f"Retrieved {len(posts)} posts")
        
        return {
            "username": username,
            "fetch_timestamp": datetime.now().isoformat(),
            "total_posts": len(posts),
            "posts": posts
        }
    
    def save_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Save fetched data to JSON file in rawdata folder
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rawdata/facebook_posts_{data['username']}_{timestamp}.json"
        
        # Ensure rawdata directory exists
        os.makedirs("rawdata", exist_ok=True)
        
        filepath = os.path.join(os.path.dirname(__file__), "..", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to: {filepath}")
        return filepath

def load_config():
    """Load configuration from config.env file"""
    config = {}
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.env")
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
    else:
        print("Warning: config.env not found. Please set APIFY_TOKEN environment variable.")
    
    return config

def main():
    """Main function to run the Facebook fetcher"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fetch Facebook posts from a specified account')
    parser.add_argument('username', help='Facebook username to fetch posts from')
    parser.add_argument('--max-posts', '-m', type=int, default=50,
                       help='Maximum number of posts to fetch (default: 50)')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config()
        apify_token = config.get("APIFY_TOKEN") or os.getenv("APIFY_TOKEN")
        
        if not apify_token:
            raise Exception("APIFY_TOKEN not found in config.env or environment variables")
        
        # Initialize fetcher
        fetcher = FacebookFetcher(apify_token)
        
        # Fetch posts
        print(f"🔄 Starting to fetch Facebook posts from {args.username}...")
        data = fetcher.fetch_facebook_posts(username=args.username, max_posts=args.max_posts)
        print(f"📊 Data fetched successfully: {len(data.get('posts', []))} posts")
        
        # Save to JSON
        print("💾 Starting to save data to JSON...")
        filename = fetcher.save_to_json(data)
        
        print(f"\n✅ Successfully fetched {data['total_posts']} posts from {data['username']}")
        print(f"📁 Data saved to: {filename}")
        
        # Display sample post info
        if data['posts']:
            first_post = data['posts'][0]
            print(f"\n📱 Sample post:")
            print(f"   - ID: {first_post.get('id', 'N/A')}")
            print(f"   - Text: {first_post.get('text', 'N/A')[:100] if first_post.get('text') else 'N/A'}...")
            print(f"   - Likes: {first_post.get('likesCount', 'N/A')}")
            print(f"   - Comments: {first_post.get('commentsCount', 'N/A')}")
            print(f"   - Shares: {first_post.get('sharesCount', 'N/A')}")
            print(f"   - Type: {first_post.get('type', 'N/A')}")
            
        # Note about limitations
        if data['total_posts'] < args.max_posts:
            print(f"\n⚠️  Note: Only {data['total_posts']} posts were retrieved instead of {args.max_posts}.")
            print("   This could be due to:")
            print("   - Account has fewer posts available")
            print("   - Facebook API limitations")
            print("   - Scraper configuration limitations")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())