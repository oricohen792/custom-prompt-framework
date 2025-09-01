#!/usr/bin/env python3
"""
Universal Social Media Merger Script
Takes any 3 social media JSON files (Facebook, Instagram, TikTok) and builds a person JSON file
with the exact structure of person1.json
"""

import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load JSON file and return its content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return {}

def detect_platform(filepath: str, data: Dict[str, Any]) -> str:
    """Detect which platform the JSON file is from"""
    filename = filepath.lower()
    
    # Check filename first
    if 'facebook' in filename:
        return 'facebook'
    elif 'instagram' in filename:
        return 'instagram'
    elif 'tiktok' in filename:
        return 'tiktok'
    
    # Check data structure
    if 'posts' in data and data['posts']:
        first_post = data['posts'][0]
        if 'facebookUrl' in first_post or 'facebookId' in first_post:
            return 'facebook'
        elif 'shortCode' in first_post or 'ownerUsername' in first_post:
            return 'instagram'
    
    if 'videos' in data and data['videos']:
        first_video = data['videos'][0]
        if 'diggCount' in first_video or 'playCount' in first_video:
            return 'tiktok'
    
    # Default based on common fields
    if 'posts' in data:
        if any('likesCount' in str(post) for post in data['posts'][:3]):
            return 'instagram'
        else:
            return 'facebook'
    
    return 'unknown'

