from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import getpass  # Import getpass for secure password input
import os
import sys
from datetime import datetime
from selenium.common.exceptions import StaleElementReferenceException

# Add this code right after the imports
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"{timestamp}_tbAppPinpon.txt")

class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
    def flush(self):
        for f in self.files:
            f.flush()

original_stdout = sys.stdout
original_stderr = sys.stderr

log_fd = open(log_file, "w", encoding="utf-8")
sys.stdout = Tee(sys.stdout, log_fd)
sys.stderr = Tee(sys.stderr, log_fd)

# Function to access the site and manage cookie settings
def accessSite(driver):
    # Click the 'Configuración de cookies' button
    try:
        config_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Configuración de cookies')]")
        config_button.click()
        time.sleep(5)  # Wait for the cookie settings to load
    except Exception as e:
        print("Error clicking 'Configuración de cookies':", e)

    # Click the 'Rechazarlas todas' button
    try:
        reject_all_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Rechazarlas todas')]")
        reject_all_button.click()
    except Exception as e:
        print("Error clicking 'Rechazarlas todas':", e)

# Function to get user credentials
def get_user_credentials():
    email = input("Please enter your email: ")
    password = getpass.getpass("Please enter your password: ")  # Masked password input
    return email, password

# Function to log in to the site
def login(driver, email, password):
    # Click the 'INICIAR SESIÓN' button located next to the 'Regístrate' button
    try:
        # Locate the 'Regístrate' button
        register_button = driver.find_element(By.XPATH, "//button[@data-test='signUp' and contains(., 'Regístrate')]")
        
        # Find the 'INICIAR SESIÓN' button next to it
        login_button = driver.find_element(By.XPATH, "//button[@data-test='login' and contains(., 'Iniciar sesión')]")
        
        # Click the 'INICIAR SESIÓN' button
        login_button.click()
        time.sleep(5)  # Wait for the login form to load

    except Exception as e:
        print("Error clicking 'INICIAR SESIÓN':", e)

    # Fill in the email and password
    try:
        email_input = driver.find_element(By.XPATH, "//input[@placeholder='Correo electrónico']")
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='Contraseña']")
        
        email_input.send_keys(email)
        password_input.send_keys(password)

        # Click the submit button to log in
        submit_button = driver.find_element(By.XPATH, "//button[@data-test='submitLogin' and contains(., 'Iniciar sesión')]")
        submit_button.click()
    except Exception as e:
        print("Error filling in credentials or logging in:", e)

# Function to check the balance
def check_balance(driver):
    while True:
        try:
            time.sleep(3)
            # Locate the balance element
            balance_element = driver.find_element(By.XPATH, "//div[contains(@class, 'customer-balance-module_text')]")
            balance_text = balance_element.text.strip()  # Get the text and strip any whitespace
            balance_value = int(balance_text.replace('$', '').replace(',', '').strip())  # Convert to integer
            
            if balance_value > 3500:
                print(f"Balance is {balance_value}. Proceeding to place bets...")
                return balance_value  # Return the balance value for further use
            else:
                print("Balance is insufficient. Waiting for balance update...")
                time.sleep(5)  # Wait and retry balance check

        except Exception as e:
            print("Error checking balance:", e)
            time.sleep(5)

def remove_betslip_2(driver):
    # Locate all coupon bet events
    coupon_bet_events = driver.find_elements(By.XPATH, "//div[@data-test='couponBetEvent']")
    
    if not coupon_bet_events:
        print("No coupon bet events found to remove.")
        return  # Exit the function if there are no events

    for event in coupon_bet_events:
        try:
            # Click the associated remove button
            remove_button = event.find_element(By.XPATH, ".//div[contains(@class, 'coupon-bet-remove-module_Holder')]")
            remove_button.click()
            print("Removed events before betting.")
        except Exception as e:
            # If the status element is not found, continue to the next event
            print(f"Error clicking remove button for event: {e}")
            continue


