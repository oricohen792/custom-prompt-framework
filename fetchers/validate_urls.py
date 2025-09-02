#!/usr/bin/env python3
"""
URL Validation Script
Runs separately from universal merger to validate URLs in data files
"""

import os
import json
import argparse
import requests
from typing import Dict, List, Tuple

class URLValidator:
    def __init__(self, image_timeout: int = 5, video_timeout: int = 3):
        self.image_timeout = image_timeout
        self.video_timeout = video_timeout
        self.validation_stats = {
            'images_tested': 0,
            'images_valid': 0,
            'images_invalid': 0,
            'videos_tested': 0,
            'videos_valid': 0,
            'videos_invalid': 0
        }
    
    def validate_image_url(self, url: str, verbose: bool = False) -> bool:
        """Check if an image URL is accessible and returns a valid image"""
        self.validation_stats['images_tested'] += 1
        
        try:
            # Check for common image file extensions first (most reliable indicator)
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.ico']
            if any(ext in url.lower() for ext in image_extensions):
                # If it has an image extension, just check if URL is accessible
                try:
                    response = requests.head(url, timeout=self.image_timeout, allow_redirects=True)
                    if response.status_code == 200:
                        self.validation_stats['images_valid'] += 1
                        return True
                except:
                    pass
                
                # If HEAD fails, try GET with stream
                try:
                    response = requests.get(url, timeout=self.image_timeout, stream=True)
                    if response.status_code == 200:
                        self.validation_stats['images_valid'] += 1
                        return True
                except:
                    pass
            
            # For URLs without clear image extensions, check content-type
            try:
                response = requests.head(url, timeout=self.image_timeout, allow_redirects=True)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    # Accept image content types
                    if content_type.startswith('image/'):
                        self.validation_stats['images_valid'] += 1
                        return True
            except:
                pass
            
            # Also try GET request for URLs that might not support HEAD
            try:
                response = requests.get(url, timeout=self.image_timeout, stream=True)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if content_type.startswith('image/'):
                        self.validation_stats['images_valid'] += 1
                        return True
            except:
                pass
            
            # For Instagram CDN URLs, be more permissive - they often work even without proper headers
            if 'cdninstagram.com' in url or 'instagram.com' in url:
                try:
                    response = requests.get(url, timeout=self.image_timeout, stream=True)
                    if response.status_code == 200:
                        # Check if response contains image data (JPEG, PNG, etc.)
                        content = response.content[:100]  # Check first 100 bytes
                        if (content.startswith(b'\xff\xd8\xff') or  # JPEG
                            content.startswith(b'\x89PNG') or       # PNG
                            content.startswith(b'GIF8') or          # GIF
                            content.startswith(b'RIFF') or          # WebP
                            b'JFIF' in content or                   # JPEG marker
                            b'PNG' in content):                     # PNG marker
                            self.validation_stats['images_valid'] += 1
                            return True
                except:
                    pass
            
            self.validation_stats['images_invalid'] += 1
            return False
        except Exception:
            self.validation_stats['images_invalid'] += 1
            return False

    def validate_video_url(self, url: str, verbose: bool = False) -> bool:
        """Check if a video URL is accessible and returns a valid video"""
        self.validation_stats['videos_tested'] += 1
        
        try:
            # Skip TikTok URLs that are often temporary or require special headers
            if 'tiktok.com' in url and ('downloadAddr' in url or 'playAddr' in url):
                self.validation_stats['videos_invalid'] += 1
                return False
            
            # Check for common video file extensions first (most reliable indicator)
            video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.3gp', '.ogv']
            if any(ext in url.lower() for ext in video_extensions):
                # If it has a video extension, just check if URL is accessible
                try:
                    response = requests.head(url, timeout=self.video_timeout, allow_redirects=True)
                    if response.status_code == 200:
                        self.validation_stats['videos_valid'] += 1
                        return True
                except:
                    pass
                
                # If HEAD fails, try GET with stream
                try:
                    response = requests.get(url, timeout=self.video_timeout, stream=True)
                    if response.status_code == 200:
                        self.validation_stats['videos_valid'] += 1
                        return True
                except:
                    pass
            
            # For URLs without clear video extensions, be very permissive
            try:
                response = requests.head(url, timeout=self.video_timeout, allow_redirects=True)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    # Accept almost any content type for video URLs
                    if (content_type.startswith('video/') or 
                        content_type.startswith('application/') or
                        content_type.startswith('text/') or  # Some video URLs return text/html
                        'stream' in content_type or
                        'octet' in content_type or
                        len(content_type) == 0):  # Some URLs don't return content-type
                        self.validation_stats['videos_valid'] += 1
                        return True
            except:
                pass
            
            # Also try GET request for URLs that might not support HEAD
            try:
                response = requests.get(url, timeout=self.video_timeout, stream=True)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if (content_type.startswith('video/') or 
                        content_type.startswith('application/') or
                        content_type.startswith('text/') or
                        'stream' in content_type or
                        'octet' in content_type or
                        len(content_type) == 0):
                        self.validation_stats['videos_valid'] += 1
                        return True
            except:
                pass
            
            # If all else fails, but URL looks like a video URL, accept it
            if any(keyword in url.lower() for keyword in ['video', 'mp4', 'stream', 'media']):
                self.validation_stats['videos_valid'] += 1
                return True
            
            self.validation_stats['videos_invalid'] += 1
            return False
        except Exception:
            self.validation_stats['videos_invalid'] += 1
            return False

    def validate_all_images(self, image_urls: List[str], verbose: bool = True) -> Tuple[List[str], List[str]]:
        """Validate all image URLs and return valid and invalid lists"""
        valid_images = []
        invalid_images = []
        
        if verbose:
            print(f"      - Testing ALL {len(image_urls)} images...")
        
        for i, img_url in enumerate(image_urls):
            print(f"        🔍 Testing image {i+1}/{len(image_urls)}: {img_url[:80]}...")
            is_valid = self.validate_image_url(img_url, verbose)
            if is_valid:
                valid_images.append(img_url)
                print(f"        ✅ Valid image {i+1}")
            else:
                invalid_images.append(img_url)
                print(f"        ❌ Invalid image {i+1}")
            
            if verbose and (i + 1) % 10 == 0:  # Progress indicator every 10 URLs
                print(f"        📊 Progress: {i + 1}/{len(image_urls)} images tested, {len(valid_images)} valid so far")
        
        return valid_images, invalid_images

    def validate_all_videos(self, video_urls: List[str], verbose: bool = True) -> Tuple[List[str], List[str]]:
        """Validate all video URLs and return valid and invalid lists"""
        valid_videos = []
        invalid_videos = []
        
        if verbose:
            print(f"      - Testing ALL {len(video_urls)} videos...")
        
        for i, vid_url in enumerate(video_urls):
            print(f"        🎥 Testing video {i+1}/{len(video_urls)}: {vid_url[:80]}...")
            is_valid = self.validate_video_url(vid_url, verbose)
            if is_valid:
                valid_videos.append(vid_url)
                print(f"        ✅ Valid video {i+1}")
            else:
                invalid_videos.append(vid_url)
                print(f"        ❌ Invalid video {i+1}")
            
            if verbose and (i + 1) % 5 == 0:  # Progress indicator every 5 URLs
                print(f"        📊 Progress: {i + 1}/{len(video_urls)} videos tested, {len(valid_videos)} valid so far")
        
        return valid_videos, invalid_videos

    def get_validation_stats(self) -> Dict[str, int]:
        """Get validation statistics"""
        return self.validation_stats.copy()

    def print_validation_summary(self):
        """Print a summary of validation results"""
        stats = self.get_validation_stats()
        print(f"      - Found {stats['images_valid']} valid images, {stats['videos_valid']} valid videos")
        print(f"      - Validation stats: {stats['images_valid']}/{stats['images_tested']} images, {stats['videos_valid']}/{stats['videos_tested']} videos")

    def revalidate_urls(self, posts: List[Dict], verbose: bool = True) -> List[Dict]:
        """Re-validate URLs in posts and move invalid ones to bad arrays"""
        if verbose:
            print(f"      - Re-validating media URLs in {len(posts)} posts...")
        
        updated_posts = []
        total_images = 0
        total_videos = 0
        
        for i, post in enumerate(posts):
            updated_post = post.copy()
            
            # Re-validate images
            current_images = post.get('images', [])
            current_bad_images = post.get('bad_images', [])
            
            valid_images = []
            invalid_images = current_bad_images.copy()  # Keep existing bad images
            
            for img_url in current_images:
                total_images += 1
                print(f"        🔍 Testing image {total_images}: {img_url[:80]}...")
                if self.validate_image_url(img_url, verbose):
                    valid_images.append(img_url)
                    print(f"        ✅ Valid image {total_images}")
                else:
                    invalid_images.append(img_url)
                    print(f"        ❌ Invalid image {total_images}")
                    if verbose:
                        print(f"        ⚠️ Image became invalid: {img_url[:80]}...")
            
            updated_post['images'] = valid_images
            updated_post['bad_images'] = invalid_images
            
            # Re-validate videos
            current_videos = post.get('videos', [])
            current_bad_videos = post.get('bad_videos', [])
            
            valid_videos = []
            invalid_videos = current_bad_videos.copy()  # Keep existing bad videos
            
            for vid_url in current_videos:
                total_videos += 1
                print(f"        🎥 Testing video {total_videos}: {vid_url[:80]}...")
                if self.validate_video_url(vid_url, verbose):
                    valid_videos.append(vid_url)
                    print(f"        ✅ Valid video {total_videos}")
                else:
                    invalid_videos.append(vid_url)
                    print(f"        ❌ Invalid video {total_videos}")
                    if verbose:
                        print(f"        ⚠️ Video became invalid: {vid_url[:80]}...")
            
            updated_post['videos'] = valid_videos
            updated_post['bad_videos'] = invalid_videos
            
            updated_posts.append(updated_post)
            
            # Progress indicator every 10 posts
            if verbose and (i + 1) % 10 == 0:
                print(f"        📊 Progress: {i + 1}/{len(posts)} posts processed, {total_images} images, {total_videos} videos checked")
        
        if verbose:
            print(f"      - Completed: {len(posts)} posts, {total_images} images, {total_videos} videos processed")
        
        return updated_posts

