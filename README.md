# Récupérer les infos du site

python .\combined_script.py -o anime_infos.json --no-headless "Yu-Gi-Oh! Card Game The Chronicles"
python .\fill_form_combined.py anime_infos.json 


# Run complete automation for a directory
python run_anime_automation.py spring_anime

# Run with auto-submit for staff entries
python run_anime_automation.py spring_anime --staff-auto-submit

# Skip staff addition
python run_anime_automation.py spring_anime --no-staff

# Process single file
python run_anime_automation.py spring_anime/Uchuujin_MuuMuu.json
 
