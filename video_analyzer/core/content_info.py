import os
import re
from typing import Dict

class ContentInfo:
    @staticmethod
    def extract_title_info(filename: str) -> Dict:
        """Extract TV show or movie title from filename."""
        # Common patterns for TV shows: "Show.Name.S01E02" or "Show Name - S01E02"
        tv_pattern = re.compile(r'(.+?)[.\s-]+[Ss](\d+)[Ee](\d+)', re.IGNORECASE)
        
        # Try to match TV show pattern
        tv_match = tv_pattern.search(filename)
        if tv_match:
            show_name = tv_match.group(1).replace('.', ' ').strip()
            season = int(tv_match.group(2))
            episode = int(tv_match.group(3))
            return {
                'type': 'tv_show',
                'title': show_name,
                'season': season,
                'episode': episode
            }
        
        # If not a TV show, assume it's a movie
        # Remove file extension and common tags
        clean_name = os.path.splitext(filename)[0]
        common_tags = [
            '1080p', '720p', '2160p', '4K', 'HDR', 'HEVC', 'x264', 'x265', 
            'BluRay', 'WEB-DL', 'REMUX', 'AMZN', 'NF', 'DSNP', 'HULU'
        ]
        
        for tag in common_tags:
            clean_name = re.sub(
                r'[.\s-]*' + tag + r'[.\s-]*',
                ' ',
                clean_name,
                flags=re.IGNORECASE
            )
        
        # Remove year in parentheses or brackets
        clean_name = re.sub(r'[\(\[\.\s-]*\d{4}[\)\]\.\s-]*', ' ', clean_name)
        
        return {
            'type': 'movie',
            'title': clean_name.replace('.', ' ').strip()
        } 