def validate_data_file(data_file: str, verbose: bool = True, move_bad_files: bool = True) -> Dict:
    """Validate all URLs in a data file and move to bad folder if invalid URLs found"""
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"error": f"File not found: {data_file}"}
    except Exception as e:
        return {"error": f"Error loading file: {e}"}
    
    # Handle different data structures
    if isinstance(data, list):
        posts = data
    elif isinstance(data, dict):
        posts = data.get('posts', [])
    else:
        return {"error": "Unknown data structure"}
    
    print(f"🔍 Validating URLs in {data_file}")
    print(f"📊 Total posts: {len(posts)}")
    
    # Create URLValidator instance
    validator = URLValidator()
    
    # Re-validate all URLs in posts
    updated_posts = validator.revalidate_urls(posts, verbose=verbose)
    
    # Print validation summary
    validator.print_validation_summary()
    
    # Check if there are any invalid URLs
    stats = validator.get_validation_stats()
    has_invalid_urls = stats['images_invalid'] > 0 or stats['videos_invalid'] > 0
    
    if has_invalid_urls and move_bad_files:
        # Create bad folder structure
        data_dir = os.path.dirname(data_file)
        bad_dir = os.path.join(data_dir, 'bad')
        os.makedirs(bad_dir, exist_ok=True)
        
        # Move file to bad folder
        filename = os.path.basename(data_file)
        bad_file_path = os.path.join(bad_dir, filename)
        
        try:
            # Save updated data to bad folder
            with open(bad_file_path, 'w', encoding='utf-8') as f:
                json.dump(updated_posts, f, indent=2, ensure_ascii=False)
            print(f"⚠️  File moved to bad folder: {bad_file_path}")
            print(f"   Reason: Found {stats['images_invalid']} invalid images and {stats['videos_invalid']} invalid videos")
        except Exception as e:
            return {"error": f"Error saving file to bad folder: {e}"}
    else:
        # Save updated data in original location
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(updated_posts, f, indent=2, ensure_ascii=False)
            print(f"💾 Updated data saved to: {data_file}")
        except Exception as e:
            return {"error": f"Error saving file: {e}"}
    
    return {
        "total_posts": len(posts),
        "validation_stats": validator.get_validation_stats(),
        "moved_to_bad": has_invalid_urls and move_bad_files,
        "bad_file_path": os.path.join(os.path.dirname(data_file), 'bad', os.path.basename(data_file)) if has_invalid_urls and move_bad_files else None
    }

