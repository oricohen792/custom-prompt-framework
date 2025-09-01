#!/usr/bin/env python3
"""
Instagram Fetcher Script
Fetches latest post data from Instagram accounts using Apify
and saves the results to a JSON file.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any
import time
from apify_client import ApifyClient

class InstagramFetcher:
    def __init__(self, apify_token: str):
        self.apify_token = apify_token
        
    def fetch_instagram_posts(self, username: str = "tivoneat", max_posts: int = 50) -> Dict[str, Any]:
        """
        Fetch Instagram posts using Apify Instagram Post Scraper
        """
        print(f"Fetching latest posts from Instagram account: @{username}")
        
        # Initialize the ApifyClient
        client = ApifyClient(self.apify_token)
        
        # Prepare the Actor input
        run_input = {
            "resultsLimit": max_posts,
            "skipPinnedPosts": False,
            "username": [f"@{username}"]
        }
        
        print("Starting Instagram scraper with official Apify client...")
        
        # Run the Actor and monitor its status
        print("Starting Instagram scraper...")
        run = client.actor("apify~instagram-post-scraper").call(run_input=run_input)
        
        # Monitor the run status
        print(f"Monitoring Instagram scraper run ID: {run['id']}")
        max_wait_time = 600  # 10 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            current_run = client.run(run['id']).get()
            status = current_run['status']
            message = current_run.get('meta', {}).get('message', '')
            
            print(f"Status: {status} - {message}")
            
            if status == 'SUCCEEDED':
                print("✅ Instagram scraper completed successfully!")
                run = current_run
                break
            elif status in ['FAILED', 'ABORTED']:
                raise Exception(f"Instagram scraper failed with status: {status} - {message}")
            
            time.sleep(10)  # Wait 10 seconds before checking again
        else:
            raise Exception("Instagram scraper timed out after 10 minutes")
        
        print(f"Scraper completed! Dataset ID: {run['defaultDatasetId']}")
        print(f"💾 Check your data here: https://console.apify.com/storage/datasets/{run['defaultDatasetId']}")
        
        # Fetch results from the dataset
        posts = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            posts.append(item)
        
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
            filename = f"rawdata/instagram_posts_{data['username']}_{timestamp}.json"
        
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
    """Main function to run the Instagram fetcher"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fetch Instagram posts from a specified account')
    parser.add_argument('username', help='Instagram username to fetch posts from')
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
        fetcher = InstagramFetcher(apify_token)
        
        # Fetch posts
        print(f"🔄 Starting to fetch Instagram posts from @{args.username}...")
        data = fetcher.fetch_instagram_posts(username=args.username, max_posts=args.max_posts)
        
        # Save to JSON
        filename = fetcher.save_to_json(data)
        
        print(f"\n✅ Successfully fetched {data['total_posts']} posts from @{args.username}")
        print(f"📁 Data saved to: {filename}")
        
        # Display sample post info
        if data['posts']:
            first_post = data['posts'][0]
            print(f"\n📱 Sample post:")
            print(f"   - ID: {first_post.get('id', 'N/A')}")
            print(f"   - Caption: {first_post.get('caption', 'N/A')[:100] if first_post.get('caption') else 'N/A'}...")
            print(f"   - Likes: {first_post.get('likesCount', 'N/A')}")
            print(f"   - Comments: {first_post.get('commentsCount', 'N/A')}")
            print(f"   - Type: {first_post.get('type', 'N/A')}")
            
        # Note about limitations
        if data['total_posts'] < args.max_posts:
            print(f"\n⚠️  Note: Only {data['total_posts']} posts were retrieved instead of {args.max_posts}.")
            print("   This could be due to:")
            print("   - Account has fewer posts available")
            print("   - Instagram API limitations")
            print("   - Scraper configuration limitations")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())