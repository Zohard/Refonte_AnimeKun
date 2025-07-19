from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import json
import time
import argparse
import sys

# Role mapping dictionary: maps roles from JSON to roles in the form
ROLE_MAPPING = {
    # Director/Réalisateur roles
    "Director": "Réalisation",
    "Réalisateur": "Réalisation",
    "Chief Director": "Directeur exécutif",
    "Assistant Director": "Assistance à la réalisation",
    "Episode Director": "Directeur d'épisode",
    "Series Director": "Supervision",
    
    # Producer/Production roles
    "Producer": "Producteur (staff)",
    "Production": "Production",
    "Executive Producer": "Producteur délégué",
    "Line Producer": "Producteur exécutif",
    "Production Manager": "Production manager",
    
    # Animation roles
    "Animation": "Animation",
    "Key Animation": "Animation clé",
    "Animateur clé": "Animation clé",
    "Chef animateur": "Chef animateur",
    "Chief animator": "Chef animateur",
    "Animation Director": "Directeur de l'animation",
    "In-Between Animation": "Intervaliste",
    "CGI Director": "Réalisateur 3D",
    "3D Director": "Réalisateur 3D",
    "CG Director": "Réalisateur 3D",
    "CGI": "CGI",
    "Animation CGI": "Animation CGI",
    "3D Animation": "Animation CGI",
    
    # Design roles
    "Character Design": "Chara-design",
    "Character designer": "Chara-design",
    "Chara-Design": "Chara-design",
    "Original Character Design": "Chara-design original",
    "Original character designer": "Chara-design original",
    "Art Design": "Art design",
    "Design Work": "Design work",
    "Mecha Design": "Mecha-design",
    "Monster Design": "Monster-design",
    "Prop Design": "Prop-design",
    "Set Design": "Set design",
    "Scene Design": "Scene-design",
    "Background": "Décors",
    "Décors": "Décors",
    "Chargé des décors": "Décors",
    "Layout": "Layout",
    "Color Design": "Couleurs",
    "Couleurs": "Couleurs",
    "Color design": "Couleurs",
    "Colors": "Couleurs",
    "Title Design": "Title Design",
    
    # Sound/Music roles
    "Sound Director": "Directeur du son",
    "Directeur du son": "Directeur du son",
    "Music": "Musique",
    "Musique": "Musique",
    "Composer": "Musique",
    "Sound Production": "Production du son",
    "Music Production": "Production de la musique",
    
    # Story roles
    "Original creator": "Auteur",
    "Créateur original": "Créateur original",
    "Original Work": "Auteur",
    "Scenario": "Scénario",
    "Scénariste": "Scénario",
    "Screenplay": "Scénario",
    "Script": "Script",
    "Series Composition": "Composition de la série",
    "Story": "Scénario",
    "Original Story": "Idée originale",
    "Concept original": "Idée originale",
    "Original Concept": "Idée originale",
    "Planning": "Planning",
    "Storyboard": "Storyboard",
    
    # Technical roles
    "Art Director": "Directeur artistique",
    "Directeur artistique": "Directeur artistique",
    "Photography Director": "Directeur de la photographie",
    "Directeur de la photo": "Directeur de la photographie",
    "FX Production": "Effets spéciaux",
    "VFX Supervisor": "Effets spéciaux",
    "FX": "Effets spéciaux",
    "Special Effects": "Effets spéciaux",
    "Effets spéciaux": "Effets spéciaux",
    "Editing": "Montage",
    "Montage": "Montage",
    "Editor": "Montage",
    
    # Studio roles
    "Studio": "Studio d'animation",
    "Animation Studio": "Studio d'animation",
    "Animation Production": "Studio d'animation",
    "Animation Assistance": "Studio d'animation (sous-traitance)",
    
    # Other roles
    "Supervision": "Supervision",
    "Illustrations originales": "Illustrations originales",
    "Original Arts": "Illustrations originales",
    "Original Illustrations": "Illustrations originales",
    "Distribution": "Distribution",
    "Broadcaster": "Diffuseur",
    "Diffuseur": "Diffuseur",
    "Motion Design": "Motion Design"
}