def convert_facebook_post(post: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Facebook post to person1.json format"""
    # Extract time and convert to required format
    post_time = post.get("time", "")
    if post_time:
        try:
            dt = datetime.fromisoformat(post_time.replace('Z', '+00:00'))
            post_time = dt.strftime("%Y-%m-%d %H:%M:%S+00")
        except:
            post_time = "2025-08-31 00:00:00+00"
    
    # Extract all available statistics
    likes_count = post.get("likes", 0)
    comments_count = post.get("comments", 0)
    shares_count = post.get("shares", 0)
    
    return {
        "post_time": post_time,
        "content": post.get("text", ""),
        "social_network": "facebook",
        "likes_count": likes_count,
        "comments_count": comments_count,
        "views": 0,  # Facebook doesn't have views
        "plays": 0,  # Facebook doesn't have plays
        "shares": shares_count,
        "saves": 0,  # Facebook doesn't have saves
        "video_url": post.get("url", ""),
        "replies_data": []
    }

def convert_instagram_post(post: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Instagram post to person1.json format"""
    # Extract time from timestamp
    timestamp = post.get("timestamp", "")
    if timestamp:
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            post_time = dt.strftime("%Y-%m-%d %H:%M:%S+00")
        except:
            post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S+00")
    else:
        post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S+00")
    
    # Extract all available statistics
    likes_count = post.get("likesCount", 0)
    comments_count = post.get("commentsCount", 0)
    video_views = post.get("videoViewCount", 0)
    video_plays = post.get("videoPlayCount", 0)
    
    return {
        "post_time": post_time,
        "content": post.get("caption", ""),
        "social_network": "instagram",
        "likes_count": likes_count,
        "comments_count": comments_count,
        "views": video_views,
        "plays": video_plays,
        "shares": 0,  # Instagram doesn't have shares
        "saves": 0,  # Instagram doesn't have saves
        "video_url": post.get("url", ""),
        "replies_data": []
    }

def convert_tiktok_video(video: Dict[str, Any]) -> Dict[str, Any]:
    """Convert TikTok video to person1.json format"""
    # Extract time and convert to required format
    post_time = video.get("createTimeISO", "")
    if post_time:
        try:
            dt = datetime.fromisoformat(post_time.replace('Z', '+00:00'))
            post_time = dt.strftime("%Y-%m-%d %H:%M:%S+00")
        except:
            post_time = "2025-08-31 00:00:00+00"
    else:
        post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S+00")
    
    # Extract all available statistics
    likes_count = video.get("diggCount", 0)
    comments_count = video.get("commentCount", 0)
    views_count = video.get("playCount", 0)
    shares_count = video.get("shareCount", 0)
    saves_count = video.get("collectCount", 0)
    
    return {
        "post_time": post_time,
        "content": video.get("text", ""),
        "social_network": "tiktok",
        "likes_count": likes_count,
        "comments_count": comments_count,
        "views": views_count,
        "plays": views_count,
        "shares": shares_count,
        "saves": saves_count,
        "video_url": video.get("webVideoUrl", ""),
        "replies_data": []
    }

def list_available_rawdata_files(rawdata_dir: str) -> None:
    """List all available JSON files in the rawdata directory"""
    print(f"📁 Available JSON files in {rawdata_dir} folder:")
    print("=" * 60)
    
    if not os.path.exists(rawdata_dir):
        print(f"❌ Directory not found: {rawdata_dir}")
        return
    
    json_files = [f for f in os.listdir(rawdata_dir) if f.endswith('.json')]
    
    if not json_files:
        print("📁 No JSON files found")
        return
    
    for i, filename in enumerate(sorted(json_files), 1):
        file_path = os.path.join(rawdata_dir, filename)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            print(f"   {i:2d}. {filename} ({file_size_mb:.2f} MB)")
    
    print(f"\n📊 Total: {len(json_files)} JSON files")

def get_rawdata_files(rawdata_dir: str) -> List[str]:
    """Get all JSON files from the rawdata directory"""
    if not os.path.exists(rawdata_dir):
        return []
    
    json_files = [f for f in os.listdir(rawdata_dir) if f.endswith('.json')]
    return [os.path.join(rawdata_dir, f) for f in json_files]

def group_files_by_username(rawdata_files: List[str]) -> Dict[str, List[str]]:
    """Group rawdata files by username"""
    username_files = {}
    
    for filepath in rawdata_files:
        username = extract_username_from_filename(filepath)
        if username:
            username_lower = username.lower()
            if username_lower not in username_files:
                username_files[username_lower] = []
            username_files[username_lower].append(filepath)
    
    return username_files

def merge_username_platforms(username: str, platform_files: List[str], output_file: str) -> bool:
    """Merge all platform files for a specific username into one analysis file"""
    try:
        print(f"   📖 Loading {len(platform_files)} platform files...")
        
        # Load all platform files
        platform_data = []
        for filepath in platform_files:
            data = load_json_file(filepath)
            if data:
                platform = detect_platform(filepath, data)
                platform_data.append((platform, data, filepath))
                print(f"      - {platform}: {os.path.basename(filepath)}")
        
        if not platform_data:
            print(f"   ❌ No valid data loaded from platform files")
            return False
        
        # Convert all posts from all platforms
        all_converted_posts = []
        
        for platform, data, filepath in platform_data:
            print(f"   🔄 Converting {platform} posts...")
            
            if platform == 'facebook':
                posts = data.get("posts", [])
                for post in posts:
                    converted_post = convert_facebook_post(post)
                    all_converted_posts.append(converted_post)
                print(f"      - Converted {len(posts)} Facebook posts")
                
            elif platform == 'instagram':
                posts = data.get("posts", [])
                for post in posts:
                    converted_post = convert_instagram_post(post)
                    all_converted_posts.append(converted_post)
                print(f"      - Converted {len(posts)} Instagram posts")
                
            elif platform == 'tiktok':
                videos = data.get("videos", [])
                for video in videos:
                    converted_post = convert_tiktok_video(video)
                    all_converted_posts.append(converted_post)
                print(f"      - Converted {len(videos)} TikTok videos")
            
            else:
                print(f"      ⚠️  Unknown platform {platform}, attempting generic conversion")
                if 'posts' in data:
                    posts = data.get("posts", [])
                    for post in posts:
                        converted_post = convert_generic_post(post)
                        all_converted_posts.append(converted_post)
                    print(f"      - Converted {len(posts)} generic posts")
        
        if not all_converted_posts:
            print(f"   ❌ No posts converted from any platform")
            return False
        
        # Sort by post time (newest first)
        print(f"   🔄 Sorting {len(all_converted_posts)} posts by time...")
        all_converted_posts.sort(key=lambda x: x["post_time"], reverse=True)
        
        # Calculate comprehensive statistics
        total_likes = sum(post["likes_count"] for post in all_converted_posts)
        total_comments = sum(post["comments_count"] for post in all_converted_posts)
        total_views = sum(post["views"] for post in all_converted_posts)
        total_plays = sum(post["plays"] for post in all_converted_posts)
        total_shares = sum(post["shares"] for post in all_converted_posts)
        total_saves = sum(post["saves"] for post in all_converted_posts)
        
        # Platform-specific stats
        fb_posts = [p for p in all_converted_posts if p["social_network"] == "facebook"]
        ig_posts = [p for p in all_converted_posts if p["social_network"] == "instagram"]
        tt_posts = [p for p in all_converted_posts if p["social_network"] == "tiktok"]
        
        print(f"   📊 Platform breakdown:")
        print(f"      - Facebook: {len(fb_posts)} posts")
        print(f"      - Instagram: {len(ig_posts)} posts")
        print(f"      - TikTok: {len(tt_posts)} posts")
        print(f"      - Total: {len(all_converted_posts)} posts")
        
        print(f"   📈 Statistics:")
        print(f"      - Total likes: {total_likes:,}")
        print(f"      - Total comments: {total_comments:,}")
        print(f"      - Total views: {total_views:,}")
        print(f"      - Total shares: {total_shares:,}")
        
        # Create the final merged structure - just the posts array
        final_data = all_converted_posts
        
        # Save the merged data
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Saved merged data to: {output_file}")
        
        # Get file size
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        print(f"   📁 File size: {file_size_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error merging platforms for {username}: {e}")
        return False

def extract_username_from_filename(filepath: str) -> Optional[str]:
    """Extract username from filename"""
    filename = os.path.basename(filepath)
    
    # Remove file extension
    name = filename.replace('.json', '')
    
    # Common patterns for our naming convention
    # facebook_posts_taylorswift_20250831_220201.json -> taylorswift
    # instagram_posts_taylorswift_20250831_220201.json -> taylorswift
    # tiktok_videos_taylorswift_20250831_220016.json -> taylorswift
    
    if '_' in name:
        parts = name.split('_')
        
        # Try different patterns
        if len(parts) >= 3:
            # Pattern: platform_posts_username_timestamp
            username = parts[2]
            return username
        elif len(parts) >= 2:
            # Fallback: platform_username
            username = parts[1]
            return username
    
    # If no underscore, return the whole name
    return name



def convert_generic_post(post: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a generic post to the required format"""
    return {
        "post_time": post.get("time", post.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S+00"))),
        "content": post.get("text", post.get("content", post.get("caption", ""))),
        "social_network": "unknown",
        "likes_count": post.get("likes", post.get("likes_count", 0)),
        "comments_count": post.get("comments", post.get("comments_count", 0)),
        "views": post.get("views", post.get("view_count", 0)),
        "plays": post.get("plays", post.get("play_count", 0)),
        "shares": post.get("shares", post.get("share_count", 0)),
        "saves": post.get("saves", post.get("save_count", 0)),
        "video_url": post.get("url", post.get("video_url", "")),
        "replies_data": []
    }

def merge_social_media_files(file1: str, file2: str, file3: str, output_file: str, username: str = None) -> bool:
    """Merge three social media JSON files into one person JSON file"""
    
    print("🔄 Starting universal social media merger...")
    print("=" * 60)
    
    # Load all three JSON files
    files = [file1, file2, file3]
    data_sources = []
    
    for i, filepath in enumerate(files, 1):
        print(f"📖 Loading file {i}: {filepath}")
        data = load_json_file(filepath)
        if not data:
            print(f"❌ Failed to load {filepath}")
            return False
        
        platform = detect_platform(filepath, data)
        print(f"   - Detected platform: {platform}")
        data_sources.append((platform, data, filepath))
    
    # Validate we have all three platforms
    platforms = [source[0] for source in data_sources]
    if len(set(platforms)) < 3:
        print("❌ Error: Need files from 3 different platforms (Facebook, Instagram, TikTok)")
        return False
    
    # Convert all posts to person1.json format
    converted_posts = []
    
    for platform, data, filepath in data_sources:
        print(f"🔄 Converting {platform} posts from {os.path.basename(filepath)}...")
        
        if platform == 'facebook':
            posts = data.get("posts", [])
            for post in posts:
                converted_post = convert_facebook_post(post)
                converted_posts.append(converted_post)
            print(f"   - Converted {len(posts)} Facebook posts")
            
        elif platform == 'instagram':
            posts = data.get("posts", [])
            for post in posts:
                converted_post = convert_instagram_post(post)
                converted_posts.append(converted_post)
            print(f"   - Converted {len(posts)} Instagram posts")
            
        elif platform == 'tiktok':
            videos = data.get("videos", [])
            for video in videos:
                converted_post = convert_tiktok_video(video)
                converted_posts.append(converted_post)
            print(f"   - Converted {len(videos)} TikTok videos")
    
    # Sort by post time (newest first)
    print("🔄 Sorting posts by time...")
    converted_posts.sort(key=lambda x: x["post_time"], reverse=True)
    
    # Calculate comprehensive statistics summary
    total_likes = sum(post["likes_count"] for post in converted_posts)
    total_comments = sum(post["comments_count"] for post in converted_posts)
    total_views = sum(post["views"] for post in converted_posts)
    total_plays = sum(post["plays"] for post in converted_posts)
    total_shares = sum(post["shares"] for post in converted_posts)
    total_saves = sum(post["saves"] for post in converted_posts)
    
    # Platform-specific stats
    fb_posts = [p for p in converted_posts if p["social_network"] == "facebook"]
    ig_posts = [p for p in converted_posts if p["social_network"] == "instagram"]
    tt_posts = [p for p in converted_posts if p["social_network"] == "tiktok"]
    
    print(f"\n📊 Conversion summary:")
    print(f"   - Facebook posts converted: {len(fb_posts)}")
    print(f"   - Instagram posts converted: {len(ig_posts)}")
    print(f"   - TikTok videos converted: {len(tt_posts)}")
    print(f"   - Total converted posts: {len(converted_posts)}")
    
    print(f"\n📈 Comprehensive Statistics Summary:")
    print(f"   - Total likes: {total_likes:,}")
    print(f"   - Total comments: {total_comments:,}")
    print(f"   - Total views: {total_views:,}")
    print(f"   - Total plays: {total_plays:,}")
    print(f"   - Total shares: {total_shares:,}")
    print(f"   - Total saves: {total_saves:,}")
    
    # Platform-specific stats
    if fb_posts:
        fb_likes = sum(p["likes_count"] for p in fb_posts)
        fb_comments = sum(p["comments_count"] for p in fb_posts)
        fb_shares = sum(p["shares"] for p in fb_posts)
        print(f"   📘 Facebook: {fb_likes:,} likes, {fb_comments:,} comments, {fb_shares:,} shares")
    
    if ig_posts:
        ig_likes = sum(p["likes_count"] for p in ig_posts)
        ig_comments = sum(p["comments_count"] for p in ig_posts)
        ig_views = sum(p["views"] for p in ig_posts)
        print(f"   📷 Instagram: {ig_likes:,} likes, {ig_comments:,} comments, {ig_views:,} views")
    
    if tt_posts:
        tt_likes = sum(p["likes_count"] for p in tt_posts)
        tt_comments = sum(p["comments_count"] for p in tt_posts)
        tt_views = sum(p["views"] for p in tt_posts)
        tt_saves = sum(p["saves"] for p in tt_posts)
        print(f"   🎬 TikTok: {tt_likes:,} likes, {tt_comments:,} comments, {tt_views:,} views, {tt_saves:,} saves")
    
    # Save the merged data
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(converted_posts, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Merged data saved to: {output_file}")
        
        # Get file size
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        print(f"📁 File size: {file_size_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving merged data: {e}")
        return False

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Merge social media JSON files from rawdata folder into person JSON files')
    parser.add_argument('-o', '--output-dir', default='data', help='Output directory for merged files (default: data)')
    parser.add_argument('-r', '--rawdata-dir', default='rawdata', help='Raw data directory to scan (default: rawdata)')
    parser.add_argument('-u', '--username', help='Specific username to process (optional, processes all if not specified)')
    parser.add_argument('-l', '--list-files', action='store_true', help='List available raw data files and exit')
    
    args = parser.parse_args()
    
    # List available files if requested
    if args.list_files:
        list_available_rawdata_files(args.rawdata_dir)
        return 0
    
    # Get all JSON files from rawdata folder
    rawdata_files = get_rawdata_files(args.rawdata_dir)
    
    if not rawdata_files:
        print(f"❌ No JSON files found in {args.rawdata_dir} folder")
        return 1
    
    print("🚀 Universal Social Media Merger")
    print("=" * 60)
    print(f"📁 Raw data directory: {args.rawdata_dir}")
    print(f"📁 Output directory: {args.output_dir}")
    print(f"📁 Found {len(rawdata_files)} JSON files")
    
    # Group files by username
    username_files = group_files_by_username(rawdata_files)
    
    if args.username:
        print(f"👤 Processing specific username: {args.username}")
        if args.username.lower() in username_files:
            username_files = {args.username.lower(): username_files[args.username.lower()]}
        else:
            print(f"❌ No files found for username: {args.username}")
            return 1
    
    print(f"👥 Found {len(username_files)} unique usernames to process")
    print()
    
    # Process each username's files
    success_count = 0
    total_usernames = len(username_files)
    
    for username, files in username_files.items():
        print(f"🔄 Processing {username} ({len(files)} platform files)")
        
        # Create output filename
        output_file = os.path.join(args.output_dir, f"{username}_analysis.json")
        
        # Merge all platform files for this username
        success = merge_username_platforms(username, files, output_file)
        
        if success:
            success_count += 1
            print(f"   ✅ Successfully merged {username} ({len(files)} platforms)")
        else:
            print(f"   ❌ Failed to merge {username}")
        
        print()
    
    # Summary
    print("🎯 Processing Summary")
    print("=" * 60)
    print(f"📊 Total usernames: {total_usernames}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {total_usernames - success_count}")
    
    if success_count > 0:
        print(f"\n📁 Output directory contents:")
        if os.path.exists(args.output_dir):
            for file in os.listdir(args.output_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(args.output_dir, file)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        file_size_mb = file_size / (1024 * 1024)
                        print(f"   - {file}: {file_size_mb:.2f} MB")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    exit(main())