def validate_all_data_files(data_dir: str = "data", verbose: bool = True, move_bad_files: bool = True) -> Dict:
    """Validate URLs in all JSON files in the data directory and move bad files to bad folder"""
    if not os.path.exists(data_dir):
        return {"error": f"Directory not found: {data_dir}"}
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    if not json_files:
        return {"error": "No JSON files found in data directory"}
    
    print(f"🔍 Validating URLs in {len(json_files)} data files...")
    print("=" * 60)
    
    results = {}
    total_stats = {
        'images_tested': 0,
        'images_valid': 0,
        'images_invalid': 0,
        'videos_tested': 0,
        'videos_valid': 0,
        'videos_invalid': 0
    }
    
    files_moved_to_bad = 0
    
    for filename in json_files:
        file_path = os.path.join(data_dir, filename)
        print(f"\n📁 Processing: {filename}")
        print("-" * 40)
        
        result = validate_data_file(file_path, verbose=verbose, move_bad_files=move_bad_files)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            results[filename] = result
        else:
            if result.get('moved_to_bad', False):
                print(f"⚠️  File moved to bad folder: {filename}")
                files_moved_to_bad += 1
            else:
                print(f"✅ Successfully validated {filename}")
                results[filename] = result
                
                # Aggregate stats
                stats = result.get('validation_stats', {})
                for key in total_stats:
                    total_stats[key] += stats.get(key, 0)
    
    print("\n" + "=" * 60)
    print("📋 Overall Validation Summary:")
    print(f"📊 Files processed: {len(json_files)}")
    print(f"⚠️  Files moved to bad folder: {files_moved_to_bad}")
    print(f"✅ Files kept in original location: {len(json_files) - files_moved_to_bad}")
    print(f"📸 Total images tested: {total_stats['images_tested']}")
    print(f"✅ Valid images: {total_stats['images_valid']}")
    print(f"❌ Invalid images: {total_stats['images_invalid']}")
    print(f"🎥 Total videos tested: {total_stats['videos_tested']}")
    print(f"✅ Valid videos: {total_stats['videos_valid']}")
    print(f"❌ Invalid videos: {total_stats['videos_invalid']}")
    
    return {
        "files_processed": len(json_files),
        "files_moved_to_bad": files_moved_to_bad,
        "results": results,
        "total_stats": total_stats
    }

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Validate URLs in data files and move bad files to bad folder. By default, validates all JSON files in data directory.')
    parser.add_argument('-f', '--file', help='Specific data file to validate (e.g., data/username_analysis.json)')
    parser.add_argument('-d', '--data-dir', default='data', help='Data directory to validate (default: data)')
    parser.add_argument('-a', '--all', action='store_true', help='Validate all files in data directory (same as default behavior)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (less verbose output)')
    parser.add_argument('--no-move-bad', action='store_true', help='Do not move files with invalid URLs to bad folder')
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    move_bad_files = not args.no_move_bad
    
    if args.file:
        # Validate specific file
        result = validate_data_file(args.file, verbose=verbose, move_bad_files=move_bad_files)
        if "error" in result:
            print(f"❌ {result['error']}")
            return 1
        return 0
    
    elif args.all:
        # Validate all files in data directory
        result = validate_all_data_files(args.data_dir, verbose=verbose, move_bad_files=move_bad_files)
        if "error" in result:
            print(f"❌ {result['error']}")
            return 1
        return 0
    
    else:
        # Default behavior: validate all files in data directory
        print("🔄 No specific file or --all flag provided, validating all JSON files in data directory...")
        result = validate_all_data_files(args.data_dir, verbose=verbose, move_bad_files=move_bad_files)
        if "error" in result:
            print(f"❌ {result['error']}")
            return 1
        return 0

