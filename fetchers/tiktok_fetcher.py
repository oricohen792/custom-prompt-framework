#!/usr/bin/env python3
"""
TikTok Fetcher Script
Fetches latest video data from TikTok accounts using Apify
and saves the results to a JSON file.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any
import time
from apify_client import ApifyClient

class TikTokFetcher:
    def __init__(self, apify_token: str):
        self.apify_token = apify_token
        
    def fetch_tiktok_videos(self, username: str = "tivoneat", max_videos: int = 50) -> Dict[str, Any]:
        """
        Fetch TikTok videos using Apify TikTok Video Scraper
        """
        print(f"Fetching latest videos from TikTok account: @{username}")
        
        # Initialize the ApifyClient
        client = ApifyClient(self.apify_token)
        
        # Prepare the Actor input
        run_input = {
            "excludePinnedPosts": False,
            "proxyCountryCode": "None",
            "resultsPerPage": 100,
            "scrapeRelatedVideos": False,
            "searchQueries": [f"@{username}"],
            "shouldDownloadAvatars": False,
            "shouldDownloadCovers": False,
            "shouldDownloadMusicCovers": False,
            "shouldDownloadSlideshowImages": False,
            "shouldDownloadSubtitles": False,
            "shouldDownloadVideos": False
        }
        
        print("Starting TikTok scraper with official Apify client...")
        
        # Run the Actor and monitor its status
        print("Starting TikTok scraper...")
        run = client.actor("clockworks~tiktok-scraper").call(run_input=run_input)
        
        # Monitor the run status
        print(f"Monitoring TikTok scraper run ID: {run['id']}")
        max_wait_time = 600  # 10 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            current_run = client.run(run['id']).get()
            status = current_run['status']
            message = current_run.get('meta', {}).get('message', '')
            
            print(f"Status: {status} - {message}")
            
            if status in ['SUCCEEDED', 'FINISHED', 'COMPLETED']:
                print("✅ TikTok scraper completed successfully!")
                run = current_run
                break
            elif status in ['FAILED', 'ABORTED']:
                raise Exception(f"TikTok scraper failed with status: {status} - {message}")
            
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
        videos = []
        try:
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                videos.append(item)
                if len(videos) % 10 == 0:  # Print progress every 10 items
                    print(f"Retrieved {len(videos)} items so far...")
        except Exception as e:
            print(f"Error retrieving data from dataset: {e}")
            raise
        
        print(f"Retrieved {len(videos)} videos")
        
        return {
            "username": username,
            "fetch_timestamp": datetime.now().isoformat(),
            "total_videos": len(videos),
            "videos": videos
        }
    
    def save_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Save fetched data to JSON file in rawdata folder
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rawdata/tiktok_videos_{data['username']}_{timestamp}.json"
        
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
    """Main function to run the TikTok fetcher"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fetch TikTok videos from a specified account')
    parser.add_argument('username', nargs='?', default='tivoneat', 
                       help='TikTok username to fetch videos from (default: tivoneat)')
    parser.add_argument('--max-videos', '-m', type=int, default=50,
                       help='Maximum number of videos to fetch (default: 50)')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config()
        apify_token = config.get("APIFY_TOKEN") or os.getenv("APIFY_TOKEN")
        
        if not apify_token:
            raise Exception("APIFY_TOKEN not found in config.env or environment variables")
        
        # Initialize fetcher
        fetcher = TikTokFetcher(apify_token)
        
        # Fetch videos
        print(f"🔄 Starting to fetch TikTok videos from @{args.username}...")
        data = fetcher.fetch_tiktok_videos(username=args.username, max_videos=args.max_videos)
        print(f"📊 Data fetched successfully: {len(data.get('videos', []))} videos")
        
        # Save to JSON
        print("💾 Starting to save data to JSON...")
        filename = fetcher.save_to_json(data)
        
        print(f"\n✅ Successfully fetched {data['total_videos']} videos from @{data['username']}")
        print(f"📁 Data saved to: {filename}")
        
        # Display sample video info
        if data['videos']:
            first_video = data['videos'][0]
            print(f"\n📱 Sample video:")
            print(f"   - ID: {first_video.get('id', 'N/A')}")
            print(f"   - Description: {first_video.get('description', 'N/A')[:100] if first_video.get('description') else 'N/A'}...")
            print(f"   - Likes: {first_video.get('likesCount', 'N/A')}")
            print(f"   - Comments: {first_video.get('commentsCount', 'N/A')}")
            print(f"   - Shares: {first_video.get('sharesCount', 'N/A')}")
            print(f"   - Views: {first_video.get('viewsCount', 'N/A')}")
            print(f"   - Duration: {first_video.get('duration', 'N/A')}")
            print(f"   - Video URL: {first_video.get('videoUrl', 'N/A')}")
            
        # Note about limitations
        if data['total_videos'] < args.max_videos:
            print(f"\n⚠️  Note: Only {data['total_videos']} videos were retrieved instead of {args.max_videos}.")
            print("   This could be due to:")
            print("   - Account has fewer videos available")
            print("   - TikTok API limitations")
            print("   - Scraper configuration limitations")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