class TagSelector:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # Tag mapping based on your actual HTML structure
        self.tag_mapping = {
            # === GENRES (from your HTML) ===
            "Action": {"id": "t_9", "name": "action"},
            "Aventure": {"id": "t_10", "name": "aventure"},
            "Adventure": {"id": "t_10", "name": "aventure"},
            "Comédie": {"id": "t_15", "name": "comédie"},
            "Comedy": {"id": "t_15", "name": "comédie"},
            "Drame": {"id": "t_11", "name": "drame"},
            "Drama": {"id": "t_11", "name": "drame"},
            "Ecchi": {"id": "t_77", "name": "ecchi"},
            "Guerre": {"id": "t_16", "name": "guerre"},
            "War": {"id": "t_16", "name": "guerre"},
            "Historique": {"id": "t_38", "name": "historique"},
            "Historical": {"id": "t_38", "name": "historique"},
            "Horreur": {"id": "t_19", "name": "horreur"},
            "Horreur / Épouvante": {"id": "t_19", "name": "horreur"},
            "Horror": {"id": "t_19", "name": "horreur"},
            "Policier": {"id": "t_14", "name": "policier"},
            "Psychologique": {"id": "t_18", "name": "psychologique"},
            "Psychological": {"id": "t_18", "name": "psychologique"},
            "Romance": {"id": "t_13", "name": "romance"},
            "Sport": {"id": "t_17", "name": "sport"},
            "Sports": {"id": "t_17", "name": "sport"},
            "Thriller": {"id": "t_12", "name": "thriller"},
            "Slice of Life": {"id": "t_45", "name": "tranches de vie"},
            "Slice of life": {"id": "t_45", "name": "tranches de vie"},
            "Western": {"id": "t_112", "name": "western"},
            "Jeux vidéo": {"id": "t_72", "name": "jeu vidéo"},
            
            # === CLASSIFICATION ===
            "Josei": {"id": "t_85", "name": "josei"},
            "Kodomo": {"id": "t_8", "name": "kodomo"},
            "Seinen": {"id": "t_5", "name": "seinen"},
            "Shôjo": {"id": "t_3", "name": "shôjo"},
            "Shoujo": {"id": "t_3", "name": "shôjo"},
            "Shônen": {"id": "t_1", "name": "shônen"},
            "Shounen": {"id": "t_1", "name": "shônen"},
            "Yaoi": {"id": "t_7", "name": "yaoi"},
            "Yuri": {"id": "t_6", "name": "yuri"},
            
            # === UNIVERS ===
            "Cyberpunk": {"id": "t_41", "name": "cyberpunk"},
            "Fantastique": {"id": "t_37", "name": "fantastique"},
            "Fantasy": {"id": "t_35", "name": "fantasy"},
            "Gothique": {"id": "t_111", "name": "gothique"},
            "Post-apocalyptique": {"id": "t_39", "name": "post-apocalyptique"},
            "Réaliste": {"id": "t_34", "name": "réaliste"},
            "Science-fiction": {"id": "t_36", "name": "sci-fi"},
            "Sci-Fi": {"id": "t_36", "name": "sci-fi"},
            "Space opera": {"id": "t_22", "name": "space opera"},
            "Space Opera": {"id": "t_22", "name": "space opera"},
            "Steampunk": {"id": "t_40", "name": "steampunk"},
            "Surréaliste": {"id": "t_133", "name": "surréaliste"},
            
            # === ÉPOQUE ET LIEU ===
            "École": {"id": "t_33", "name": "école"},
            "Ecole": {"id": "t_33", "name": "école"},
            "School": {"id": "t_33", "name": "école"},
            "School Life": {"id": "t_33", "name": "école"},
            "Époque Edo": {"id": "t_43", "name": "époque Edo"},
            "Ère Taishō": {"id": "t_188", "name": "ère Taishō"},
            "Meiji": {"id": "t_167", "name": "meiji"},
            "Monde parallèle": {"id": "t_121", "name": "monde parallèle"},
            "Univers alternatif": {"id": "t_121", "name": "monde parallèle"},
            "Moyen Age": {"id": "t_44", "name": "Moyen Age"},
            "Prison": {"id": "t_145", "name": "prison"},
            "Seconde guerre mondiale": {"id": "t_42", "name": "seconde guerre mondiale"},
            
            # === SOUS-GENRE ===
            "Arts martiaux": {"id": "t_31", "name": "arts martiaux"},
            "Combat": {"id": "t_20", "name": "combat"},
            "Combats": {"id": "t_20", "name": "combat"},
            "Harem": {"id": "t_26", "name": "harem"},
            "Isekai": {"id": "t_186", "name": "isekai"},
            "Magical girl": {"id": "t_24", "name": "magical girl"},
            "Mahou Shoujo": {"id": "t_24", "name": "magical girl"},
            "Magie": {"id": "t_25", "name": "magie"},
            "Magic": {"id": "t_25", "name": "magie"},
            "Mecha": {"id": "t_23", "name": "mecha"},
            "Mechas": {"id": "t_23", "name": "mecha"},
            "Mystère": {"id": "t_104", "name": "mystère"},
            "Mystery": {"id": "t_104", "name": "mystère"},
            "Parodie": {"id": "t_30", "name": "parodie"},
            "Super-pouvoirs": {"id": "t_32", "name": "super-pouvoirs"},
            "Surnaturel": {"id": "t_80", "name": "surnaturel"},
            "Supernatural": {"id": "t_80", "name": "surnaturel"},
            "Voyage temporel": {"id": "t_158", "name": "voyage temporel"},
            "Time Travel": {"id": "t_158", "name": "voyage temporel"},
            
            # === PERSONNAGES ===
            "Aliens / Extra-terrestres": {"id": "t_102", "name": "extra-terrestre"},
            "Extra-terrestre": {"id": "t_102", "name": "extra-terrestre"},
            "Ange": {"id": "t_88", "name": "ange"},
            "Animal": {"id": "t_114", "name": "animal"},
            "Assassin": {"id": "t_179", "name": "assassin"},
            "Catgirl": {"id": "t_98", "name": "catgirl"},
            "Chasseur de prime": {"id": "t_49", "name": "chasseur de prime"},
            "Cyborg": {"id": "t_53", "name": "cyborg"},
            "Démon": {"id": "t_56", "name": "démon"},
            "Démons": {"id": "t_56", "name": "démon"},
            "Détective": {"id": "t_134", "name": "détective"},
            "Dieu/déesse": {"id": "t_78", "name": "dieu/déesse"},
            "Enfant": {"id": "t_119", "name": "enfant"},
            "Espion": {"id": "t_182", "name": "espion"},
            "Fantôme": {"id": "t_107", "name": "fantôme"},
            "Fantômes": {"id": "t_107", "name": "fantôme"},
            "Guerrier": {"id": "t_108", "name": "guerrier"},
            "Idol": {"id": "t_175", "name": "idol"},
            "Idols": {"id": "t_175", "name": "idol"},
            "Magicien": {"id": "t_52", "name": "magicien"},
            "Militaire": {"id": "t_93", "name": "militaire"},
            "Monstre": {"id": "t_110", "name": "monstre"},
            "Monstres": {"id": "t_110", "name": "monstre"},
            "Ninja": {"id": "t_89", "name": "ninja"},
            "Pirate": {"id": "t_87", "name": "pirate"},
            "Robot": {"id": "t_92", "name": "robot"},
            "Robots": {"id": "t_92", "name": "robot"},
            "Samouraï": {"id": "t_51", "name": "samouraï"},
            "Samouraïs": {"id": "t_51", "name": "samouraï"},
            "Sorcière": {"id": "t_127", "name": "sorcière"},
            "Super-héros": {"id": "t_101", "name": "super-héros"},
            "Vampire": {"id": "t_55", "name": "vampire"},
            "Vampires": {"id": "t_55", "name": "vampire"},
            "Yakuza": {"id": "t_100", "name": "yakuza"},
            "Yōkai": {"id": "t_168", "name": "yôkai"},
            "Zombie": {"id": "t_170", "name": "zombie"},
            "Zombies": {"id": "t_170", "name": "zombie"},
            
            # === ACTIVITÉS ===
            "Cosplay": {"id": "t_74", "name": "cosplay"},
            "Cuisine": {"id": "t_105", "name": "cuisine"},
            "Gastronomie": {"id": "t_105", "name": "cuisine"},
            "Musique": {"id": "t_73", "name": "musique"},
            "Music": {"id": "t_73", "name": "musique"},
            
            # === ARCHÉTYPE ===
            "Otaku": {"id": "t_59", "name": "otaku"},
            "Otaku Culture": {"id": "t_59", "name": "otaku"},
            
            # === ÉLEMENT NARRATIF/THÈME ===
            "Compétition": {"id": "t_128", "name": "compétition"},
            "Religion": {"id": "t_150", "name": "religion"},
            "Triangle amoureux": {"id": "t_27", "name": "triangle amoureux"},
            "Vengeance": {"id": "t_148", "name": "vengeance"},
            "Violence": {"id": "t_126", "name": "violence"},
            
            # === MOTS-CLÉ DIVERS ===
            "Moe": {"id": "t_165", "name": "moe"},
            "Mythologie": {"id": "t_172", "name": "mythologie"},
            "Transformation": {"id": "t_194", "name": "transformation"},
            
            # === SPECIAL MAPPINGS FOR YOUR DATA ===
            "Adolescence": {"id": "t_45", "name": "tranches de vie"},  # Life themes
            "Amour": {"id": "t_13", "name": "romance"},
            "Couture": {"id": "t_45", "name": "tranches de vie"},  # Lifestyle
            "Dystopie": {"id": "t_39", "name": "post-apocalyptique"},  # Often overlaps
        }
    
    def wait_for_page_load(self):
        """Wait for the tag elements to be present on the page"""
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "t_1")))
            print("✓ Page with tags loaded successfully")
            return True
        except TimeoutException:
            print("✗ Timeout waiting for tags to load")
            return False
    
    def find_tag_element(self, tag_id):
        """Find a tag element by ID"""
        try:
            element = self.driver.find_element(By.ID, tag_id)
            return element
        except NoSuchElementException:
            return None
    
    def is_tag_selected(self, element):
        """Check if a tag is already selected - FIXED LOGIC"""
        try:
            classes = element.get_attribute("class") or ""
            # FIXED: Check for "selected" class and NOT "notselected"
            return "selected" in classes and "notselected" not in classes
        except:
            return False
    
    def click_tag(self, element, tag_name, original_term):
        """Click on a tag element with verification"""
        try:
            # Scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            
            # Check if already selected
            if self.is_tag_selected(element):
                print(f"  ⚠ Tag '{tag_name}' already selected for '{original_term}'")
                return True
            
            # Log the current state
            current_classes = element.get_attribute("class") or ""
            print(f"  🎯 Clicking tag '{tag_name}' for '{original_term}' (current classes: '{current_classes}')")
            
            # Try clicking
            element.click()
            time.sleep(0.5)
            
            # Verify the click worked
            updated_classes = element.get_attribute("class") or ""
            if self.is_tag_selected(element):
                print(f"  ✓ Successfully selected '{tag_name}' for '{original_term}' (new classes: '{updated_classes}')")
                return True
            else:
                print(f"  ⚠ Click may have failed for '{tag_name}' ('{original_term}') - classes: '{updated_classes}'")
                return False
                
        except Exception as e:
            print(f"  ✗ Error clicking tag '{tag_name}' for '{original_term}': {e}")
            return False
    
    def debug_available_tags(self):
        """Debug function to show what tags are available on the page"""
        print("\n=== DEBUG: Available tags on page ===")
        try:
            tag_elements = self.driver.find_elements(By.CSS_SELECTOR, "[id^='t_']")
            print(f"Found {len(tag_elements)} potential tag elements")
            
            # Show first few with their current selection status
            for element in tag_elements[:10]:
                tag_id = element.get_attribute("id")
                tag_text = element.text[:30] if element.text else "No text"
                tag_classes = element.get_attribute("class") or "No classes"
                is_selected = self.is_tag_selected(element)
                print(f"  ID: {tag_id}, Text: '{tag_text}', Classes: '{tag_classes}', Selected: {is_selected}")
                
        except Exception as e:
            print(f"Error during debug: {e}")
        print("=== END DEBUG ===\n")
    
    def select_tags(self, terms_list, category_name="tags"):
        """Select tags based on a list of terms"""
        if not terms_list:
            print(f"No {category_name} provided")
            return
        
        print(f"\n=== Processing {len(terms_list)} {category_name} ===")
        print(f"{category_name.capitalize()}: {terms_list}")
        
        # Debug: show available tags for first few terms
        if len(terms_list) > 0:
            self.debug_available_tags()
        
        successful = 0
        failed = []
        
        for term in terms_list:
            print(f"\nProcessing {category_name[:-1]}: '{term}'")
            
            if term in self.tag_mapping:
                tag_info = self.tag_mapping[term]
                tag_id = tag_info["id"]
                tag_name = tag_info["name"]
                
                element = self.find_tag_element(tag_id)
                if element:
                    if self.click_tag(element, tag_name, term):
                        successful += 1
                    else:
                        failed.append(term)
                else:
                    print(f"  ✗ Element with ID '{tag_id}' not found")
                    failed.append(term)
            else:
                print(f"  ⚠ '{term}' not found in mapping")
                failed.append(term)
        
        # Summary
        print(f"\n{category_name.capitalize()} selection summary:")
        print(f"  ✓ Successfully selected: {successful}")
        print(f"  ✗ Failed to select: {len(failed)}")
        
        if failed:
            print(f"  Failed {category_name}: {failed}")
        
        return successful, failed