def test_urls_main():
    """Main function to test individual URLs (from old url_validator.py)"""
    parser = argparse.ArgumentParser(description='URL Validator - Test URL validation functionality')
    parser.add_argument('--test-image', help='Test a single image URL')
    parser.add_argument('--test-video', help='Test a single video URL')
    parser.add_argument('--test-batch', nargs='+', help='Test multiple URLs (mix of images and videos)')
    
    args = parser.parse_args()
    
    validator = URLValidator()
    
    if args.test_image:
        print(f"🔍 Testing image URL: {args.test_image}")
        is_valid = validator.validate_image_url(args.test_image, True)
        print(f"Result: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
    elif args.test_video:
        print(f"🔍 Testing video URL: {args.test_video}")
        is_valid = validator.validate_video_url(args.test_video, True)
        print(f"Result: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
    elif args.test_batch:
        print(f"🔍 Testing {len(args.test_batch)} URLs...")
        for i, url in enumerate(args.test_batch, 1):
            print(f"\n{i}. Testing: {url[:80]}...")
            # Try as image first, then video
            is_valid_image = validator.validate_image_url(url, True)
            is_valid_video = validator.validate_video_url(url, True)
            
            if is_valid_image:
                print(f"   Result: ✅ Valid Image")
            elif is_valid_video:
                print(f"   Result: ✅ Valid Video")
            else:
                print(f"   Result: ❌ Invalid")
        
        print(f"\n📊 Validation Summary:")
        validator.print_validation_summary()
        
    else:
        print("URL Validator - Standalone URL validation tool")
        print("Usage examples:")
        print("  python validate_urls.py --test-image https://example.com/image.jpg")
        print("  python validate_urls.py --test-video https://example.com/video.mp4")
        print("  python validate_urls.py --test-batch https://example.com/img1.jpg https://example.com/vid1.mp4")
        print("\nFor full data file validation, use:")
        print("  python validate_urls.py -f data/username_analysis.json")
        print("  python validate_urls.py -a")

if __name__ == "__main__":
    # Check if we're being called with test arguments
    import sys
    if any(arg.startswith('--test-') for arg in sys.argv):
        test_urls_main()
    else:
        exit(main())