def remove_betslip(driver):
    # Click the 'Borrar resultado' button if it exists
    while True:
        try:
            borrar_resultado_button = driver.find_element(By.XPATH, "//button[@data-test='betslip-remove-stopped-events' and contains(., 'Borrar resultado')]")
            borrar_resultado_button.click()
            print("Clicked 'Borrar resultado' button.")
            time.sleep(1)  # Wait a moment after clicking
        except Exception as e:
            print("No more 'Borrar resultado' buttons to click.")
            break  # Exit the loop if the button is not found
    # Locate all coupon bet events
    coupon_bet_events = driver.find_elements(By.XPATH, "//div[@data-test='couponBetEvent']")
    
    for event in coupon_bet_events:
        try:
            # Check for the status element indicating "pausa" or "pause"
            status_element = event.find_element(By.XPATH, ".//div[contains(@class, 'coupon-bet-status-module_TextWarning')]")
            status_text = status_element.text.strip().lower()  # Get the text and convert to lower case
            
            if "pausa" in status_text or "pause" in status_text:
                print("Found paused event, removing from betslip...")
                # Click the associated remove button
                remove_button = event.find_element(By.XPATH, ".//div[contains(@class, 'coupon-bet-remove-module_Holder')]")
                remove_button.click()
                print("Clicked remove button for paused event.")
        except Exception as e:
            # If the status element is not found, continue to the next event
            continue
        
def set_bet_amount(driver):
    """Clear the bet input field and set a new bet amount."""
    bet_input = driver.find_element(By.XPATH, "//input[@data-test='betslip-amount']")
    bet_input.clear()  # Clear any existing value
    amount = 500
    #amount = str(amount_value)
    bet_input.send_keys(amount)  # Set the value to the specified amount
    print(f"Bet amount set to: {amount}")
    return amount

def check_bet_amount(driver, amount):
    """Check if the possible win amount is sufficient to place the bet."""
    try:
        # Locate the possible win amount element
        possible_win_element = driver.find_element(By.XPATH, "//span[@data-test='betslip-possible-win-amount']")
        possible_win_text = possible_win_element.text.strip()
        possible_win_amount = float(possible_win_text)  # Convert to float

        # Check the difference
        if possible_win_amount - amount >= 15:
            print(f"Possible win amount ({possible_win_amount}) is sufficient compared to input amount ({amount}).")
            return True  # Sufficient amount to place the bet
        else:
            print(f"Possible win amount ({possible_win_amount}) is not sufficient compared to input amount ({amount}).")
            return False  # Not sufficient to place the bet

    except Exception as e:
        print("Error checking bet amount:", e)
        return False  # Return false if there's an error


def place_bet_and_check_errors(driver, button, selected_outcome_buttons, amount, placed_bet):
    """Click the 'Apostar' button and check for error messages."""
    
    def click_with_retry(element, retries=3):
        """Attempt to click an element with a specified number of retries."""
        for attempt in range(retries):
            try:
                element.click()
                return True  # Click successful
            except Exception as e:
                print(f"Click failed on attempt {attempt + 1}: {e}")
                time.sleep(1)  # Wait before retrying
        return False  # Click failed after retries

    if not check_bet_amount(driver, amount):
        # Unclick the selected outcome buttons if the bet amount is not sufficient
        button.click()  # This assumes clicking again will unselect it
        placed_bet = False
        print("Unclicked selected outcome button due to insufficient bet amount.")
        return False  # Exit the function if the bet cannot be placed

    # Locate the 'Apostar' button
    apostar_button = driver.find_element(By.XPATH, "//button[@data-test='betslip-place-bet']//span[contains(text(), 'Apostar')]")
    
    # Attempt to click the 'Apostar' button with retries
    if not click_with_retry(apostar_button):
        print("Failed to click 'Apostar' button after multiple attempts.")
        placed_bet = False
        return False  # Exit if the button could not be clicked

    placed_bet = True

    # Loop to check for the error message
    for _ in range(2):  # Loop for 4 seconds
        time.sleep(0.5)  # Wait for 1 second before checking
        try:
            # Check for the error message
            error_message = driver.find_element(By.XPATH, "//div[contains(@class, 'snackbar-module_Text__KmK6DrKF__platform-common')]")
            error_message_text = error_message.text.strip().lower()  # Get the text and convert to lower case
            if "invalid stake amount entered for current bet" in error_message_text or "algo salió mal" in error_message_text:
                print("Error message detected: Invalid stake amount entered for current bet.")
                
                # Unclick the selected outcome buttons
                button.click()  # This assumes clicking again will unselect it
                placed_bet = False
                print("Unclicked selected outcome button due to error.")
                return placed_bet  # Exit the function after handling the error
        except Exception:
            # If the error message is not found, continue checking
            print("Looking for after-bet errors")
            continue

    if placed_bet:
        print("Bet placed successfully.")
        
        # Print the scoreboard for each selected match
        try:
            # Find the event container for the button
            events_table = button.find_element(By.XPATH, ".//ancestor::div[@data-test='eventTableRow']")
            
            team_scores = events_table.find_elements(By.XPATH, ".//div[contains(@class, 'event-table-additional-results-module_base__ZlPakjl1__platform-common')]")
            set_team_scores = events_table.find_elements(By.XPATH, ".//div[@data-test='teamScore']")
            team_names = events_table.find_elements(By.XPATH, ".//div[@data-test='teamName']")

            
            print("Scoreboard:")
            for team_name, team_score, set_team_score in zip(team_names, team_scores, set_team_scores):
                print(f"Team Name: {team_name.text}, Team Score: {team_score.text}, Set: {set_team_score.text}")
            placed_bet = True

        except Exception as e:
            print("Error retrieving team names and scores:", e)

    time.sleep(1)  # Wait for 30 seconds after placing a bet
    return placed_bet


