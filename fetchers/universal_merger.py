#!/usr/bin/env python3
"""
Universal Social Media Merger Script
Takes social media JSON files (Facebook, Instagram, TikTok) and merges them into a unified format.
This script focuses on merging data without URL validation - use url_validator.py separately for validation.
"""

import os
import json
import argparse
import re
from datetime import datetime
from typing import Dict, List, Any, Optional





def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text content"""
    if not text:
        return []
    
    # Find all hashtags using regex
    hashtag_pattern = r'#\w+'
    hashtags = re.findall(hashtag_pattern, text)
    
    # Remove duplicates and return as list
    return list(set(hashtags))

def extract_images_from_post(post: Dict[str, Any], platform: str) -> List[Dict[str, Any]]:
    """Extract all image data with URLs and likes count from a post"""
    images = []
    
    if platform == 'instagram':
        # Main post images - use post likes count
        if 'displayUrl' in post and post['displayUrl']:
            images.append({
                "url": post['displayUrl'],
                "likes_count": post.get('likesCount', 0)
            })
        
        # Carousel images from main images array
        if 'images' in post and isinstance(post['images'], list):
            for img_url in post['images']:
                images.append({
                    "url": img_url,
                    "likes_count": post.get('likesCount', 0)  # Use post likes for carousel
                })
        
        # Child posts (carousel sub-posts) - each has its own likes
        if 'childPosts' in post and isinstance(post['childPosts'], list):
            for child_post in post['childPosts']:
                if 'displayUrl' in child_post and child_post['displayUrl']:
                    images.append({
                        "url": child_post['displayUrl'],
                        "likes_count": child_post.get('likesCount', 0)
                    })
                if 'images' in child_post and isinstance(child_post['images'], list):
                    for img_url in child_post['images']:
                        images.append({
                            "url": img_url,
                            "likes_count": child_post.get('likesCount', 0)
                        })
        
        # Profile pictures from comments and replies (no likes for profile pics)
        if 'latestComments' in post and isinstance(post['latestComments'], list):
            for comment in post['latestComments']:
                if 'ownerProfilePicUrl' in comment and comment['ownerProfilePicUrl']:
                    images.append({
                        "url": comment['ownerProfilePicUrl'],
                        "likes_count": 0
                    })
                if 'owner' in comment and 'profile_pic_url' in comment['owner'] and comment['owner']['profile_pic_url']:
                    images.append({
                        "url": comment['owner']['profile_pic_url'],
                        "likes_count": 0
                    })
                
                # Replies to comments
                if 'replies' in comment and isinstance(comment['replies'], list):
                    for reply in comment['replies']:
                        if 'ownerProfilePicUrl' in reply and reply['ownerProfilePicUrl']:
                            images.append({
                                "url": reply['ownerProfilePicUrl'],
                                "likes_count": 0
                            })
                        if 'owner' in reply and 'profile_pic_url' in reply['owner'] and reply['owner']['profile_pic_url']:
                            images.append({
                                "url": reply['owner']['profile_pic_url'],
                                "likes_count": 0
                            })
    
    elif platform == 'facebook':
        # Facebook image fields - use post likes
        post_likes = post.get('likes', 0)
        if 'imageUrl' in post and post['imageUrl']:
            images.append({
                "url": post['imageUrl'],
                "likes_count": post_likes
            })
        if 'fullPicture' in post and post['fullPicture']:
            images.append({
                "url": post['fullPicture'],
                "likes_count": post_likes
            })
        if 'picture' in post and post['picture']:
            images.append({
                "url": post['picture'],
                "likes_count": post_likes
            })
        
        # Facebook media array structure
        if 'media' in post and isinstance(post['media'], list):
            for media_item in post['media']:
                # Photo images
                if 'photo_image' in media_item and 'uri' in media_item['photo_image']:
                    images.append({
                        "url": media_item['photo_image']['uri'],
                        "likes_count": post_likes
                    })
                # Thumbnail images
                if 'thumbnail' in media_item and media_item['thumbnail']:
                    images.append({
                        "url": media_item['thumbnail'],
                        "likes_count": post_likes
                    })
                # Video thumbnails
                if 'video' in media_item and 'thumbnail' in media_item['video']:
                    images.append({
                        "url": media_item['video']['thumbnail'],
                        "likes_count": post_likes
                    })
        
        # Profile pictures from comments (no likes for profile pics)
        if 'comments' in post and isinstance(post['comments'], list):
            for comment in post['comments']:
                if 'from' in comment and 'picture' in comment['from'] and comment['from']['picture']:
                    images.append({
                        "url": comment['from']['picture'],
                        "likes_count": 0
                    })
                if 'from' in comment and 'picture' in comment['from'] and 'data' in comment['from']['picture'] and 'url' in comment['from']['picture']['data']:
                    images.append({
                        "url": comment['from']['picture']['data']['url'],
                        "likes_count": 0
                    })
                
                # Replies to comments
                if 'comments' in comment and isinstance(comment['comments'], list):
                    for reply in comment['comments']:
                        if 'from' in reply and 'picture' in reply['from'] and reply['from']['picture']:
                            images.append({
                                "url": reply['from']['picture'],
                                "likes_count": 0
                            })
                        if 'from' in reply and 'picture' in reply['from'] and 'data' in reply['from']['picture'] and 'url' in reply['from']['picture']['data']:
                            images.append({
                                "url": reply['from']['picture']['data']['url'],
                                "likes_count": 0
                            })
    
    elif platform == 'tiktok':
        # TikTok video thumbnails and covers - use video likes
        video_likes = post.get('diggCount', 0)
        if 'video' in post and 'cover' in post['video']:
            images.append({
                "url": post['video']['cover'],
                "likes_count": video_likes
            })
        if 'video' in post and 'originCover' in post['video']:
            images.append({
                "url": post['video']['originCover'],
                "likes_count": video_likes
            })
        if 'video' in post and 'dynamicCover' in post['video']:
            images.append({
                "url": post['video']['dynamicCover'],
                "likes_count": video_likes
            })
        
        # Author profile picture (no likes for profile pics)
        if 'author' in post and 'avatarMedium' in post['author']:
            images.append({
                "url": post['author']['avatarMedium'],
                "likes_count": 0
            })
        if 'author' in post and 'avatarLarger' in post['author']:
            images.append({
                "url": post['author']['avatarLarger'],
                "likes_count": 0
            })
        if 'author' in post and 'avatarThumb' in post['author']:
            images.append({
                "url": post['author']['avatarThumb'],
                "likes_count": 0
            })
        
        # Comment profile pictures (no likes for profile pics)
        if 'comments' in post and isinstance(post['comments'], list):
            for comment in post['comments']:
                if 'user' in comment and 'avatarMedium' in comment['user']:
                    images.append({
                        "url": comment['user']['avatarMedium'],
                        "likes_count": 0
                    })
                if 'user' in comment and 'avatarLarger' in comment['user']:
                    images.append({
                        "url": comment['user']['avatarLarger'],
                        "likes_count": 0
                    })
                if 'user' in comment and 'avatarThumb' in comment['user']:
                    images.append({
                        "url": comment['user']['avatarThumb'],
                        "likes_count": 0
                    })
                
                # Replies to comments
                if 'reply_comment' in comment and isinstance(comment['reply_comment'], list):
                    for reply in comment['reply_comment']:
                        if 'user' in reply and 'avatarMedium' in reply['user']:
                            images.append({
                                "url": reply['user']['avatarMedium'],
                                "likes_count": 0
                            })
                        if 'user' in reply and 'avatarLarger' in reply['user']:
                            images.append({
                                "url": reply['user']['avatarLarger'],
                                "likes_count": 0
                            })
                        if 'user' in reply and 'avatarThumb' in reply['user']:
                            images.append({
                                "url": reply['user']['avatarThumb'],
                                "likes_count": 0
                            })
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_images = []
    for img in images:
        if img['url'] and img['url'].strip() and img['url'] not in seen_urls:
            seen_urls.add(img['url'])
            unique_images.append(img)
    
    return unique_images

def extract_videos_from_post(post: Dict[str, Any], platform: str, video_url: str = "") -> List[Dict[str, Any]]:
    """Extract all video data with URLs and likes count from a post"""
    videos = []
    
    # Add the main video_url if provided
    if video_url and video_url.strip():
        # Get the correct likes count based on platform
        if platform == 'tiktok':
            likes_count = post.get('diggCount', 0)
        elif platform == 'instagram':
            likes_count = post.get('likesCount', 0)
        elif platform == 'facebook':
            likes_count = post.get('likes', 0)
        else:
            likes_count = post.get('likesCount', post.get('likes', 0))
        
        videos.append({
            "url": video_url,
            "likes_count": likes_count
        })
    
    if platform == 'instagram':
        # Main post video - use post likes
        post_likes = post.get('likesCount', 0)
        if 'videoUrl' in post and post['videoUrl']:
            videos.append({
                "url": post['videoUrl'],
                "likes_count": post_likes
            })
        if 'video_url' in post and post['video_url']:
            videos.append({
                "url": post['video_url'],
                "likes_count": post_likes
            })
        
        # Child posts (carousel sub-posts) videos - each has its own likes
        if 'childPosts' in post and isinstance(post['childPosts'], list):
            for child_post in post['childPosts']:
                child_likes = child_post.get('likesCount', 0)
                if 'videoUrl' in child_post and child_post['videoUrl']:
                    videos.append({
                        "url": child_post['videoUrl'],
                        "likes_count": child_likes
                    })
                if 'video_url' in child_post and child_post['video_url']:
                    videos.append({
                        "url": child_post['video_url'],
                        "likes_count": child_likes
                    })
        
        # Check if post type is video
        if post.get('type') == 'Video' and 'displayUrl' in post:
            # For video posts, the displayUrl might be a video thumbnail, but we'll include it
            # The actual video URL might be in videoUrl field
            pass
    
    elif platform == 'facebook':
        # Facebook video fields - use post likes
        post_likes = post.get('likes', 0)
        if 'videoUrl' in post and post['videoUrl']:
            videos.append({
                "url": post['videoUrl'],
                "likes_count": post_likes
            })
        if 'source' in post and post['source']:
            videos.append({
                "url": post['source'],
                "likes_count": post_likes
            })
        if 'link' in post and post['link'] and ('video' in post['link'].lower() or 'youtube' in post['link'].lower() or 'vimeo' in post['link'].lower()):
            videos.append({
                "url": post['link'],
                "likes_count": post_likes
            })
        
        # Check for embedded videos in attachments
        if 'attachments' in post and isinstance(post['attachments'], list):
            for attachment in post['attachments']:
                if 'media' in attachment and 'video' in attachment['media']:
                    if 'source' in attachment['media']['video']:
                        videos.append({
                            "url": attachment['media']['video']['source'],
                            "likes_count": post_likes
                        })
                if 'subattachments' in attachment and isinstance(attachment['subattachments'], list):
                    for subattachment in attachment['subattachments']:
                        if 'media' in subattachment and 'video' in subattachment['media']:
                            if 'source' in subattachment['media']['video']:
                                videos.append({
                                    "url": subattachment['media']['video']['source'],
                                    "likes_count": post_likes
                                })
    
    elif platform == 'tiktok':
        # TikTok video URLs - use video likes
        video_likes = post.get('diggCount', 0)
        if 'video' in post and 'downloadAddr' in post['video']:
            videos.append({
                "url": post['video']['downloadAddr'],
                "likes_count": video_likes
            })
        if 'video' in post and 'playAddr' in post['video']:
            videos.append({
                "url": post['video']['playAddr'],
                "likes_count": video_likes
            })
        if 'video' in post and 'playApi' in post['video']:
            videos.append({
                "url": post['video']['playApi'],
                "likes_count": video_likes
            })
        if 'webVideoUrl' in post and post['webVideoUrl']:
            videos.append({
                "url": post['webVideoUrl'],
                "likes_count": video_likes
            })
        if 'videoUrl' in post and post['videoUrl']:
            videos.append({
                "url": post['videoUrl'],
                "likes_count": video_likes
            })
        
        # TikTok share URL (web version)
        if 'shareUrl' in post and post['shareUrl']:
            videos.append({
                "url": post['shareUrl'],
                "likes_count": video_likes
            })
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_videos = []
    for video in videos:
        if video['url'] and video['url'].strip() and video['url'] not in seen_urls:
            seen_urls.add(video['url'])
            unique_videos.append(video)
    
    return unique_videos

def extract_reply_data(post: Dict[str, Any], platform: str) -> List[Dict[str, Any]]:
    """Extract all reply data with text and likes count from a post based on platform"""
    all_replies = []
    
    if platform == 'instagram':
        # Instagram has latestComments with nested replies
        latest_comments = post.get('latestComments', [])
        for comment in latest_comments:
            # Add the main comment text with likes
            comment_text = comment.get('text', '')
            comment_likes = comment.get('likesCount', 0)
            if comment_text:
                all_replies.append({
                    "comment": comment_text,
                    "likes_count": comment_likes
                })
            
            # Add replies to this comment
            replies = comment.get('replies', [])
            for reply in replies:
                reply_text = reply.get('text', '')
                reply_likes = reply.get('likesCount', 0)
                if reply_text:
                    all_replies.append({
                        "comment": reply_text,
                        "likes_count": reply_likes
                    })
        
        # Remove duplicate comments based on text content
        seen_comments = set()
        unique_replies = []
        for reply in all_replies:
            comment_text = reply['comment']
            if comment_text not in seen_comments:
                seen_comments.add(comment_text)
                unique_replies.append(reply)
        
        all_replies = unique_replies
    
    elif platform == 'facebook':
        # Facebook structure - check for comments array
        comments = post.get('comments', [])
        if isinstance(comments, list):
            for comment in comments:
                comment_text = comment.get('text', comment.get('message', ''))
                comment_likes = comment.get('likes', 0)
                if comment_text:
                    all_replies.append({
                        "comment": comment_text,
                        "likes_count": comment_likes
                    })
                
                # Check for replies to this comment
                comment_replies = comment.get('replies', comment.get('comments', []))
                if isinstance(comment_replies, list):
                    for reply in comment_replies:
                        reply_text = reply.get('text', reply.get('message', ''))
                        reply_likes = reply.get('likes', 0)
                        if reply_text:
                            all_replies.append({
                                "comment": reply_text,
                                "likes_count": reply_likes
                            })
        else:
            # If comments is just a count, add placeholder
            comment_count = post.get('comments', 0)
            if comment_count > 0:
                all_replies.append({
                    "comment": f'[{comment_count} comments available but not extracted]',
                    "likes_count": 0
                })
    
    elif platform == 'tiktok':
        # TikTok structure - check for comments
        comments = post.get('comments', [])
        if isinstance(comments, list):
            for comment in comments:
                comment_text = comment.get('text', '')
                comment_likes = comment.get('likesCount', 0)
                if comment_text:
                    all_replies.append({
                        "comment": comment_text,
                        "likes_count": comment_likes
                    })
                
                # Check for replies to this comment
                comment_replies = comment.get('reply_comment', [])
                if isinstance(comment_replies, list):
                    for reply in comment_replies:
                        reply_text = reply.get('text', '')
                        reply_likes = reply.get('likesCount', 0)
                        if reply_text:
                            all_replies.append({
                                "comment": reply_text,
                                "likes_count": reply_likes
                            })
        else:
            # If comments is just a count, add placeholder
            comment_count = post.get('commentCount', 0)
            if comment_count > 0:
                all_replies.append({
                    "comment": f'[{comment_count} comments available but not extracted]',
                    "likes_count": 0
                })
    
    return all_replies

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
    
    # Extract content, hashtags, reply data, images, and videos
    content = post.get("text", "")
    hashtags = extract_hashtags(content)
    replies_data = extract_reply_data(post, "facebook")
    images = extract_images_from_post(post, "facebook")
    video_url = post.get("url", "")
    videos = extract_videos_from_post(post, "facebook", video_url)
    
    return {
        "post_time": post_time,
        "content": content,
        "social_network": "facebook",
        "likes_count": likes_count,
        "comments_count": comments_count,
        "views": 0,  # Facebook doesn't have views
        "plays": 0,  # Facebook doesn't have plays
        "shares": shares_count,
        "saves": 0,  # Facebook doesn't have saves
        "hashtags": hashtags,
        "replies_data": replies_data,
        "images": images,
        "videos": videos
    }

def convert_instagram_post(post: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Instagram post to person1.json format"""
    # Extract time from timestamp
    timestamp = post.get("timestamp", "")
    if timestamp:
        try:
            # Handle ISO format timestamps (e.g., "2025-08-31T13:50:16.000Z")
            if 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                post_time = dt.strftime("%Y-%m-%d %H:%M:%S+00")
            else:
                # Handle Unix timestamp format
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
    
    # Extract content, hashtags, reply data, images, and videos
    content = post.get("caption", "")
    hashtags = extract_hashtags(content)
    replies_data = extract_reply_data(post, "instagram")
    images = extract_images_from_post(post, "instagram")
    video_url = post.get("url", "")
    videos = extract_videos_from_post(post, "instagram", video_url)
    
    return {
        "post_time": post_time,
        "content": content,
        "social_network": "instagram",
        "likes_count": likes_count,
        "comments_count": comments_count,
        "views": video_views,
        "plays": video_plays,
        "shares": 0,  # Instagram doesn't have shares
        "saves": 0,  # Instagram doesn't have saves
        "hashtags": hashtags,
        "replies_data": replies_data,
        "images": images,
        "videos": videos
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
    
    # Extract content, hashtags, reply data, images, and videos
    content = video.get("text", "")
    hashtags = extract_hashtags(content)
    replies_data = extract_reply_data(video, "tiktok")
    images = extract_images_from_post(video, "tiktok")
    video_url = video.get("webVideoUrl", "")
    videos = extract_videos_from_post(video, "tiktok", video_url)
    
    return {
        "post_time": post_time,
        "content": content,
        "social_network": "tiktok",
        "likes_count": likes_count,
        "comments_count": comments_count,
        "views": views_count,
        "plays": views_count,
        "shares": shares_count,
        "saves": saves_count,
        "hashtags": hashtags,
        "replies_data": replies_data,
        "images": images,
        "videos": videos
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
        
        # Keep all URLs as they are - no validation during merge
        print(f"   📊 Processing {len(all_converted_posts)} posts with all media URLs...")
        
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
    # Extract content, hashtags, reply data, images, and videos
    content = post.get("text", post.get("content", post.get("caption", "")))
    hashtags = extract_hashtags(content)
    replies_data = extract_reply_data(post, "unknown")
    images = extract_images_from_post(post, "unknown")
    video_url = post.get("url", post.get("video_url", ""))
    videos = extract_videos_from_post(post, "unknown", video_url)
    
    return {
        "post_time": post.get("time", post.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S+00"))),
        "content": content,
        "social_network": "unknown",
        "likes_count": post.get("likes", post.get("likes_count", 0)),
        "comments_count": post.get("comments", post.get("comments_count", 0)),
        "views": post.get("views", post.get("view_count", 0)),
        "plays": post.get("plays", post.get("play_count", 0)),
        "shares": post.get("shares", post.get("share_count", 0)),
        "saves": post.get("saves", post.get("save_count", 0)),
        "hashtags": hashtags,
        "replies_data": replies_data,
        "images": images,
        "videos": videos
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
    else:
        print(f"👥 Found {len(username_files)} unique usernames to process")
        print("🔄 Processing ALL usernames found in rawdata folder...")
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