def load_json_data(file_path):
    """Load JSON data from file"""
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
            print("Successfully logged in")
            return True
        else:
            print("Login might have failed")
            return False
    
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return False


def extract_genres_and_themes(anime_data):
    """Extract genres and themes from various possible locations in JSON"""
    genres = []
    themes = []
    
    # Extract genres
    if "genres" in anime_data:
        genres = anime_data["genres"]
        print(f"Found genres in top-level: {genres}")
    elif "sources" in anime_data:
        if "myanimelist" in anime_data["sources"] and "genres" in anime_data["sources"]["myanimelist"]:
            genres = anime_data["sources"]["myanimelist"]["genres"]
            print(f"Found genres in MyAnimeList source: {genres}")
        elif "nautiljon" in anime_data["sources"] and "genres" in anime_data["sources"]["nautiljon"]:
            genres = anime_data["sources"]["nautiljon"]["genres"]
            print(f"Found genres in Nautiljon source: {genres}")
    
    # Extract themes
    if "themes" in anime_data:
        themes = anime_data["themes"]
        print(f"Found themes in top-level: {themes}")
    elif "sources" in anime_data:
        if "myanimelist" in anime_data["sources"] and "themes" in anime_data["sources"]["myanimelist"]:
            themes.extend(anime_data["sources"]["myanimelist"]["themes"])
        if "nautiljon" in anime_data["sources"] and "themes" in anime_data["sources"]["nautiljon"]:
            themes.extend(anime_data["sources"]["nautiljon"]["themes"])
        
        themes = list(dict.fromkeys(themes))
        print(f"Found combined themes: {themes}")
    
    return genres, themes


