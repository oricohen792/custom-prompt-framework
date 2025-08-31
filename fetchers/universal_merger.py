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
    parser = argparse.ArgumentParser(description='Merge 3 social media JSON files into one person JSON file')
    parser.add_argument('file1', help='First social media JSON file')
    parser.add_argument('file2', help='Second social media JSON file')
    parser.add_argument('file3', help='Third social media JSON file')
    parser.add_argument('-o', '--output', default='data/person.json', help='Output JSON file path (default: data/person.json)')
    parser.add_argument('-u', '--username', help='Username for the person (optional)')
    
    args = parser.parse_args()
    
    # Check if input files exist
    for filepath in [args.file1, args.file2, args.file3]:
        if not os.path.exists(filepath):
            print(f"❌ Error: File not found: {filepath}")
            return 1
    
    print("🚀 Universal Social Media Merger")
    print("=" * 60)
    print(f"📁 Input files:")
    print(f"   1. {args.file1}")
    print(f"   2. {args.file2}")
    print(f"   3. {args.file3}")
    print(f"📁 Output file: {args.output}")
    if args.username:
        print(f"👤 Username: {args.username}")
    print()
    
    # Perform the merge
    success = merge_social_media_files(args.file1, args.file2, args.file3, args.output, args.username)
    
    if success:
        print("\n🎯 Merge completed successfully!")
        print(f"📁 Output file: {args.output}")
        
        # Verify the file was created
        if os.path.exists(args.output):
            print(f"✅ File verification: {args.output} exists")
            
            # Show final directory contents
            output_dir = os.path.dirname(args.output)
            if output_dir and os.path.exists(output_dir):
                print(f"\n📂 Output directory contents:")
                for file in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, file)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        file_size_mb = file_size / (1024 * 1024)
                        print(f"   - {file}: {file_size_mb:.2f} MB")
        else:
            print(f"❌ Error: {args.output} was not created")
            return 1
    else:
        print("\n❌ Merge failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
