from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os
import argparse
import sys


def get_json_file_list(path):
    """
    Returns a list of JSON file paths from a directory, 
    or a list with a single file if a file is provided.
    """
    if os.path.isdir(path):
        return [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(".json")]
    elif os.path.isfile(path) and path.lower().endswith(".json"):
        return [path]
    else:
        print(f"Error: {path} is not a valid JSON file or directory.")
        return []

# Load the JSON data from a file
def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} does not contain valid JSON.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def extract_anime_id_from_page(driver):
    """
    Extract anime ID from the current page
    """
    try:
        # Method 1: Get from the span element
        id_element = driver.find_element(By.ID, "id_anime")
        anime_id = id_element.text.strip()
        
        if anime_id:
            print(f"Found anime ID: {anime_id}")
            return anime_id
    except:
        pass
    
    try:
        # Method 2: Get from hidden input field
        hidden_input = driver.find_element(By.CSS_SELECTOR, "input[name='id_anime']")
        anime_id = hidden_input.get_attribute("value")
        
        if anime_id:
            print(f"Found anime ID from hidden input: {anime_id}")
            return anime_id
    except:
        pass
    
    try:
        # Method 3: Extract from URL
        current_url = driver.current_url
        if "id_fiche=" in current_url:
            anime_id = current_url.split("id_fiche=")[1].split("&")[0]
            print(f"Found anime ID from URL: {anime_id}")
            return anime_id
    except:
        pass
    
    print("Could not extract anime ID from page")
    return None

def save_anime_id_to_file(anime_id, json_file_path):
    """
    Save the anime ID to a text file for later use
    """
    if not anime_id:
        return False
    
    # Create the ID file name based on the JSON file name
    base_name = os.path.splitext(os.path.basename(json_file_path))[0]
    json_dir = os.path.dirname(json_file_path) or "."
    id_file_path = os.path.join(json_dir, f"{base_name}_anime_id.txt")
    
    try:
        with open(id_file_path, 'w') as f:
            f.write(anime_id)
        print(f"Saved anime ID {anime_id} to {id_file_path}")
        return True
    except Exception as e:
        print(f"Error saving anime ID to file: {e}")
        return False

# Function to handle login
def login_to_site(driver, username, password):
    try:
        # Go to the main site
        driver.get("http://www.anime-kun.net/")
        print("Navigated to the main site")
        
        # Wait for the login form to load
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "user")))
        
        # Enter username and password
        username_field.send_keys(username)
        password_field = driver.find_element(By.ID, "passwrd")
        password_field.send_keys(password)
        print("Entered login credentials")
        
        # Submit the form
        submit_button = driver.find_element(By.ID, "llsubmit")
        submit_button.click()
        print("Submitted login form")
        
        # Wait for the login to process
        time.sleep(3)
        
        # Check if login was successful
        if "forums" in driver.current_url:
            print("Successfully logged in")
            return True
        else:
            print("Login might have failed")
            return False
    
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return False

# Parse command line arguments
parser = argparse.ArgumentParser(description='Fill anime form with data from a JSON file')
parser.add_argument('json_file', help='Path to the JSON file containing anime data')
parser.add_argument('--username', default="******", help='Username for login (default: test)')
parser.add_argument('--password', default="******", help='Password for login (default: test)')
parser.add_argument('--wait-time', type=int, default=30, help='Time in seconds to wait after filling the form (default: 30)')
parser.add_argument('--submit', action='store_true', help='Submit the form after filling it')

# Parse the arguments
args = parser.parse_args()

# Get list of JSON files
json_files = get_json_file_list(args.json_file)

if not json_files:
    print("No valid JSON files found. Exiting script.")
    sys.exit(1)