def process_genres_and_themes(driver, anime_data, anime_id):
    """Process and apply both genres and themes to the anime"""
    print("\n" + "="*60)
    print("PROCESSING GENRES AND THEMES")
    print("="*60)
    
    # Navigate to the modification page
    modification_url = f"http://www.anime-kun.net/__zone-admin__/anime.php?page=Modification&id_fiche={anime_id}"
    driver.get(modification_url)
    print(f"Navigated to modification page for anime ID: {anime_id}")
    
    # Initialize tag selector
    tag_selector = TagSelector(driver)
    
    # Wait for page to load
    if not tag_selector.wait_for_page_load():
        print("Failed to load page with tags")
        return False
    
    # Extract genres and themes
    genres, themes = extract_genres_and_themes(anime_data)
    
    # Process genres
    if genres:
        successful_genres, failed_genres = tag_selector.select_tags(genres, "genres")
    else:
        print("No genres found to process")
        successful_genres, failed_genres = 0, []
    
    # Process themes
    if themes:
        successful_themes, failed_themes = tag_selector.select_tags(themes, "themes")
    else:
        print("No themes found to process")
        successful_themes, failed_themes = 0, []
    
    print(f"\n✓ Genre and theme processing completed")
    print(f"   Genres: {successful_genres} successful, {len(failed_genres)} failed")
    print(f"   Themes: {successful_themes} successful, {len(failed_themes)} failed")
    
    return True


