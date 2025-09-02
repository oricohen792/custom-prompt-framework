#!/usr/bin/env python3
"""
Video Downloader Tool

This tool:
1. Loads video data from JSON files in the data folder
2. Selects the top 10 videos with most likes/views from different posts
3. Downloads the videos
4. Transcribes them using OpenAI
5. Saves the transcription results back to the JSON files
"""

import json
import os
import requests
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import openai
from urllib.parse import urlparse
import time

# Load environment variables
load_dotenv('../config.env')

class VideoDownloader:
    def __init__(self):
        # Load environment variables
        load_dotenv('../config.env')
        
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please check config.env file.")
        
        print(f"✓ OpenAI API key loaded (length: {len(api_key)})")
        self.openai_client = openai.OpenAI(api_key=api_key)
        self.data_dir = Path('../rawdata')
        self.download_dir = Path('../downloads')
        self.download_dir.mkdir(exist_ok=True)
        
    def load_json_files(self, filter_tivoneat: bool = True) -> List[Dict[str, Any]]:
        """Load JSON files from the data directory, optionally filtering for tivoneat only"""
        all_posts = []
        
        for json_file in self.data_dir.glob('*.json'):
            # Filter for tivoneat files only if requested
            if filter_tivoneat and 'tivoneat' not in json_file.name:
                continue
            
            # Skip Twitter/X related files
            if 'twitter' in json_file.name.lower() or 'x.com' in json_file.name.lower():
                print(f"Skipping Twitter file: {json_file.name}")
                continue
                
            print(f"Loading {json_file.name}...")
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Handle different JSON structures
                    if 'posts' in data:
                        # Facebook/Instagram structure
                        posts = data['posts']
                        # Convert Instagram video posts to videos array format
                        for post in posts:
                            if post.get('type') == 'Video' and 'videoUrl' in post:
                                # Create videos array for Instagram video posts
                                post['videos'] = [{
                                    'url': post['videoUrl'],
                                    'likes_count': post.get('likesCount', 0),
                                    'cover_url': post.get('displayUrl', ''),
                                    'duration': 0  # Instagram doesn't provide duration in this format
                                }]
                                post['social_network'] = 'instagram'
                            elif post.get('isVideo') and 'media' in post:
                                # Handle Facebook video posts
                                videos = []
                                for media_item in post['media']:
                                    if media_item.get('__typename') == 'Video' and 'url' in media_item:
                                        videos.append({
                                            'url': media_item['url'],
                                            'likes_count': post.get('likes', 0),
                                            'cover_url': media_item.get('thumbnail', ''),
                                            'duration': media_item.get('playable_duration_in_ms', 0) / 1000  # Convert ms to seconds
                                        })
                                if videos:
                                    post['videos'] = videos
                                    post['social_network'] = 'facebook'
                                    post['views'] = post.get('viewsCount', 0)
                                    post['comments_count'] = post.get('comments', 0)
                                    post['shares'] = post.get('shares', 0)
                    elif 'videos' in data:
                        # TikTok structure - convert videos to posts format
                        posts = []
                        for video in data['videos']:
                            post = {
                                'id': video.get('id', ''),
                                'content': video.get('text', ''),
                                'post_time': video.get('createTimeISO', ''),
                                'social_network': 'tiktok',
                                'likes': video.get('diggCount', 0),
                                'views': video.get('playCount', 0),
                                'comments_count': video.get('commentCount', 0),
                                'shares': video.get('shareCount', 0),
                                'videos': [{
                                    'url': video.get('webVideoUrl', ''),
                                    'likes_count': video.get('diggCount', 0),
                                    'cover_url': video.get('videoMeta', {}).get('coverUrl', ''),
                                    'duration': video.get('videoMeta', {}).get('duration', 0)
                                }],
                                'bed_videos': []  # Initialize bed_videos array
                            }
                            posts.append(post)
                    else:
                        # Assume it's a list of posts
                        posts = data if isinstance(data, list) else [data]
                    
                    # Add source file info to each post
                    for post in posts:
                        post['_source_file'] = json_file.name
                        # Ensure bed_videos array exists
                        if 'bed_videos' not in post:
                            post['bed_videos'] = []
                    
                    all_posts.extend(posts)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                
        return all_posts
    
    def clean_author_content(self, content: str) -> str:
        """Clean content to only include author's actual content, removing hashtags, mentions, and URLs"""
        if not content:
            return ""
        
        # Split content into lines
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that are mostly hashtags
            words = line.split()
            hashtag_count = sum(1 for word in words if word.startswith('#'))
            mention_count = sum(1 for word in words if word.startswith('@'))
            url_count = sum(1 for word in words if word.startswith('http'))
            
            # If more than 50% of words are hashtags/mentions/URLs, skip this line
            if len(words) > 0 and (hashtag_count + mention_count + url_count) / len(words) > 0.5:
                continue
                
            # Remove hashtags, mentions, and URLs from the line
            cleaned_words = []
            for word in words:
                if not (word.startswith('#') or word.startswith('@') or word.startswith('http')):
                    cleaned_words.append(word)
            
            # Only keep lines with actual content (at least 2 words after cleaning)
            if len(cleaned_words) >= 2:
                cleaned_lines.append(' '.join(cleaned_words))
        
        return ' '.join(cleaned_lines)

    def extract_videos_with_metrics(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract videos with their engagement metrics, filtering for content with at least 5 words and excluding Twitter and TikTok"""
        videos_with_metrics = []
        
        for post in posts:
            if 'videos' in post and post['videos']:
                # Skip Twitter and TikTok networks
                social_network = post.get('social_network', '').lower()
                if 'twitter' in social_network or 'x.com' in social_network or 'tiktok' in social_network:
                    continue
                
                # Get and clean the content to only include author content
                raw_content = post.get('content', '') or post.get('text', '') or post.get('caption', '')
                content = self.clean_author_content(raw_content)
                content_words = len(content.split()) if content else 0
                
                if content_words < 5:
                    continue  # Skip videos with less than 5 words in author content
                
                for video in post['videos']:
                    # Calculate engagement score (likes + views + plays)
                    likes = video.get('likes_count', 0) or 0
                    views = post.get('views', 0) or 0
                    plays = post.get('plays', 0) or 0
                    comments = post.get('comments_count', 0) or 0
                    shares = post.get('shares', 0) or 0
                    
                    # Weighted engagement score
                    engagement_score = likes * 1.0 + views * 0.5 + plays * 0.5 + comments * 2.0 + shares * 1.5
                    
                    video_data = {
                        'url': video['url'],
                        'likes_count': likes,
                        'views': views,
                        'plays': plays,
                        'comments_count': comments,
                        'shares': shares,
                        'engagement_score': engagement_score,
                        'post_time': post.get('post_time', ''),
                        'content': content,
                        'content_words': content_words,
                        'social_network': post.get('social_network', ''),
                        'source_file': post.get('_source_file', ''),
                        'post_index': posts.index(post),
                        'post_data': post  # Store the actual post data for reference
                    }
                    videos_with_metrics.append(video_data)
        
        return videos_with_metrics
    
    def select_all_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select all available videos, sorted by engagement score"""
        # Sort all videos by engagement score
        sorted_videos = sorted(videos, key=lambda x: x['engagement_score'], reverse=True)
        
        # Group by network for display
        videos_by_network = {}
        for video in sorted_videos:
            network = video['social_network']
            if network not in videos_by_network:
                videos_by_network[network] = []
            videos_by_network[network].append(video)
        
        # Display summary by network
        for network, network_videos in videos_by_network.items():
            print(f"Processing {network}: {len(network_videos)} videos available")
        
        print(f"Selected all {len(sorted_videos)} videos for processing")
        return sorted_videos
    
    def select_top_videos_per_network(self, videos: List[Dict[str, Any]], top_n_per_network: int = 2) -> List[Dict[str, Any]]:
        """Select top N videos per social network by engagement score"""
        # Group videos by social network
        videos_by_network = {}
        for video in videos:
            network = video['social_network']
            if network not in videos_by_network:
                videos_by_network[network] = []
            videos_by_network[network].append(video)
        
        selected_videos = []
        
        # Select top N videos from each network
        for network, network_videos in videos_by_network.items():
            print(f"Processing {network}: {len(network_videos)} videos available")
            
            # Sort by engagement score
            sorted_network_videos = sorted(network_videos, key=lambda x: x['engagement_score'], reverse=True)
            
            # Select top N videos from this network
            top_videos_from_network = sorted_network_videos[:top_n_per_network]
            selected_videos.extend(top_videos_from_network)
            
            print(f"Selected {len(top_videos_from_network)} videos from {network}")
        
        return selected_videos
    
    def download_video(self, video_url: str, filename: str) -> Optional[str]:
        """Download video using yt-dlp with multiple format attempts"""
        try:
            output_path = self.download_dir / f"{filename}.%(ext)s"
            
            # Try different format options for different platforms
            format_options = [
                'best[height<=720][ext=mp4]',  # Best MP4 up to 720p
                'best[ext=mp4]',               # Best MP4 available
                'best[height<=480][ext=mp4]',  # Lower quality MP4
                'worst[ext=mp4]',              # Worst MP4 (often more accessible)
                'best[ext=webm]',              # WebM format
                'best',                        # Any best format
            ]
            
            for format_option in format_options:
                cmd = [
                    'yt-dlp',
                    '--output', str(output_path),
                    '--format', format_option,
                    '--no-playlist',
                    '--no-check-certificate',  # Sometimes helps with SSL issues
                    '--quiet',  # Suppress most output
                    '--no-warnings',  # Suppress warnings
                    video_url
                ]
                
                print(f"Downloading {video_url} with format: {format_option}...")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Find the downloaded file
                    for file in self.download_dir.glob(f"{filename}.*"):
                        if file.suffix in ['.mp4', '.webm', '.mkv', '.avi', '.mov']:
                            print(f"Downloaded: {file}")
                            return str(file)
                else:
                    print(f"Format {format_option} failed: {result.stderr[:100]}...")
                    continue
            
            # If all formats failed, try without format specification
            cmd = [
                'yt-dlp',
                '--output', str(output_path),
                '--no-playlist',
                '--no-check-certificate',
                '--quiet',
                '--no-warnings',
                video_url
            ]
            
            print(f"Trying download without format specification...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                for file in self.download_dir.glob(f"{filename}.*"):
                    if file.suffix in ['.mp4', '.webm', '.mkv', '.avi', '.mov']:
                        print(f"Downloaded: {file}")
                        return str(file)
            
            print(f"All download attempts failed for {video_url}")
            return None
                
        except subprocess.TimeoutExpired:
            print(f"Download timeout for {video_url}")
            return None
        except Exception as e:
            print(f"Error downloading {video_url}: {e}")
            return None
    
    def convert_audio_for_whisper(self, video_path: str) -> Optional[str]:
        """Convert video audio to a format compatible with OpenAI Whisper"""
        try:
            # Create a temporary audio file
            temp_audio_path = video_path.replace('.mp4', '_audio.wav')
            
            print(f"Converting audio for Whisper compatibility...")
            
            # Use ffmpeg to extract and convert audio to WAV format
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian
                '-ar', '16000',  # 16kHz sample rate (Whisper's preferred)
                '-ac', '1',  # Mono channel
                '-y',  # Overwrite output file
                temp_audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"   ✓ Audio converted successfully: {temp_audio_path}")
                return temp_audio_path
            else:
                print(f"   ✗ Audio conversion failed: {result.stderr[:100]}...")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"   ✗ Audio conversion timeout")
            return None
        except Exception as e:
            print(f"   ✗ Audio conversion error: {e}")
            return None
    
    def extract_audio_for_facebook(self, video_path: str) -> Optional[str]:
        """Extract audio from Facebook video using multiple ffmpeg approaches"""
        try:
            # Create a temporary audio file
            temp_audio_path = video_path.replace('.mp4', '_facebook_audio.wav')
            
            print(f"Extracting audio from Facebook video...")
            
            # First, let's check what's in the video file
            print(f"   Checking video file info...")
            info_cmd = ['ffmpeg', '-i', video_path, '-f', 'null', '-']
            info_result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
            if info_result.stderr:
                print(f"   Video info: {info_result.stderr[:300]}...")
            
            # Try multiple ffmpeg approaches for Facebook videos
            approaches = [
                # Approach 1: Simple extraction without re-encoding
                [
                    'ffmpeg', '-i', video_path,
                    '-vn', '-acodec', 'copy',
                    '-y', temp_audio_path.replace('.wav', '.m4a')
                ],
                # Approach 2: Basic WAV conversion
                [
                    'ffmpeg', '-i', video_path,
                    '-vn', '-f', 'wav',
                    '-y', temp_audio_path
                ],
                # Approach 3: Standard extraction with specific codec
                [
                    'ffmpeg', '-i', video_path,
                    '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
                    '-y', temp_audio_path
                ],
                # Approach 4: Force audio stream selection
                [
                    'ffmpeg', '-i', video_path,
                    '-map', '0:a:0', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
                    '-y', temp_audio_path
                ],
                # Approach 5: AAC format
                [
                    'ffmpeg', '-i', video_path,
                    '-vn', '-acodec', 'aac', '-ar', '16000', '-ac', '1',
                    '-y', temp_audio_path.replace('.wav', '.aac')
                ]
            ]
            
            for i, cmd in enumerate(approaches, 1):
                print(f"   Trying approach {i}...")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # Check if file was created and has content
                    output_file = cmd[-1]
                    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                        print(f"   ✓ Audio extracted successfully with approach {i}: {output_file}")
                        return output_file
                    else:
                        print(f"   ⚠ Approach {i} succeeded but no audio file created")
                        continue
                else:
                    print(f"   ✗ Approach {i} failed: {result.stderr[:200]}...")
                    continue
            
            print(f"   ✗ All audio extraction approaches failed")
            return None
                
        except subprocess.TimeoutExpired:
            print(f"   ✗ Audio extraction timeout")
            return None
        except Exception as e:
            print(f"   ✗ Audio extraction error: {e}")
            return None
    
    def transcribe_video(self, video_path: str, video_data: Dict[str, Any] = None) -> Optional[str]:
        """Transcribe video using OpenAI Whisper with platform-specific audio extraction"""
        try:
            print(f"Transcribing {video_path}...")
            
            # Determine if this is a Facebook video
            is_facebook = False
            if video_data and video_data.get('social_network') == 'facebook':
                is_facebook = True
            elif 'facebook' in video_path.lower():
                is_facebook = True
            
            # First try direct transcription
            try:
                with open(video_path, 'rb') as video_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=video_file,
                        response_format="text"
                    )
                print(f"   ✓ Direct transcription successful")
                return transcript
            except Exception as direct_error:
                print(f"   ⚠ Direct transcription failed: {str(direct_error)[:100]}...")
                
                # Choose audio extraction method based on platform
                if is_facebook:
                    print(f"   🔄 Attempting Facebook-specific audio extraction...")
                    audio_path = self.extract_audio_for_facebook(video_path)
                else:
                    print(f"   🔄 Attempting standard audio conversion...")
                    audio_path = self.convert_audio_for_whisper(video_path)
                
                if audio_path:
                    try:
                        with open(audio_path, 'rb') as audio_file:
                            transcript = self.openai_client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                response_format="text"
                            )
                        print(f"   ✓ Transcription successful after audio extraction")
                        
                        # Clean up temporary audio file
                        try:
                            os.remove(audio_path)
                            print(f"   ✓ Cleaned up temporary audio file")
                        except:
                            pass
                        
                        return transcript
                    except Exception as conversion_error:
                        print(f"   ✗ Transcription failed even after audio extraction: {conversion_error}")
                        # Clean up temporary audio file
                        try:
                            os.remove(audio_path)
                        except:
                            pass
                        return None
                else:
                    print(f"   ✗ Audio extraction failed, cannot transcribe")
                    return None
            
        except Exception as e:
            print(f"Error transcribing {video_path}: {e}")
            return None
    
    def save_transcription_file(self, video_path: str, transcription: str, video_data: Dict[str, Any]) -> Optional[str]:
        """Save transcription to a text file alongside the video file"""
        try:
            # Create transcription filename based on video filename
            video_file = Path(video_path)
            transcription_file = video_file.with_suffix('.txt')
            
            # Prepare transcription content with metadata
            content = f"""TRANSCRIPTION FILE
==================

Video URL: {video_data['url']}
Network: {video_data['social_network']}
Engagement Score: {video_data['engagement_score']:.1f}
Likes: {video_data['likes_count']}
Views: {video_data['views']}
Content Words: {video_data['content_words']}
Source File: {video_data['source_file']}
Transcription Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

Original Content:
{video_data['content']}

TRANSCRIPTION:
==============
{transcription}

Word Count: {len(transcription.split())}
Character Count: {len(transcription)}
"""
            
            # Write transcription to file
            with open(transcription_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return str(transcription_file)
            
        except Exception as e:
            print(f"   ⚠ Warning: Could not save transcription file: {e}")
            return None
    
    def update_json_with_transcription(self, video_data: Dict[str, Any], transcription: str):
        """Update the original JSON file with transcription data"""
        try:
            source_file = self.data_dir / video_data['source_file']
            
            # Load the JSON file
            with open(source_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if 'posts' in data:
                posts = data['posts']
            elif 'videos' in data:
                # For TikTok, we need to find the video in the videos array
                posts = data['videos']
            else:
                posts = data if isinstance(data, list) else [data]
            
            # Find the specific post and video by URL (more reliable than index)
            video_url = video_data['url']
            found = False
            
            for post in posts:
                # Handle Facebook structure - videos are in media array with __typename: "Video"
                if 'media' in post and isinstance(post['media'], list):
                    for media_item in post['media']:
                        if media_item.get('__typename') == 'Video' and 'url' in media_item:
                            if media_item['url'] == video_url:
                                media_item['transcription'] = transcription
                                media_item['transcription_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                                found = True
                                print(f"Found and updated Facebook video: {video_url}")
                                break
                    if found:
                        break
                
                # Handle Instagram/TikTok structure - videos are in videos array
                elif 'videos' in post:
                    for video in post['videos']:
                        if video['url'] == video_url:
                            video['transcription'] = transcription
                            video['transcription_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            found = True
                            print(f"Found and updated video: {video_url}")
                            break
                    if found:
                        break
            
            if not found:
                print(f"Warning: Could not find video {video_url} in {source_file}")
                return
            
            # Save back to file
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Updated {source_file} with transcription")
            
        except Exception as e:
            print(f"Error updating JSON file: {e}")
    
    def move_failed_video_to_bed_videos(self, video_data: Dict[str, Any]):
        """Move failed video download to bed_videos array in the same post"""
        try:
            source_file = self.data_dir / video_data['source_file']
            
            # Load the JSON file
            with open(source_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if 'posts' in data:
                posts = data['posts']
            elif 'videos' in data:
                # For TikTok, we need to find the video in the videos array
                posts = data['videos']
            else:
                posts = data if isinstance(data, list) else [data]
            
            # Find the specific post and video by URL
            video_url = video_data['url']
            found = False
            
            for post in posts:
                if 'videos' in post:
                    for video in post['videos']:
                        if video['url'] == video_url:
                            # Create bed video entry from video data
                            bed_video = {
                                'url': video_url,
                                'cover_url': video.get('cover_url', ''),
                                'likes_count': video.get('likes_count', 0),
                                'duration': video.get('duration', 0),
                                'moved_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'reason': 'video_download_failed'
                            }
                            
                            # Ensure bed_videos array exists
                            if 'bed_videos' not in post:
                                post['bed_videos'] = []
                            
                            # Add to bed_videos array
                            post['bed_videos'].append(bed_video)
                            
                            # Remove from videos array
                            post['videos'].remove(video)
                            
                            found = True
                            print(f"Moved failed video to bed_videos: {video_url}")
                            break
                    if found:
                        break
            
            if not found:
                print(f"Warning: Could not find video {video_url} in {source_file}")
                return
            
            # Save back to file
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Updated {source_file} - moved failed video to bed_videos")
            
        except Exception as e:
            print(f"Error moving video to bed_videos: {e}")
    
    def clean_download_directory(self):
        """Clean the download directory before starting processing"""
        print("Cleaning download directory...")
        try:
            # Remove all files in downloads directory
            for file_path in self.download_dir.glob('*'):
                if file_path.is_file():
                    file_path.unlink()
                    print(f"   ✓ Removed: {file_path.name}")
            
            print(f"   ✓ Download directory cleaned successfully")
        except Exception as e:
            print(f"   ⚠ Warning: Could not clean download directory: {e}")
    
    def process_videos(self, filter_tivoneat: bool = True):
        """Main processing function - processes each data file separately, top 5 videos per network"""
        print("=" * 80)
        print("VIDEO DOWNLOADER - PROCESSING EACH DATA FILE SEPARATELY")
        print("=" * 80)
        
        # Clean download directory before starting
        self.clean_download_directory()
        print()
        
        # Get all JSON files in data directory
        json_files = list(self.data_dir.glob('*.json'))
        
        # Filter for tivoneat files if requested
        if filter_tivoneat:
            json_files = [f for f in json_files if 'tivoneat' in f.name]
        
        # Skip Twitter/X related files
        json_files = [f for f in json_files if 'twitter' not in f.name.lower() and 'x.com' not in f.name.lower()]
        
        print(f"Found {len(json_files)} data files to process:")
        for file in json_files:
            print(f"  - {file.name}")
        print()
        
        total_processed = 0
        total_successful = 0
        total_failed = 0
        
        # Process each file separately
        for file_idx, json_file in enumerate(json_files, 1):
            print(f"\n{'='*60}")
            print(f"PROCESSING FILE {file_idx}/{len(json_files)}: {json_file.name}")
            print(f"{'='*60}")
            
            # Load and process this specific file
            file_results = self.process_single_file(json_file)
            
            total_processed += file_results['total_videos']
            total_successful += file_results['successful_transcriptions']
            total_failed += file_results['failed_downloads'] + file_results['failed_transcriptions']
            
            print(f"\nFILE {file_idx} SUMMARY:")
            print(f"  Total videos processed: {file_results['total_videos']}")
            print(f"  Successful transcriptions: {file_results['successful_transcriptions']}")
            print(f"  Failed downloads: {file_results['failed_downloads']}")
            print(f"  Failed transcriptions: {file_results['failed_transcriptions']}")
        
        print(f"\n{'='*80}")
        print("OVERALL SUMMARY")
        print(f"{'='*80}")
        print(f"Files processed: {len(json_files)}")
        print(f"Total videos processed: {total_processed}")
        print(f"Successful transcriptions: {total_successful}")
        print(f"Failed processing: {total_failed}")
        print(f"Success rate: {(total_successful/total_processed*100):.1f}%" if total_processed > 0 else "N/A")
        print(f"{'='*80}")
    
    def process_single_file(self, json_file: Path) -> Dict[str, int]:
        """Process a single JSON file - select top 5 videos per network and process them"""
        print(f"Loading data from {json_file.name}...")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"ERROR: Failed to load {json_file.name}: {e}")
            return {'total_videos': 0, 'successful_transcriptions': 0, 'failed_downloads': 0, 'failed_transcriptions': 0}
        
        # Parse the data structure
        posts = self.parse_data_structure(data, json_file.name)
        
        # Extract videos with metrics (filtering for content with at least 5 words)
        print("Extracting videos with metrics (filtering for content with at least 5 words)...")
        videos = self.extract_videos_with_metrics(posts)
        print(f"Found {len(videos)} videos total (with at least 5 words in content)")
        
        # Filter out videos that already have transcriptions
        print("Filtering out videos that already have transcriptions...")
        available_videos = [v for v in videos if not self.has_transcription(v)]
        print(f"Available videos for processing: {len(available_videos)} (excluding already transcribed)")
        
        # Select top 5 videos per network
        print("Selecting top 5 videos per network...")
        selected_videos = self.select_top_videos_per_network(available_videos, 5)
        print(f"Selected {len(selected_videos)} videos for processing")
        
        # Display selected videos by network
        self.display_selected_videos(selected_videos)
        
        # Process each video
        return self.process_selected_videos(selected_videos, json_file)
    
    def parse_data_structure(self, data: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """Parse different JSON data structures and return standardized posts"""
        posts = []
        
        if 'posts' in data:
            # Facebook/Instagram structure
            posts = data['posts']
            for post in posts:
                if post.get('type') == 'Video' and 'videoUrl' in post:
                    # Create videos array for Instagram video posts
                    post['videos'] = [{
                        'url': post['videoUrl'],
                        'likes_count': post.get('likesCount', 0),
                        'cover_url': post.get('displayUrl', ''),
                        'duration': 0
                    }]
                    post['social_network'] = 'instagram'
                elif post.get('isVideo') and 'media' in post:
                    # Handle Facebook video posts
                    videos = []
                    for media_item in post['media']:
                        if media_item.get('__typename') == 'Video' and 'url' in media_item:
                            videos.append({
                                'url': media_item['url'],
                                'likes_count': post.get('likes', 0),
                                'cover_url': media_item.get('thumbnail', ''),
                                'duration': media_item.get('playable_duration_in_ms', 0) / 1000
                            })
                    if videos:
                        post['videos'] = videos
                        post['social_network'] = 'facebook'
                        post['views'] = post.get('viewsCount', 0)
                        post['comments_count'] = post.get('comments', 0)
                        post['shares'] = post.get('shares', 0)
        elif 'videos' in data:
            # TikTok structure - convert videos to posts format
            for video in data['videos']:
                post = {
                    'id': video.get('id', ''),
                    'content': video.get('text', ''),
                    'post_time': video.get('createTimeISO', ''),
                    'social_network': 'tiktok',
                    'likes': video.get('diggCount', 0),
                    'views': video.get('playCount', 0),
                    'comments_count': video.get('commentCount', 0),
                    'shares': video.get('shareCount', 0),
                    'videos': [{
                        'url': video.get('webVideoUrl', ''),
                        'likes_count': video.get('diggCount', 0),
                        'cover_url': video.get('videoMeta', {}).get('coverUrl', ''),
                        'duration': video.get('videoMeta', {}).get('duration', 0)
                    }],
                    'bed_videos': []
                }
                posts.append(post)
        else:
            # Assume it's a list of posts
            posts = data if isinstance(data, list) else [data]
        
        # Add source file info to each post
        for post in posts:
            post['_source_file'] = filename
            if 'bed_videos' not in post:
                post['bed_videos'] = []
        
        return posts
    
    def has_transcription(self, video_data: Dict[str, Any]) -> bool:
        """Check if a video already has a transcription"""
        try:
            source_file = self.data_dir / video_data['source_file']
            with open(source_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if 'posts' in data:
                posts = data['posts']
            elif 'videos' in data:
                posts = data['videos']
            else:
                posts = data if isinstance(data, list) else [data]
            
            # Find the specific video by URL
            video_url = video_data['url']
            for post in posts:
                # Handle Facebook structure - videos are in media array with __typename: "Video"
                if 'media' in post and isinstance(post['media'], list):
                    for media_item in post['media']:
                        if media_item.get('__typename') == 'Video' and 'url' in media_item:
                            if media_item['url'] == video_url and 'transcription' in media_item:
                                return True
                
                # Handle Instagram/TikTok structure - videos are in videos array
                elif 'videos' in post:
                    for video in post['videos']:
                        if video['url'] == video_url and 'transcription' in video:
                            return True
            return False
        except Exception as e:
            print(f"Error checking transcription for {video_data['url']}: {e}")
            return False
    
    def display_selected_videos(self, selected_videos: List[Dict[str, Any]]):
        """Display selected videos grouped by network"""
        videos_by_network = {}
        for video in selected_videos:
            network = video['social_network']
            if network not in videos_by_network:
                videos_by_network[network] = []
            videos_by_network[network].append(video)
        
        for network, network_videos in videos_by_network.items():
            print(f"\n{network.upper()} ({len(network_videos)} videos):")
            for i, video in enumerate(network_videos, 1):
                print(f"  {i}. {video['url']} (Score: {video['engagement_score']:.1f}, Likes: {video['likes_count']}, Views: {video['views']}, Words: {video['content_words']})")
                print(f"      Content: {video['content'][:100]}...")
    
    def process_selected_videos(self, selected_videos: List[Dict[str, Any]], json_file: Path) -> Dict[str, int]:
        """Process the selected videos - download, transcribe, and update JSON"""
        successful_transcriptions = 0
        failed_downloads = 0
        failed_transcriptions = 0
        
        # Track video numbers per network for naming
        network_video_counts = {}
        
        for i, video_data in enumerate(selected_videos, 1):
            print(f"\n--- Processing video {i}/{len(selected_videos)} ---")
            print(f"Source: {video_data['source_file']}")
            print(f"URL: {video_data['url']}")
            print(f"Network: {video_data['social_network']}")
            print(f"Engagement Score: {video_data['engagement_score']:.1f}")
            print(f"Content: {video_data['content'][:100]}...")
            
            # Generate filename
            source_file = video_data['source_file'].replace('.json', '')
            network = video_data['social_network']
            
            if network not in network_video_counts:
                network_video_counts[network] = 0
            network_video_counts[network] += 1
            
            filename = f"{source_file}_{network}_{network_video_counts[network]}"
            
            # Download video
            print(f"1. Downloading video...")
            video_path = self.download_video(video_data['url'], filename)
            
            if video_path:
                print(f"   ✓ Successfully downloaded: {video_path}")
                
                # Transcribe video
                print(f"2. Transcribing video...")
                transcription = self.transcribe_video(video_path, video_data)
                
                if transcription:
                    transcription_words = len(transcription.split())
                    print(f"   ✓ Transcription completed ({transcription_words} words)")
                    
                    if transcription_words > 20:
                        # Valid transcription - update JSON
                        print(f"3. Updating JSON file...")
                        self.update_json_with_transcription(video_data, transcription)
                        print(f"   ✓ JSON file updated with transcription")
                        
                        # Save transcription to file
                        print(f"4. Saving transcription file...")
                        transcription_file = self.save_transcription_file(video_path, transcription, video_data)
                        if transcription_file:
                            print(f"   ✓ Transcription saved: {transcription_file}")
                        
                        # Keep video file
                        print(f"5. Keeping video file...")
                        print(f"   ✓ Kept: {video_path}")
                        
                        successful_transcriptions += 1
                        print(f"✓ Successfully processed video {i}")
                        
                    else:
                        print(f"   ✗ Invalid transcription (only {transcription_words} words, need >20)")
                        failed_transcriptions += 1
                        self.move_failed_video_to_bed_videos(video_data)
                        # Keep video file even if transcription failed
                        print(f"   ✓ Kept failed video: {video_path}")
                else:
                    print(f"   ✗ Transcription failed")
                    failed_transcriptions += 1
                    self.move_failed_video_to_bed_videos(video_data)
                    # Keep video file even if transcription failed
                    print(f"   ✓ Kept failed video: {video_path}")
            else:
                print(f"   ✗ Download failed")
                failed_downloads += 1
                self.move_failed_video_to_bed_videos(video_data)
        
        return {
            'total_videos': len(selected_videos),
            'successful_transcriptions': successful_transcriptions,
            'failed_downloads': failed_downloads,
            'failed_transcriptions': failed_transcriptions
        }

def full_data_transcription():
    """Full transcription script for all videos in data folder - selects top 10 most liked videos"""
    downloader = VideoDownloader()
    
    print("=" * 80)
    print("FULL DATA FOLDER TRANSCRIPTION")
    print("=" * 80)
    print("Processing all videos from data folder...")
    print("Selecting top 10 most liked videos for transcription")
    print()
    
    # Load video data from all JSON files
    posts = downloader.load_json_files()
    videos = downloader.extract_videos_with_metrics(posts)
    
    print(f"Found {len(videos)} total videos across all data files")
    print()
    
    # Check which videos already have transcriptions
    already_transcribed = set()
    for json_file in downloader.data_dir.glob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for post in data:
            if 'videos' in post:
                for video in post['videos']:
                    if 'transcription' in video:
                        already_transcribed.add(video['url'])
    
    print(f"Videos already transcribed: {len(already_transcribed)}")
    
    # Filter out already transcribed videos and sort by likes
    available_videos = [v for v in videos if v['url'] not in already_transcribed]
    available_videos.sort(key=lambda x: x['likes_count'], reverse=True)
    
    print(f"Available videos for transcription: {len(available_videos)}")
    print()
    
    # Select top 10 most liked videos that don't have transcriptions
    top_10_videos = available_videos[:10]
    
    print("TOP 10 MOST LIKED VIDEOS (WITHOUT TRANSCRIPTIONS) SELECTED:")
    print("-" * 60)
    for i, video in enumerate(top_10_videos, 1):
        print(f"{i:2d}. {video['url']}")
        print(f"    Likes: {video['likes_count']:,} | Views: {video['views']:,} | Score: {video['engagement_score']:,.1f}")
        print(f"    Source: {video['source_file']} | Network: {video['social_network']}")
        print()
    
    # Process each video
    successful_transcriptions = 0
    failed_downloads = 0
    failed_transcriptions = 0
    transcription_results = []
    
    for i, video_data in enumerate(top_10_videos, 1):
        print(f"PROCESSING VIDEO {i}/10:")
        print("=" * 60)
        print(f"URL: {video_data['url']}")
        print(f"Likes: {video_data['likes_count']:,} | Views: {video_data['views']:,}")
        print(f"Engagement Score: {video_data['engagement_score']:,.1f}")
        print(f"Source: {video_data['source_file']} | Network: {video_data['social_network']}")
        print()
        
        # Generate filename
        filename = f"top10_video_{i}_{int(time.time())}"
        
        # Download video
        print("1. Downloading video...")
        video_path = downloader.download_video(video_data['url'], filename)
        
        if video_path:
            print(f"   ✓ Successfully downloaded: {video_path}")
            
            # Transcribe video
            print("2. Transcribing video...")
            transcription = downloader.transcribe_video(video_path, video_data)
            
            if transcription:
                print("   ✓ Transcription completed!")
                print(f"   Transcription preview: '{transcription.strip()[:100]}...'")
                
                # Update JSON
                print("3. Updating JSON file...")
                downloader.update_json_with_transcription(video_data, transcription)
                print("   ✓ JSON file updated!")
                
                # Save transcription to file
                print("4. Saving transcription file...")
                transcription_file = downloader.save_transcription_file(video_path, transcription, video_data)
                if transcription_file:
                    print(f"   ✓ Transcription saved: {transcription_file}")
                
                # Keep video file
                print("5. Keeping video file...")
                print(f"   ✓ Kept: {video_path}")
                
                # Store results
                transcription_results.append({
                    'url': video_data['url'],
                    'transcription': transcription.strip(),
                    'likes': video_data['likes_count'],
                    'views': video_data['views'],
                    'engagement_score': video_data['engagement_score'],
                    'source_file': video_data['source_file'],
                    'social_network': video_data['social_network'],
                    'word_count': len(transcription.strip().split()),
                    'char_count': len(transcription.strip()),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
                
                successful_transcriptions += 1
                
            else:
                print("   ✗ Transcription failed!")
                failed_transcriptions += 1
                # Keep video file even if transcription failed
                print(f"   ✓ Kept failed video: {video_path}")
        else:
            print("   ✗ Download failed!")
            failed_downloads += 1
        
        print("-" * 60)
        print()
    
    # Create comprehensive results file
    print("CREATING RESULTS FILES...")
    print("-" * 40)
    
    # Create detailed results file
    results_content = f"""# Full Data Transcription Results
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
# Total videos processed: 10
# Successful transcriptions: {successful_transcriptions}
# Failed downloads: {failed_downloads}
# Failed transcriptions: {failed_transcriptions}

## Summary Statistics:
- Total videos in dataset: {len(videos)}
- Already transcribed: {len(already_transcribed)}
- Available for processing: {len(available_videos)}
- Successfully processed: {successful_transcriptions}

## Transcription Results:

"""
    
    for i, result in enumerate(transcription_results, 1):
        results_content += f"""### Video {i}: {result['social_network'].upper()}
- **URL**: {result['url']}
- **Likes**: {result['likes']:,}
- **Views**: {result['views']:,}
- **Engagement Score**: {result['engagement_score']:,.1f}
- **Source File**: {result['source_file']}
- **Word Count**: {result['word_count']}
- **Character Count**: {result['char_count']}
- **Timestamp**: {result['timestamp']}

**Transcription:**
{result['transcription']}

---

"""
    
    # Save results file
    results_file = "full_transcription_results.txt"
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(results_content)
    
    print(f"✓ Detailed results saved to: {results_file}")
    
    # Create HTML results file
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Full Transcription Results</title>
    <style>
        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            margin: 40px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .video-result {{
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #f9f9f9;
        }}
        .transcription {{
            font-size: 16px;
            line-height: 1.8;
            margin: 15px 0;
            padding: 15px;
            background-color: white;
            border-left: 4px solid #007acc;
        }}
        .metadata {{
            font-size: 14px;
            color: #666;
            margin: 10px 0;
        }}
        .stats {{
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Full Data Transcription Results</h1>
            <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <h3>Summary Statistics:</h3>
            <ul>
                <li>Total videos in dataset: {len(videos):,}</li>
                <li>Already transcribed: {len(already_transcribed):,}</li>
                <li>Available for processing: {len(available_videos):,}</li>
                <li>Successfully processed: {successful_transcriptions}</li>
                <li>Failed downloads: {failed_downloads}</li>
                <li>Failed transcriptions: {failed_transcriptions}</li>
            </ul>
        </div>
"""
    
    for i, result in enumerate(transcription_results, 1):
        html_content += f"""
        <div class="video-result">
            <h3>Video {i}: {result['social_network'].upper()}</h3>
            <div class="metadata">
                <p><strong>URL:</strong> <a href="{result['url']}" target="_blank">{result['url']}</a></p>
                <p><strong>Likes:</strong> {result['likes']:,} | <strong>Views:</strong> {result['views']:,} | <strong>Engagement Score:</strong> {result['engagement_score']:,.1f}</p>
                <p><strong>Source:</strong> {result['source_file']} | <strong>Words:</strong> {result['word_count']} | <strong>Characters:</strong> {result['char_count']}</p>
                <p><strong>Timestamp:</strong> {result['timestamp']}</p>
            </div>
            <div class="transcription">
                {result['transcription']}
            </div>
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>"""
    
    html_file = "full_transcription_results.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ HTML results saved to: {html_file}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("TRANSCRIPTION SUMMARY")
    print("=" * 80)
    print(f"Total videos in dataset: {len(videos):,}")
    print(f"Already transcribed: {len(already_transcribed):,}")
    print(f"Available for processing: {len(available_videos):,}")
    print(f"Successfully transcribed: {successful_transcriptions}")
    print(f"Failed downloads: {failed_downloads}")
    print(f"Failed transcriptions: {failed_transcriptions}")
    print()
    print("Files created:")
    print(f"1. {results_file} - Detailed text results")
    print(f"2. {html_file} - HTML results with formatting")
    print("=" * 80)

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        # Run full data transcription
        full_data_transcription()
    else:
        # Run regular video processing - processes ALL files in data folder
        downloader = VideoDownloader()
        downloader.process_videos(filter_tivoneat=False)

if __name__ == "__main__":
    main()