def check_and_adjust_outcome_buttons(driver, button, selected_outcome_buttons, placed_bet):
    """Validate all selected buttons' scores and values before placing bet"""
    valid_buttons = []
    time.sleep(1)
    if selected_outcome_buttons == True:
        try:
            texto = button.text.strip()
            print("SELECTED BUTTON: ", texto)
            # Get the specific row context for each button
            row = button.find_element(By.XPATH, ".//ancestor::div[@data-test='eventTableRow']")
            
            # Get current value check
            value_span = button.find_element(By.XPATH, ".//span")
            current_value = float(value_span.text.strip())
            

            # Get scores from THIS button's match context
            #team_scores = row.find_elements(By.XPATH, ".//div[contains(@class, 'event-table-additional-results-module_base__ZlPakjl1__platform-common')]")
            #team_set_scores = row.find_elements(By.XPATH, ".//div[@data-test='teamScore']")
            #team_names = row.find_elements(By.XPATH, ".//div[@data-test='teamName']")
            #score_dict = {name.text.strip(): int(score.text.strip()) 
            #            for name, score in zip(team_names, team_scores)}
            #set_score_dict = {name2.text.strip(): int(score2.text.strip())
            #                  for name2, score2 in zip(team_names, team_set_scores)}
            #print("Scoreboard:")
            #for team_name, team_score, set_team_score in zip(team_names, team_scores, team_set_scores):
            #    print(f"Team Name: {team_name.text}, Team Score: {team_score.text}, Set: {set_team_score.text}")

            # Get selected team for THIS button
            selected_team_name = define_sel_team(button, row)
            #selected_team_element = define_sel_team(button, row)
            #selected_team_name = selected_team_element.text.replace("Ganador:", "").strip()

            # Score validation for THIS button's match
            if current_value > 1.2: #or not check_selected_team_score(selected_team_name, score_dict, set_score_dict):
                wait = WebDriverWait(driver, 2)
                element = wait.until(EC.element_to_be_clickable(button))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                driver.execute_script("arguments[0].click();", element)
                print(f"Unclicked {selected_team_name} - insufficient lead and/or value {current_value}")
                placed_bet = False
                
                
            selected_outcome_buttons = True

        except Exception as e:
            print(f"Validation error for button: {str(e)}")
            
    return selected_outcome_buttons


def check_selected_team_score(selected_team_name, score_dict, set_score_dict):
    """Check if selected team is winning by 3+ points."""
    if selected_team_name in score_dict and selected_team_name in set_score_dict:
        selected_score = score_dict[selected_team_name]
        set_score = set_score_dict[selected_team_name]
        if selected_score > 4 and set_score == 2:
            opponent_scores = [score for name, score in score_dict.items() 
                         if name != selected_team_name]
            return any(selected_score - score >= 2 for score in opponent_scores)
    return False


def define_sel_team(button, row):
    """Match button position to corresponding team name using DOM order"""
    try:
        # Get all outcome buttons in the same market container
        market_container = button.find_element(By.XPATH, "./ancestor::div[@data-test='marketItem']")
        outcome_buttons = market_container.find_elements(By.XPATH, ".//div[@data-test='outcome']")
        
        # Get button index within its market container
        button_index = outcome_buttons.index(button)
        
        # Get team names from the same event row
        team_names = row.find_elements(By.XPATH, ".//div[@data-test='teamName']")
        
        # Validate index alignment
        if button_index >= len(team_names):
            print(f"Button index {button_index} exceeds team count {len(team_names)}")
            return None
            
        return team_names[button_index].text.strip()
        
    except ValueError:
        print("Button not found in market container")
        return None
    except Exception as e:
        print(f"Team definition error: {str(e)}")
        return None