def extract_staff_info(anime_data):
    """Extract staff information from JSON data"""
    staff_list = []
    
    if "staff" in anime_data:
        staff_list.extend(anime_data["staff"])
    
    if "sources" in anime_data:
        if "myanimelist" in anime_data["sources"] and "staff" in anime_data["sources"]["myanimelist"]:
            staff_list.extend(anime_data["sources"]["myanimelist"]["staff"])
        if "nautiljon" in anime_data["sources"] and "staff" in anime_data["sources"]["nautiljon"]:
            staff_list.extend(anime_data["sources"]["nautiljon"]["staff"])
    
    # Add studios
    studios = []
    if "studios" in anime_data and anime_data["studios"]:
        studios.extend(anime_data["studios"])
    
    if "sources" in anime_data:
        if "myanimelist" in anime_data["sources"] and "studios" in anime_data["sources"]["myanimelist"]:
            studios.extend(anime_data["sources"]["myanimelist"]["studios"])
        if "nautiljon" in anime_data["sources"] and "studio" in anime_data["sources"]["nautiljon"]:
            studio = anime_data["sources"]["nautiljon"]["studio"]
            if studio:
                studios.append(studio)
    
    for studio in studios:
        staff_list.append({
            "name": studio,
            "role": "Studio d'animation"
        })
    
    # Normalize staff info
    normalized_staff = []
    seen_entries = set()
    
    for staff_member in staff_list:
        if not staff_member.get("name") or not staff_member.get("role"):
            continue
        
        name = staff_member["name"].replace(",", "").strip()
        role = staff_member["role"].strip()
        mapped_role = ROLE_MAPPING.get(role, role)
        
        unique_key = f"{name.lower()}|{mapped_role.lower()}"
        
        if unique_key not in seen_entries:
            normalized_staff.append({
                "name": name,
                "role": mapped_role
            })
            seen_entries.add(unique_key)
    
    return normalized_staff


