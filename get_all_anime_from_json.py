#!/usr/bin/env python3
import argparse
import json
import sys
import time
import os
import re

# Import the individual scrapers
from get_info_json_myanime import MyAnimeListScraper
import nautiljon_scraper

class CombinedAnimeScraper:
    def __init__(self, webdriver_path=None, headless=True):
        self.mal_scraper = MyAnimeListScraper()
        self.webdriver_path = webdriver_path
        self.headless = headless
    
    def scrape_anime(self, anime_name, nautiljon_url=None, nautiljon_only=False):
        """
        Scrape anime information from both MyAnimeList and Nautiljon, or just Nautiljon
        
        Args:
            anime_name (str): Name of the anime to search
            nautiljon_url (str, optional): Direct URL for Nautiljon page
            nautiljon_only (bool): If True, only scrape from Nautiljon
        
        Returns:
            dict: Combined anime information from both sources, or just Nautiljon
        """
        combined_info = {
            "title": "",
            "sources": {}
        }
        
        # Step 1: Scrape Nautiljon (now first priority)
        print("\n=== Scraping Nautiljon ===")
        
        # Get the URL or format it
        if not nautiljon_url:
            nautiljon_url = nautiljon_scraper.format_anime_url(anime_name)
        
        print(f"Using Nautiljon URL: {nautiljon_url}")
        nautiljon_info = nautiljon_scraper.scrape_nautiljon_with_selenium(
            nautiljon_url,
            webdriver_path=self.webdriver_path,
            headless=self.headless
        )
        
        if nautiljon_info:
            combined_info["title"] = nautiljon_info.get("title", "")
            combined_info["sources"]["nautiljon"] = nautiljon_info
            print(f"✓ Successfully scraped data from Nautiljon")
        else:
            print("× Failed to scrape data from Nautiljon")
        
        # If nautiljon_only is True, skip MyAnimeList scraping
        if nautiljon_only:
            print("\n=== Nautiljon-only mode: Skipping MyAnimeList ===")
            if nautiljon_info:
                # Return only Nautiljon data with simplified structure
                return {
                    "title": nautiljon_info.get("title", ""),
                    "source": "nautiljon",
                    **nautiljon_info
                }
            else:
                print("Failed to scrape data from Nautiljon")
                return None
        
        # Step 2: Scrape MyAnimeList (only if not nautiljon_only)
        print("\n=== Scraping MyAnimeList ===")
        
        mal_url = self.mal_scraper.search_anime(anime_name)
        if mal_url:
            mal_info = self.mal_scraper.get_anime_info(mal_url)
        else:
            mal_info = None
        
        if mal_info:
            # Only set title from MAL if we don't have one from Nautiljon
            if not combined_info["title"]:
                combined_info["title"] = mal_info.get("title", "")
            combined_info["sources"]["myanimelist"] = mal_info
            print(f"✓ Successfully scraped data from MyAnimeList")
        else:
            print("× Failed to scrape data from MyAnimeList")
        
        # Step 3: Merge the information to create a comprehensive record
        if combined_info["sources"]:
            combined_info.update(self._merge_info(combined_info["sources"]))
            return combined_info
        else:
            print("Failed to scrape data from any source")
            return None
    
    def _is_social_media_url(self, url):
        """
        Check if a URL is from social media platforms that should be excluded from official websites
        
        Args:
            url (str): URL to check
        
        Returns:
            bool: True if the URL is from a social media platform, False otherwise
        """
        if not url:
            return False
        
        # List of social media domains to exclude
        social_media_domains = [
            'twitter.com',
            'x.com',
            'facebook.com',
            'instagram.com',
            'youtube.com',
            'tiktok.com',
            'weibo.com',
            'linkedin.com',
            'discord.gg',
            'discord.com'
        ]
        
        url_lower = url.lower()
        return any(domain in url_lower for domain in social_media_domains)
    
    def _merge_info(self, sources):
        """
        Merge information from different sources with Nautiljon priority
        
        Args:
            sources (dict): Dictionary with keys as source names and values as source data
        
        Returns:
            dict: Merged anime information with Nautiljon taking priority
        """
        merged = {
            "title": "",
            "alternative_titles": [],
            "synopsis": "",
            "genres": [],
            "themes": [],
            "studios": [],
            "staff": [],
            "episodes": [],
            "airing_info": {},
            "streaming": [],
            "official_websites": [],
            "scores": {},
            "source_urls": {}
        }
        
        # Add source URLs
        for source_name, source_data in sources.items():
            if source_name == "myanimelist" and source_data.get("url"):
                merged["source_urls"]["myanimelist"] = source_data["url"]
            elif source_name == "nautiljon":
                if source_data.get("url"):
                    merged["source_urls"]["nautiljon"] = source_data["url"]
        
        # Title: Prefer Nautiljon (changed priority)
        if sources.get("nautiljon", {}).get("title"):
            merged["title"] = sources["nautiljon"]["title"]
        elif sources.get("myanimelist", {}).get("title"):
            merged["title"] = sources["myanimelist"]["title"]
        
        # Alternative Titles: Combine from both sources
        alt_titles = set()
        
        # From Nautiljon first
        if sources.get("nautiljon", {}).get("alternative_titles"):
            for title in sources["nautiljon"]["alternative_titles"]:
                if title:
                    alt_titles.add(title)
        
        # From MAL
        if sources.get("myanimelist", {}).get("alt_titles"):
            for title in sources["myanimelist"]["alt_titles"].split(","):
                title = title.strip()
                if title:
                    alt_titles.add(title)
        
        merged["alternative_titles"] = list(alt_titles)
        
        # Synopsis: Prefer Nautiljon (changed priority)
        if sources.get("nautiljon", {}).get("synopsis"):
            merged["synopsis"] = sources["nautiljon"]["synopsis"]
        elif sources.get("myanimelist", {}).get("synopsis") and sources["myanimelist"]["synopsis"] != "No synopsis available":
            merged["synopsis"] = sources["myanimelist"]["synopsis"]
        
        # Genres, Themes: Combine from both sources (Nautiljon first)
        genres_set = set()
        themes_set = set()
        
        # Nautiljon first
        if sources.get("nautiljon"):
            for genre in sources["nautiljon"].get("genres", []):
                genres_set.add(genre)
            for theme in sources["nautiljon"].get("themes", []):
                themes_set.add(theme)
        
        # Then MAL
        if sources.get("myanimelist"):
            for genre in sources["myanimelist"].get("genres", []):
                genres_set.add(genre)
            for theme in sources["myanimelist"].get("themes", []):
                themes_set.add(theme)
        
        merged["genres"] = list(genres_set)
        merged["themes"] = list(themes_set)
        
        # Studios: Prefer Nautiljon, then combine
        studios_set = set()
        
        if sources.get("nautiljon", {}).get("studio"):
            studios_set.add(sources["nautiljon"]["studio"])
        
        if sources.get("myanimelist"):
            for studio in sources["myanimelist"].get("studios", []):
                studios_set.add(studio)
        
        merged["studios"] = list(studios_set)
        
        # Staff: Prefer Nautiljon (changed priority)
        if sources.get("nautiljon", {}).get("staff"):
            merged["staff"] = sources["nautiljon"]["staff"]
        elif sources.get("myanimelist", {}).get("staff"):
            merged["staff"] = sources["myanimelist"]["staff"]
        
        # Episodes: Prefer Nautiljon's episode details
        if sources.get("nautiljon", {}).get("episodes"):
            merged["episodes"] = sources["nautiljon"]["episodes"]
        
        # Episode count: Prefer Nautiljon
        if sources.get("nautiljon", {}).get("episodes_count"):
            merged["episode_count"] = sources["nautiljon"]["episodes_count"]
        elif sources.get("myanimelist", {}).get("episodes"):
            merged["episode_count"] = sources["myanimelist"]["episodes"]
        
        # Airing Information: Prefer Nautiljon data
        merged["airing_info"] = {}
        
        # Nautiljon first
        if sources.get("nautiljon"):
            if sources["nautiljon"].get("airing_dates"):
                merged["airing_info"]["dates"] = sources["nautiljon"]["airing_dates"]
            if sources["nautiljon"].get("season"):
                merged["airing_info"]["season"] = sources["nautiljon"]["season"]
        
        # MAL as backup/supplement
        if sources.get("myanimelist"):
            if sources["myanimelist"].get("status"):
                merged["airing_info"]["status"] = sources["myanimelist"]["status"]
            if sources["myanimelist"].get("aired") and not merged["airing_info"].get("dates"):
                merged["airing_info"]["aired"] = sources["myanimelist"]["aired"]
            if sources["myanimelist"].get("season") and not merged["airing_info"].get("season"):
                merged["airing_info"]["season"] = sources["myanimelist"]["season"]
        
        # Streaming platforms: From Nautiljon (MAL doesn't have this)
        if sources.get("nautiljon", {}).get("streaming"):
            merged["streaming"] = sources["nautiljon"]["streaming"]
        
        # Official Websites: Combine from both (Nautiljon first) - EXCLUDE SOCIAL MEDIA
        websites = set()
        
        if sources.get("nautiljon", {}).get("official_website"):
            for site in sources["nautiljon"]["official_website"]:
                if site and not self._is_social_media_url(site):
                    websites.add(site)
                elif site and self._is_social_media_url(site):
                    print(f"Excluding social media URL: {site}")
        
        if sources.get("myanimelist", {}).get("official_site"):
            site = sources["myanimelist"]["official_site"]
            if site and not self._is_social_media_url(site):
                websites.add(site)
            elif site and self._is_social_media_url(site):
                print(f"Excluding social media URL: {site}")
        
        merged["official_websites"] = list(websites)
        
        # Scores: From both sources (keeping both for comparison)
        if sources.get("nautiljon"):
            if sources["nautiljon"].get("popularity"):
                merged["scores"]["nautiljon_popularity"] = sources["nautiljon"]["popularity"]
            if sources["nautiljon"].get("trend"):
                merged["scores"]["nautiljon_trend"] = sources["nautiljon"]["trend"]
        
        if sources.get("myanimelist"):
            if sources["myanimelist"].get("score"):
                merged["scores"]["myanimelist"] = sources["myanimelist"]["score"]
            if sources["myanimelist"].get("rank"):
                merged["scores"]["mal_rank"] = sources["myanimelist"]["rank"]
            if sources["myanimelist"].get("popularity"):
                merged["scores"]["mal_popularity"] = sources["myanimelist"]["popularity"]
        
        return merged