# Initialize the webdriver once
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    for json_file_path in json_files:
        print(f"\nProcessing file: {json_file_path}")

        anime_data = load_json_data(json_file_path)
        if not anime_data:
            print(f"Skipping {json_file_path} due to loading error.")
            continue

        # Login to the site (only once)
        if json_file_path == json_files[0]:  # Only login for the first file
            login_success = login_to_site(driver, args.username, args.password)
            
            if not login_success:
                print("Could not verify successful login. Continuing anyway...")
        
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
        print("Title filled:", anime_data["title"])
        
        # Select the format (assuming it's a TV series)
        format_select = Select(driver.find_element(By.ID, "format"))
        format_select.select_by_value("Série TV")
        print("Format selected: Série TV")
        
        # Fill in the year (assuming 2025, update as needed)
        year_field = driver.find_element(By.ID, "annee")
        year_field.clear()
        year_field.send_keys("2025")
        print("Year field filled: 2025")
        
        # Fill in the original title (Japanese)
        original_title_field = driver.find_element(By.ID, "titre_orig")
        original_title_field.clear()
        original_title_field.send_keys(anime_data["title"])
        print("Original title field filled:", anime_data["title"])
        
        # Fill in alternative titles
        alt_titles_text = ""
        
        # Check if we have a combined format with sources
        if "sources" in anime_data:
            # First try to get alternative titles from Nautiljon
            if "nautiljon" in anime_data["sources"] and "alternative_titles" in anime_data["sources"]["nautiljon"]:
                nautiljon_alt_titles = anime_data["sources"]["nautiljon"]["alternative_titles"]
                if nautiljon_alt_titles and len(nautiljon_alt_titles) > 0:
                    alt_titles_text = "\n".join(nautiljon_alt_titles)
                    print("Using alternative titles from Nautiljon")
            
            # If no Nautiljon titles found, try MyAnimeList
            if not alt_titles_text and "myanimelist" in anime_data["sources"] and "alt_titles" in anime_data["sources"]["myanimelist"]:
                mal_alt_titles = anime_data["sources"]["myanimelist"]["alt_titles"]
                if mal_alt_titles and mal_alt_titles.strip():
                    alt_titles_text = mal_alt_titles
                    print("Using alternative titles from MyAnimeList")
        
        # If we have merged alternative_titles at the top level, use those
        elif "alternative_titles" in anime_data and anime_data["alternative_titles"]:
            alt_titles_text = "\n".join(anime_data["alternative_titles"])
            print("Using alternative titles from merged data")
        
        # Fall back to the original alt_titles field if it exists
        elif "alt_titles" in anime_data and anime_data["alt_titles"]:
            alt_titles_text = anime_data["alt_titles"]
            print("Using original alt_titles field")
        
        if alt_titles_text:
            alt_titles_field = driver.find_element(By.ID, "titres_alternatifs")
            alt_titles_field.clear()
            alt_titles_field.send_keys(alt_titles_text)
            print("Alternative titles field filled:", alt_titles_text)
        else:
            print("No alternative titles found")
        
        # Select if it's licensed in France (assuming no)
        license_select = Select(driver.find_element(By.ID, "licence"))
        license_select.select_by_value("0")
        print("License status selected: Not licensed")
        
        # Fill in the number of episodes with "NC" (Non Communiqué) by default
        episode_count = "NC"  # Default value
        
        # We only try to get episode count if explicitly specified in the JSON
        if "episode_count" in anime_data and anime_data["episode_count"]:
            episode_count = str(anime_data["episode_count"])
        
        episodes_field = driver.find_element(By.ID, "nb_episodes")
        episodes_field.clear()
        episodes_field.send_keys(episode_count)
        print("Episodes field filled:", episode_count)
        
        # Fill in the official site if available
        official_site = ""
        
        # Helper function to filter out social media sites and prioritize official websites
        def prioritize_official_sites(websites):
            # List of common social media domains to deprioritize
            social_media = ["twitter", "facebook", "instagram", "youtube", "tiktok", "weibo"]
            
            # First try to find a site that doesn't contain any social media names
            for site in websites:
                if site and all(social not in site.lower() for social in social_media):
                    return site
            
            # If no non-social media site is found, return the first available site
            if websites:
                return websites[0]
            
            return ""
        
        # Try to get official site from merged data or sources
        if "official_websites" in anime_data and anime_data["official_websites"]:
            official_site = prioritize_official_sites(anime_data["official_websites"])
        elif "source_urls" in anime_data:
            if "myanimelist" in anime_data["source_urls"]:
                official_site = anime_data["source_urls"]["myanimelist"]
            elif "nautiljon" in anime_data["source_urls"]:
                official_site = anime_data["source_urls"]["nautiljon"]
        elif "sources" in anime_data:
            if "myanimelist" in anime_data["sources"] and "official_site" in anime_data["sources"]["myanimelist"]:
                official_site = anime_data["sources"]["myanimelist"]["official_site"]
            elif "nautiljon" in anime_data["sources"] and "official_website" in anime_data["sources"]["nautiljon"] and anime_data["sources"]["nautiljon"]["official_website"]:
                official_site = prioritize_official_sites(anime_data["sources"]["nautiljon"]["official_website"])
        elif "official_site" in anime_data and anime_data["official_site"] != "No official site found":
            official_site = anime_data["official_site"]
        
        if official_site:
            site_field = driver.find_element(By.ID, "site_officiel")
            site_field.clear()
            site_field.send_keys(official_site)
            print("Official site field filled:", official_site)
        else:
            print("No official site found")
        
        # Fill in the voice actors
        voice_actors_text = ""
        
        # Function to extract voice actors based on various data structures
        def extract_voice_actors(data):
            result = ""
            
            # Handle original structure
            if "characters" in data:
                for character in data["characters"]:
                    if "voice_actors" in character and character["voice_actors"]:
                        for va in character["voice_actors"]:
                            if "language" in va and va["language"] == "Japanese":
                                # Get the name without splitting by comma
                                formatted_name = va['name'].replace(", ", " ")
                                
                                # Get the character name without comma
                                character_name = character['name'].replace(", ", " ")
                                
                                result += f"{formatted_name} ({character_name}), "
            
            # Handle combined/merged structure
            elif "sources" in data and "myanimelist" in data["sources"] and "characters" in data["sources"]["myanimelist"]:
                for character in data["sources"]["myanimelist"]["characters"]:
                    if "voice_actors" in character and character["voice_actors"]:
                        for va in character["voice_actors"]:
                            if "language" in va and va["language"] == "Japanese":
                                # Get the name without splitting by comma
                                formatted_name = va['name'].replace(", ", " ")
                                
                                # Get the character name without comma
                                character_name = character['name'].replace(", ", " ")
                                
                                result += f"{formatted_name} ({character_name}), "
            
            # Remove the trailing comma and space if exists
            if result:
                result = result[:-2]
            
            return result
        
        voice_actors_text = extract_voice_actors(anime_data)
        
        if voice_actors_text:
            doubleurs_field = driver.find_element(By.ID, "doubleurs")
            doubleurs_field.clear()
            doubleurs_field.send_keys(voice_actors_text)
            print("Voice actors field filled")
        else:
            print("No voice actors found")
        
        # Do not fill in synopsis as requested
        print("Skipping synopsis field as requested")
        
        # Do not fill in comment field as requested
        print("Skipping commentaire field as requested")
        
        # Submit the form if requested
        if args.submit:
            submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
            submit_button.click()
            print("Form submitted")
            
            # Wait for the submission to process
            time.sleep(5)
            
            # Try to extract anime ID from the resulting page
            anime_id = extract_anime_id_from_page(driver)
            if anime_id:
                save_anime_id_to_file(anime_id, json_file_path)
                print(f"✓ Anime ID {anime_id} saved for staff processing")
            else:
                print("⚠ Warning: Could not extract anime ID")
        else:
            print("Form was not submitted. Use --submit flag to submit the form automatically.")
        
        # Wait a bit to see the results
        print(f"All fields have been filled. Waiting {args.wait_time} seconds before continuing...")
        time.sleep(args.wait_time)

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Uncomment to close the browser when done
    # driver.quit()
    print("Script completed.")