# Function to place a bet
def place_bet(driver, button, selected_outcome_buttons, placed_bet):
    try:
        # Validate all buttons before placing bet
        selected_outcome_buttons = check_and_adjust_outcome_buttons(driver, button, selected_outcome_buttons, placed_bet)
        
        if not selected_outcome_buttons:
            print("No valid buttons remaining after final checks")
            return
        
        # Proceed with only validated buttons
        amount = set_bet_amount(driver)
        time.sleep(1)
        placed_bet = place_bet_and_check_errors(driver, button, selected_outcome_buttons, amount, placed_bet)
        
    except Exception as e:
        print(f"Error in place_bet: {str(e)}")

    return placed_bet



# New function to obtain button information
def button_info(driver, button, selected_outcome_buttons, row):
    value_span = button.find_element(By.XPATH, ".//span")
    value_text = value_span.text.strip()
    print(value_text)
    value = float(value_text)

    if value < 1.21:  # Adjusted condition to click buttons with value < 1.1
        events_table = button.find_element(By.XPATH, ".//ancestor::div[@data-test='eventsTable']")
        associated_image = events_table.find_element(By.XPATH, ".//img[@title='Sport']")
        associated_alt = associated_image.get_attribute("alt")

        # Print team names and scores
        #team_names = row.find_elements(By.XPATH, ".//div[@data-test='teamName']")
        #team_scores = row.find_elements(By.XPATH, ".//div[@data-test='teamScore']")
            
        #for team_name, team_score in zip(team_names, team_scores):
        #    print(f"Team Name: {team_name.text}, Team Score: {team_score.text}")

        # Find the league name from the corresponding 'a' tag
        league_name_element = events_table.find_element(By.XPATH, ".//a[@data-test='leagueLink']")  # Locate the league link
        league_name = league_name_element.text.strip()  # Get the league name text

        # Get the period text
        try:
            game_period = row.find_element(By.XPATH, ".//div[@data-test='eventPeriodAndScore']")
            period_text = game_period.text.strip()
            print(f"Game period text: {period_text}")  # Debugging statement
        except Exception as e:
            print("Error finding game period:", e)
            period_text = ""  # Set to empty if not found

        print(f"Associated alt value: {associated_alt}")  # Debugging statement
        print(f"League name: {league_name}")  # Debugging statement

        # Get scores from THIS button's match context
        team_scores = row.find_elements(By.XPATH, ".//div[contains(@class, 'event-table-additional-results-module_base__ZlPakjl1__platform-common')]")
        team_set_scores = row.find_elements(By.XPATH, ".//div[@data-test='teamScore']")
        team_names = row.find_elements(By.XPATH, ".//div[@data-test='teamName']")
        score_dict = {name.text.strip(): int(score.text.strip()) 
                    for name, score in zip(team_names, team_scores)}
        set_score_dict = {name2.text.strip(): int(score2.text.strip())
                            for name2, score2 in zip(team_names, team_set_scores)}
        print("Scoreboard:")
        for team_name, team_score, set_team_score in zip(team_names, team_scores, team_set_scores):
            print(f"Team Name: {team_name.text}, Team Score: {team_score.text}, Set: {set_team_score.text}")

        # Get selected team for THIS button
        selected_team_name = define_sel_team(button, row)

        if any(phrase.lower() in period_text.lower() for phrase in ["1er set", "2do set", "no iniciado", "primer", "segundo", "break"]) or not check_selected_team_score(selected_team_name, score_dict, set_score_dict):
                print(f"Skipping button click for league: {league_name} at timer: {period_text} because it's in the first or second set.")
                return  # Move on to the next case or iteration
            
        if any(phrase.lower() in period_text.lower() for phrase in ["3º set", "4º set", "5º set"]) and check_selected_team_score(selected_team_name, score_dict, set_score_dict):
            button.click()
            print(f"Button clicked for league: {league_name}")
            selected_outcome_buttons = True
            time.sleep(1)
        # Inside your main logic where you handle the sports
        #sport_case(driver, button, associated_alt, events_table, league_name, period_text, selected_outcome_buttons, row)
        return selected_outcome_buttons