def sanitize_filename(name):
    """
    Remove invalid filename characters and replace spaces with underscores.
    """
    return re.sub(r'[\\/*?:"<>|]', '', name).replace(' ', '_')

def main():
    parser = argparse.ArgumentParser(description="Combined anime scraper from MyAnimeList and Nautiljon")
    parser.add_argument("input", help="Anime name or path to text file with list of anime names")
    parser.add_argument("--nautiljon-url", "-n", help="Specific Nautiljon URL to scrape (ignored if list is provided)")
    parser.add_argument("--nautiljon-only", "-N", action="store_true", help="Only scrape from Nautiljon (skip MyAnimeList)")
    parser.add_argument("--output-dir", "-o", help="Directory to save JSON results", default="anime_results")
    parser.add_argument("--webdriver-path", "-w", help="Path to ChromeDriver executable")
    parser.add_argument("--no-headless", action="store_true", help="Run Chrome in visible mode (not headless)")

    args = parser.parse_args()

    scraper = CombinedAnimeScraper(
        webdriver_path=args.webdriver_path,
        headless=not args.no_headless
    )

    os.makedirs(args.output_dir, exist_ok=True)

    # Check if input is a file
    if os.path.isfile(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            anime_list = []
            for line in f:
                line = line.strip()
                # Remove leading numbers and punctuation
                cleaned_title = re.sub(r'^\s*\d+\s*[\.\)\:\-\s]*', '', line)
                if cleaned_title:
                    anime_list.append(cleaned_title)
        
        for anime_name in anime_list:
            print(f"\n--- Processing: {anime_name} ---")
            result = scraper.scrape_anime(anime_name, nautiljon_only=args.nautiljon_only)
            if result:
                output_path = os.path.join(args.output_dir, f"{sanitize_filename(anime_name)}.json")
                with open(output_path, 'w', encoding='utf-8') as f_out:
                    json.dump(result, f_out, indent=2, ensure_ascii=False)
                print(f"✓ Saved to {output_path}")
            else:
                print(f"× Failed to retrieve information for: {anime_name}")

    else:
        # Single anime mode
        result = scraper.scrape_anime(
            args.input, 
            args.nautiljon_url,
            nautiljon_only=args.nautiljon_only
        )
        
        if result:
            safe_title = sanitize_filename(result['title'])
            output_filename = f"{safe_title}.json"
            output_path = os.path.join(args.output_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f_out:
                json.dump(result, f_out, indent=2, ensure_ascii=False)
            print(f"\n✓ Results saved to {output_path}")
        else:
            print("\n× Failed to retrieve anime information.")
            sys.exit(1)

if __name__ == "__main__":
    main()