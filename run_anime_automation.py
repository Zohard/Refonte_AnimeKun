#!/usr/bin/env python3
"""
Complete automation script for anime form filling and staff addition
Fixed version with better browser session handling
"""

import subprocess
import sys
import argparse
import os
import time
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def load_json_data(file_path):
    """Load JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return None

def login_to_site(driver, username, password):
    """Handle login to the site"""
    try:
        driver.get("http://www.anime-kun.net/")
        print("Navigated to the main site")
        
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "user")))
        
        username_field.send_keys(username)
        password_field = driver.find_element(By.ID, "passwrd")
        password_field.send_keys(password)
        print("Entered login credentials")
        
        submit_button = driver.find_element(By.ID, "llsubmit")
        submit_button.click()
        print("Submitted login form")
        
        time.sleep(3)
        
        if "forums" in driver.current_url:
            print("✓ Successfully logged in")
            return True
        else:
            print("⚠ Login might have failed")
            return False
    
    except Exception as e:
        print(f"✗ Error during login: {e}")
        return False

def fill_anime_form(driver, json_file_path, wait_time=30, submit=True):
    """Fill the anime form using the existing form filling logic"""
    print(f"\n=== FILLING FORM FOR: {os.path.basename(json_file_path)} ===")
    
    anime_data = load_json_data(json_file_path)
    if not anime_data:
        print(f"Failed to load JSON data from {json_file_path}")
        return None
    
    try:
        # Navigate to the admin page for adding a new anime
        driver.get("http://www.anime-kun.net/__zone-admin__/anime.php?page=Ajout")
        print("Navigated to the anime addition page")
        
        # Wait for the form to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "informations_principales")))
        print("Form loaded successfully")
        
        # Fill in the main title
        title_field = driver.find_element(By.ID, "titre")
        title_field.clear()
        title_field.send_keys(anime_data["title"])
        print("✓ Title filled:", anime_data["title"])
        
        # Select the format (assuming it's a TV series)
        from selenium.webdriver.support.ui import Select
        format_select = Select(driver.find_element(By.ID, "format"))
        format_select.select_by_value("Série TV")
        print("✓ Format selected: Série TV")
        
        # Fill in the year
        year_field = driver.find_element(By.ID, "annee")
        year_field.clear()
        year_field.send_keys("2025")
        print("✓ Year field filled: 2025")
        
        # Fill in the original title
        original_title_field = driver.find_element(By.ID, "titre_orig")
        original_title_field.clear()
        original_title_field.send_keys(anime_data["title"])
        print("✓ Original title field filled:", anime_data["title"])
        
        # Fill in alternative titles
        alt_titles_text = ""
        
        if "sources" in anime_data:
            if "nautiljon" in anime_data["sources"] and "alternative_titles" in anime_data["sources"]["nautiljon"]:
                nautiljon_alt_titles = anime_data["sources"]["nautiljon"]["alternative_titles"]
                if nautiljon_alt_titles and len(nautiljon_alt_titles) > 0:
                    alt_titles_text = "\n".join(nautiljon_alt_titles)
            elif "myanimelist" in anime_data["sources"] and "alt_titles" in anime_data["sources"]["myanimelist"]:
                mal_alt_titles = anime_data["sources"]["myanimelist"]["alt_titles"]
                if mal_alt_titles and mal_alt_titles.strip():
                    alt_titles_text = mal_alt_titles
        elif "alternative_titles" in anime_data and anime_data["alternative_titles"]:
            alt_titles_text = "\n".join(anime_data["alternative_titles"])
        
        if alt_titles_text:
            alt_titles_field = driver.find_element(By.ID, "titres_alternatifs")
            alt_titles_field.clear()
            alt_titles_field.send_keys(alt_titles_text)
            print("✓ Alternative titles field filled")
        
        # Select license status
        license_select = Select(driver.find_element(By.ID, "licence"))
        license_select.select_by_value("0")
        print("✓ License status selected: Not licensed")
        
        # Fill episodes
        episode_count = "NC"
        if "episode_count" in anime_data and anime_data["episode_count"]:
            episode_count = str(anime_data["episode_count"])
        
        episodes_field = driver.find_element(By.ID, "nb_episodes")
        episodes_field.clear()
        episodes_field.send_keys(episode_count)
        print("✓ Episodes field filled:", episode_count)
        
        # Fill official site
        official_site = ""
        if "official_websites" in anime_data and anime_data["official_websites"]:
            # Filter out social media sites
            social_media = ["twitter", "facebook", "instagram", "youtube", "tiktok", "weibo"]
            for site in anime_data["official_websites"]:
                if site and all(social not in site.lower() for social in social_media):
                    official_site = site
                    break
            if not official_site and anime_data["official_websites"]:
                official_site = anime_data["official_websites"][0]
        
        if official_site:
            site_field = driver.find_element(By.ID, "site_officiel")
            site_field.clear()
            site_field.send_keys(official_site)
            print("✓ Official site field filled:", official_site)
        
        # Fill voice actors
        voice_actors_text = ""
        if "sources" in anime_data and "myanimelist" in anime_data["sources"]:
            characters = anime_data["sources"]["myanimelist"].get("characters", [])
            for character in characters:
                if "voice_actors" in character and character["voice_actors"]:
                    for va in character["voice_actors"]:
                        if "language" in va and va["language"] == "Japanese":
                            formatted_name = va['name'].replace(", ", " ")
                            character_name = character['name'].replace(", ", " ")
                            voice_actors_text += f"{formatted_name} ({character_name}), "
            
            if voice_actors_text:
                voice_actors_text = voice_actors_text[:-2]  # Remove trailing comma
                doubleurs_field = driver.find_element(By.ID, "doubleurs")
                doubleurs_field.clear()
                doubleurs_field.send_keys(voice_actors_text)
                print("✓ Voice actors field filled")
        
        # Submit the form if requested
        if submit:
            submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
            submit_button.click()
            print("✓ Form submitted")
            
            # Wait for submission to process
            time.sleep(5)
            
            # Extract anime ID
            anime_id = extract_anime_id_from_page(driver)
            if anime_id:
                save_anime_id_to_file(anime_id, json_file_path)
                print(f"✓ Anime ID {anime_id} saved for staff processing")
                return anime_id
            else:
                print("⚠ Warning: Could not extract anime ID")
                return None
        else:
            print("Form filled but not submitted")
            return None
            
    except Exception as e:
        print(f"✗ Error filling form: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_anime_id_from_page(driver):
    """Extract anime ID from the current page"""
    try:
        # Method 1: Get from the span element
        id_element = driver.find_element(By.ID, "id_anime")
        anime_id = id_element.text.strip()
        if anime_id:
            return anime_id
    except:
        pass
    
    try:
        # Method 2: Get from hidden input field
        hidden_input = driver.find_element(By.CSS_SELECTOR, "input[name='id_anime']")
        anime_id = hidden_input.get_attribute("value")
        if anime_id:
            return anime_id
    except:
        pass
    
    try:
        # Method 3: Extract from URL
        current_url = driver.current_url
        if "id_fiche=" in current_url:
            anime_id = current_url.split("id_fiche=")[1].split("&")[0]
            return anime_id
    except:
        pass
    
    return None

def save_anime_id_to_file(anime_id, json_file_path):
    """Save the anime ID to a text file"""
    if not anime_id:
        return False
    
    base_name = os.path.splitext(os.path.basename(json_file_path))[0]
    json_dir = os.path.dirname(json_file_path) or "."
    id_file_path = os.path.join(json_dir, f"{base_name}_anime_id.txt")
    
    try:
        with open(id_file_path, 'w') as f:
            f.write(anime_id)
        print(f"✓ Saved anime ID {anime_id} to {id_file_path}")
        return True
    except Exception as e:
        print(f"✗ Error saving anime ID: {e}")
        return False

def process_staff_and_tags(driver, json_file_path, anime_id, auto_submit=False):
    """Process staff and tags using the same browser session"""
    print(f"\n=== PROCESSING STAFF AND TAGS FOR: {os.path.basename(json_file_path)} ===")
    
    try:
        # Import the necessary modules from add_staff.py
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Import functions we need
        from add_staff import (
            extract_staff_info, 
            extract_genres_and_themes, 
            TagSelector,
            add_staff_member,
            ROLE_MAPPING
        )
        
        anime_data = load_json_data(json_file_path)
        if not anime_data:
            print("Failed to load JSON data")
            return False
        
        # === PROCESS GENRES AND THEMES ===
        print("\n--- Processing Genres and Themes ---")
        
        # Navigate to the modification page for tags
        modification_url = f"http://www.anime-kun.net/__zone-admin__/anime.php?page=Modification&id_fiche={anime_id}"
        driver.get(modification_url)
        print(f"Navigated to modification page for anime ID: {anime_id}")
        
        # Initialize tag selector
        tag_selector = TagSelector(driver)
        
        # Wait for page to load
        if tag_selector.wait_for_page_load():
            # Extract and process genres and themes
            genres, themes = extract_genres_and_themes(anime_data)
            
            if genres:
                successful_genres, failed_genres = tag_selector.select_tags(genres, "genres")
                print(f"✓ Genres: {successful_genres} successful, {len(failed_genres)} failed")
            
            if themes:
                successful_themes, failed_themes = tag_selector.select_tags(themes, "themes")
                print(f"✓ Themes: {successful_themes} successful, {len(failed_themes)} failed")
        else:
            print("⚠ Failed to load tags page")
        
        # === PROCESS STAFF ===
        print("\n--- Processing Staff ---")
        
        staff_list = extract_staff_info(anime_data)
        if not staff_list:
            print("No staff information found")
            return True
        
        print(f"Found {len(staff_list)} staff members to add")
        
        # Navigate to staff management page
        staff_url = f"http://www.anime-kun.net/__zone-admin__/anime.php?page=Modification2&id_fiche={anime_id}"
        driver.get(staff_url)
        print(f"Navigated to staff management page for anime ID: {anime_id}")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "name_business")))
        print("✓ Staff management form loaded successfully")
        
        successful_additions = 0
        for i, staff_member in enumerate(staff_list):
            print(f"\nProcessing staff member {i+1}/{len(staff_list)}: {staff_member['name']} - {staff_member['role']}")
            
            success = add_staff_member(
                driver=driver,
                name=staff_member["name"],
                role=staff_member["role"],
                wait=wait,
                auto_submit=auto_submit
            )
            
            if success:
                successful_additions += 1
            
            time.sleep(2)  # Wait between staff additions
        
        print(f"\n✓ Staff processing completed")
        print(f"  Successfully added: {successful_additions}")
        print(f"  Failed: {len(staff_list) - successful_additions}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error processing staff and tags: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_json_files(json_path):
    """Get list of JSON files to process"""
    json_files = []
    
    if os.path.isdir(json_path):
        pattern = os.path.join(json_path, "*.json")
        json_files = glob.glob(pattern)
        print(f"Found {len(json_files)} JSON files in directory: {json_path}")
        for f in json_files:
            print(f"  - {os.path.basename(f)}")
    elif os.path.isfile(json_path) and json_path.endswith('.json'):
        json_files = [json_path]
        print(f"Processing single JSON file: {json_path}")
    else:
        print(f"Error: {json_path} is not a valid JSON file or directory")
        return []
    
    return json_files

def main():
    parser = argparse.ArgumentParser(description='Automate anime form filling and staff addition')
    parser.add_argument('json_file', help='Path to the JSON file or directory containing anime data')
    parser.add_argument('--username', default="*****", help='Username for login (default: test)')
    parser.add_argument('--password', default="*****", help='Password for login (default: test)')
    parser.add_argument('--wait-time', type=int, default=30, help='Time in seconds to wait after filling the form (default: 30)')
    parser.add_argument('--no-staff', action='store_true', help='Skip staff addition step')
    parser.add_argument('--staff-auto-submit', action='store_true', help='Auto-submit staff entries')
    parser.add_argument('--form-only', action='store_true', help='Only run form filling, skip staff processing entirely')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode (keep browser open)')
    
    args = parser.parse_args()
    
    # Get list of JSON files to process
    json_files = get_json_files(args.json_file)
    
    if not json_files:
        print("No JSON files found to process")
        sys.exit(1)
    
    # Initialize webdriver with appropriate options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if not args.debug:
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Login once at the beginning
        print("=== LOGGING IN ===")
        login_success = login_to_site(driver, args.username, args.password)
        if not login_success:
            print("⚠ Could not verify successful login. Continuing anyway...")
        
        # Process each JSON file
        successful_forms = 0
        successful_staff = 0
        
        for json_file_path in json_files:
            print(f"\n{'*'*80}")
            print(f"PROCESSING: {os.path.basename(json_file_path)}")
            print(f"{'*'*80}")
            
            # Step 1: Fill the form
            anime_id = fill_anime_form(driver, json_file_path, args.wait_time, submit=True)
            
            if anime_id:
                successful_forms += 1
                print(f"✓ Form filling successful for {os.path.basename(json_file_path)}")
                
                # Step 2: Process staff and tags if requested
                if not args.no_staff and not args.form_only:
                    staff_success = process_staff_and_tags(
                        driver, 
                        json_file_path, 
                        anime_id, 
                        auto_submit=args.staff_auto_submit
                    )
                    
                    if staff_success:
                        successful_staff += 1
                        print(f"✓ Staff processing successful for {os.path.basename(json_file_path)}")
                    else:
                        print(f"⚠ Staff processing had issues for {os.path.basename(json_file_path)}")
            else:
                print(f"✗ Form filling failed for {os.path.basename(json_file_path)}")
                continue
            
            # Wait between different anime processing (except for the last one)
            if json_file_path != json_files[-1]:
                print(f"Waiting 10 seconds before processing next file...")
                time.sleep(10)
        
        # Final summary
        print("\n" + "="*80)
        print("AUTOMATION SUMMARY")
        print("="*80)
        print(f"Total JSON files found: {len(json_files)}")
        print(f"Successful form submissions: {successful_forms}")
        
        if not args.no_staff and not args.form_only:
            print(f"Successful staff additions: {successful_staff}")
        
        print(f"Failed form submissions: {len(json_files) - successful_forms}")
        
        if not args.no_staff and not args.form_only:
            print(f"Failed staff additions: {successful_forms - successful_staff}")
        
        print("="*80)
        
        if successful_forms == len(json_files):
            print("🎉 All files processed successfully!")
        elif successful_forms > 0:
            print("⚠ Some files processed successfully, check the logs above for details")
        else:
            print("❌ No files were processed successfully")
        
        if args.debug:
            print("\nDEBUG MODE: Keeping browser open for inspection...")
            input("Press Enter to close browser...")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if not args.debug:
            driver.quit()
        print("Script completed.")

if __name__ == "__main__":
    main()