# Function to select bets based on conditions
def bet_sel(driver):
    remove_betslip(driver)
    selected_outcome_buttons = False  # Array to store selected outcome buttons
    placed_bet = False
    #button_clicked = False  # Initialize a flag to track if any button was clicked
    # Locate all event table rows
    event_rows = driver.find_elements(By.XPATH, "//div[@data-test='eventTableRow']")
    if not event_rows:
        print("No event table rows found.")
        return selected_outcome_buttons  # Return the array

    for row in event_rows:
        try:
            # Find the first market item within the current event row
            market_item = row.find_element(By.XPATH, ".//div[@data-test='marketItem'][1]")  # Get the first market item
            # Find outcome buttons within the first market item
            outcome_buttons = market_item.find_elements(By.XPATH, ".//div[@data-test='outcome']")
            if not outcome_buttons:
                print("No outcome buttons found in the first market item.")
                continue  # Skip to the next row if no outcome buttons are found

            for button in outcome_buttons:
                try:
                    selected_outcome_buttons = False
                    selected_outcome_buttons = button_info(driver, button, selected_outcome_buttons, row)
                    if selected_outcome_buttons == True:
                        placed_bet = place_bet(driver, button, selected_outcome_buttons, placed_bet)
                    
                    time.sleep(0.5)  # Optional: wait a moment before checking again

                except Exception as e:
                    print(f"Error processing button:", e)
            
        except Exception as e:
            print(f"Error processing event row:", e)
    
    #for button in selected_outcome_buttons:
    #            try:
    #                check_outcome_buttons_score(driver, row, button, selected_outcome_buttons)
    #            except Exception as e:
    #                print(f"Error checking scores:", e)
    if placed_bet == True:
        time.sleep(300)
    elif placed_bet == False:
        time.sleep(1)

    return selected_outcome_buttons  # Return the array of selected outcome buttons

# Function to scrape the full website structure and save it to scraped.txt
def scrape_full_structure(url):
    options = Options()
    options.use_chromium = True
    service = Service(r'C:\Users\ignac\Downloads\msedgedriver.exe')  # Use raw string
    driver = webdriver.Edge(service=service, options=options)

    driver.get(url)

    # Maximize the browser window to full screen
    driver.maximize_window()  # Open the browser in full-screen mode

    # Wait for the page to load
    time.sleep(10)  # Adjust as necessary

    # Access the site and manage cookie settings
    accessSite(driver)

    # Get user credentials and log in
    email, password = get_user_credentials()
    login(driver, email, password)

    # Wait for 20 seconds to allow JavaScript to load content
    time.sleep(10)

    return driver  # Return the driver for further use


def open_bets(driver):
    """Open the bets panel if the opener button is present."""
    try:
        # Look for the opener button with a small wait
        opener_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modern-layout-module_asideOpenerButton__nfGhC-OF__platform-desktop-ui"))
        )
        opener_button.click()
        print("Opened bets panel")
        time.sleep(1)  # Short wait for animation
    except Exception as e:
        print("Bets panel already open or button not found")
        pass  # Continue with the program if button is not found



# Example usage
if __name__ == "__main__":
    try:
        # List of URLs to check
        urls = [
            #"https://tonybet.com/cl/live?top=1",
            #"https://tonybet.com/cl/live/tennis",
            #"https://tonybet.com/cl/live/football",
            #"https://tonybet.com/cl/live/basketball",
            #"https://tonybet.com/cl/live/volleyball",
            #"https://tonybet.com/cl/live/badminton",
            "https://tonybet.com/cl/live/table-tennis"
            #"https://tonybet.com/cl/live/cricket"
            #"https://tonybet.com/cl/live/esport-fifa",
            #"https://tonybet.com/cl/live/snooker",
            #"https://tonybet.com/cl/live/dota-2",
            #"https://tonybet.com/cl/live/league-of-legends",
            #"https://tonybet.com/cl/live/futsal"
            #"https://tonybet.com/cl/live/baseball",
            #"https://tonybet.com/cl/live/ice-hockey"
        ]

        driver = scrape_full_structure(urls[0])  # Start with the first URL

        while True:  # Main loop to continuously check URLs
            for index, url in enumerate(urls):
                print(f"Checking URL: {url}")
                driver.get(url)  # Navigate to the URL
                time.sleep(2)

                # Open bets panel if needed
                open_bets(driver)

                # Run the check_balance function
                balance_value = check_balance(driver)  # Check balance logic here

                # Call bet_sel to click buttons
                #button_clicked = bet_sel(driver)
                remove_betslip_2(driver)

                # Call bet_sel to click buttons and get selected outcome buttons
                selected_outcome_buttons = bet_sel(driver)

                #place_bet(driver, selected_outcome_buttons)

                # Place a bet only after visiting the last URL and returning to the first
                #if index == len(urls) - 1:  # If it's the last URL
                #    place_bet(driver)  # Place a bet after checking all URLs

                # Wait before checking the next URL or re-checking
                time.sleep(1)  # Adjust as necessary

    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_fd.close()