def add_staff_member(driver, name, role, wait, auto_submit=False):
    """Add a staff member"""
    try:
        business_field = wait.until(EC.presence_of_element_located((By.ID, "name_business")))
        business_field.clear()
        business_field.send_keys(name)
        print(f"Searching for staff member: {name}")
        
        time.sleep(2)
        
        try:
            autocomplete_items = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ul.ui-autocomplete li.ui-menu-item")
            ))
            autocomplete_items.click()
            print(f"Selected autocomplete result for: {name}")
        except (TimeoutException, NoSuchElementException):
            print(f"No autocomplete results found for {name}, may need to create this business entry")
            business_field.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        custom_field = wait.until(EC.presence_of_element_located((By.ID, "custom")))
        custom_field.clear()
        custom_field.send_keys(role)
        print(f"Entered role: {role}")
        
        time.sleep(2)
        
        try:
            function_box = wait.until(EC.presence_of_element_located((By.ID, "fonction_box")))
            
            if function_box.is_displayed():
                role_options = function_box.find_elements(By.TAG_NAME, "a")
                selected = False
                
                for option in role_options:
                    if option.text.lower() == role.lower():
                        option.click()
                        selected = True
                        print(f"Selected exact role match: {role}")
                        break
                
                if not selected and role_options:
                    role_options[0].click()
                    print(f"Selected first role option: {role_options[0].text}")
            else:
                print("Role autocomplete not displayed, continuing with entered role")
        except (TimeoutException, NoSuchElementException):
            print(f"No role autocomplete results found for {role}, continuing with entered role")
        
        id_business_field = wait.until(EC.presence_of_element_located((By.ID, "id_business")))
        id_value = id_business_field.get_attribute("value")
        
        if not id_value or id_value.strip() == "":
            print(f"Warning: No business ID found for {name}")
            return False
        
        if auto_submit:
            submit_button = driver.find_element(By.XPATH, "//form[@id='ajout_staff']//input[@type='submit']")
            submit_button.click()
            print(f"Submitted staff entry for {name} with role {role}")
            time.sleep(2)
        else:
            print(f"Ready to submit staff entry for {name} with role {role}")
            print("Please review and manually submit the form.")
            input("Press Enter to continue to the next staff member...")
        
        return True
    
    except Exception as e:
        print(f"Error adding staff member {name} with role {role}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Add staff and genres to anime on anime-kun.net')
    parser.add_argument('json_file', help='Path to the JSON file containing anime data')
    parser.add_argument('--anime-id', required=True, help='ID of the anime on anime-kun.net')
    parser.add_argument('--username', default="******", help='Username for login (default: test)')
    parser.add_argument('--password', default="******", help='Password for login (default: test)')
    parser.add_argument('--auto-submit', action='store_true', help='Automatically submit each staff entry')
    parser.add_argument('--wait-time', type=int, default=5, help='Time in seconds to wait between actions (default: 5)')
    parser.add_argument('--skip-genres', action='store_true', help='Skip genre processing and go directly to staff')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with extra logging')
    parser.add_argument('--tags-only', action='store_true', help='Only process tags, skip staff completely')
    
    args = parser.parse_args()
    
    # Load JSON data
    anime_data = load_json_data(args.json_file)
    if not anime_data:
        print(f"Failed to load JSON data from {args.json_file}. Exiting script.")
        sys.exit(1)
    
    # Extract staff information
    staff_list = extract_staff_info(anime_data)
    
    if not staff_list and not args.tags_only:
        print("No staff information found in the JSON data. Will only process genres/themes.")
    elif args.tags_only:
        print("Tags-only mode: Will only process genres and themes.")
    else:
        print(f"Found {len(staff_list)} staff members to add")
    
    # Initialize webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if not args.debug:
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Login
        login_success = login_to_site(driver, args.username, args.password)
        if not login_success:
            print("Could not verify successful login. Continuing anyway...")
        
        # Process genres and themes (unless skipped)
        if not args.skip_genres:
            success = process_genres_and_themes(driver, anime_data, args.anime_id)
            if not success:
                print("Genre/theme processing failed, but continuing...")
        
        # Process staff if available and not tags-only mode
        if staff_list and not args.tags_only:
            print("\n" + "="*60)
            print("PROCESSING STAFF")
            print("="*60)
            
            staff_url = f"http://www.anime-kun.net/__zone-admin__/anime.php?page=Modification2&id_fiche={args.anime_id}"
            driver.get(staff_url)
            print(f"Navigated to staff management page for anime ID: {args.anime_id}")
            
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "name_business")))
            print("Staff management form loaded successfully")
            
            successful_additions = 0
            for i, staff_member in enumerate(staff_list):
                print(f"\nProcessing staff member {i+1}/{len(staff_list)}: {staff_member['name']} - {staff_member['role']}")
                
                success = add_staff_member(
                    driver=driver,
                    name=staff_member["name"],
                    role=staff_member["role"],
                    wait=wait,
                    auto_submit=args.auto_submit
                )
                
                if success:
                    successful_additions += 1
                
                time.sleep(args.wait_time)
            
            print(f"\nCompleted processing {len(staff_list)} staff members")
            print(f"Successfully added: {successful_additions}")
            print(f"Failed: {len(staff_list) - successful_additions}")
        
        print("\n" + "="*60)
        print("SCRIPT COMPLETED")
        print("="*60)
        
        if not args.auto_submit or args.debug:
            print("You can review the changes in the browser before closing.")
            input("Press Enter to close the browser...")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if args.debug:
            print("DEBUG MODE: Keeping browser open for inspection...")
            input("Press Enter to close browser...")
        # Uncomment to auto-close browser
        # driver.quit()
        print("Script completed.")


if __name__ == "__main__":
    main()