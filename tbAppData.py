import sys
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import getpass  # Import getpass for secure password input
import re
import psycopg2
from psycopg2 import sql


def get_db_connection():
    try:
        return psycopg2.connect(
            host="localhost",
            database="tebedata",
            user="postgres",
            password="admin",  # Add actual password
            port="5432"
        )
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None


def insert_into_bet_history(data):
    """Insert validated data into bet_history table"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to establish database connection")
            return
        query = sql.SQL("""
            INSERT INTO bet_history (
                bet_id, bet_date, bet_time, odds, stake, win_amount, bet_status,
                sport_id, league, team_1, team_2, selected_team, match_result,
                point_score, set_score, bet_type
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        """)
        
        # Validate and transform data
        validated = {
            'bet_id': data.get('bet_id'),
            'bet_date': data.get('bet_date'),
            'bet_time': data.get('bet_time'),
            'odds': float(data['odds']) if data.get('odds') else None,
            'stake': float(data['stake']) if data.get('stake') else None,
            'win_amount': float(data['win_amount']) if data.get('win_amount') else 0.0,
            'bet_status': data.get('bet_status'),
            'sport_id': int(data['sport_id']) if data.get('sport_id') else None,
            'league': data.get('league'),
            'team_1': data.get('team_1'),
            'team_2': data.get('team_2'),
            'selected_team': data.get('selected_team'),
            'match_result': data.get('match_result'),
            'point_score': data.get('point_score'),
            'set_score': data.get('set_score'),
            'bet_type': int(data.get('bet_type', 1))  # Default to simple bet
        }

        with conn.cursor() as cursor:
            cursor.execute(query, tuple(validated.values()))
        conn.commit()
        print(f"Successfully inserted bet {validated['bet_id']}")
        
    except Exception as e:
        print(f"Database insertion error: {str(e)}")
        print(f"Failed data: {validated}")
    finally:
        if conn:
            conn.close()




def setup_logging():
    """Configure logging to file and console"""
    logs_dir = 'logs'
    os.makedirs(logs_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"data_log_{timestamp}.txt"
    log_path = os.path.join(logs_dir, log_filename)
    
    log_file = open(log_path, 'a', encoding='utf-8')
    
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
    sys.stdout = Tee(sys.stdout, log_file)
    
    return original_stdout, log_file


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
            
            if balance_value > 1000:
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

def place_bet_and_check_errors(driver, selected_outcome_buttons, amount, row):
    """Click the 'Apostar' button and check for error messages."""
    # Final check right before placing bet
    valid_buttons = []
    for button in selected_outcome_buttons:
        try:
            value_span = button.find_element(By.XPATH, ".//span")
            current_value = float(value_span.text.strip())
            if current_value <= 1.09:
                valid_buttons.append(button)
            else:
                button.click()
                print(f"Unclicked button with value {current_value} before placing bet")
        except Exception as e:
            print("Error in final button check:", e)
    
    if not valid_buttons:
        print("No valid buttons remaining after final check")
        return False

    if not check_bet_amount(driver, amount):
        # Unclick the selected outcome buttons if the bet amount is not sufficient
        for button in selected_outcome_buttons:
            button.click()  # This assumes clicking again will unselect it
            print("Unclicked selected outcome button due to insufficient bet amount.")
        return False  # Exit the function if the bet cannot be placed

    # Locate the 'Apostar' button
    apostar_button = driver.find_element(By.XPATH, "//button[@data-test='betslip-place-bet']//span[contains(text(), 'Apostar')]")
    
    # Attempt to click the 'Apostar' button with retries
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

    if not click_with_retry(apostar_button):
        print("Failed to click 'Apostar' button after multiple attempts.")
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
                for button in selected_outcome_buttons:
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
        for button in selected_outcome_buttons:
            try:
                # Find the event container for the button
                events_table = button.find_element(By.XPATH, ".//ancestor::div[@data-test='eventTableRow']")
                
                team_scores = events_table.find_elements(By.XPATH, ".//div[contains(@class, 'event-table-additional-results-module_base__ZlPakjl1__platform-common')]")
                team_names = events_table.find_elements(By.XPATH, ".//div[@data-test='teamName']")
    
                
                print("Scoreboard:")
                for team_name, team_score in zip(team_names, team_scores):
                    print(f"Team Name: {team_name.text}, Team Score: {team_score.text}")

            except Exception as e:
                print("Error retrieving team names and scores:", e)

    time.sleep(300)  # Wait for 30 seconds after placing a bet
    return placed_bet

def input_bet(driver, selected_outcome_buttons, row, button):
    """Main function to input the bet and place it."""
    amount = set_bet_amount(driver)  # Set the bet amount

    # Check if the input field is not empty
    bet_input = driver.find_element(By.XPATH, "//input[@data-test='betslip-amount']")
    if bet_input.get_attribute("value"):  # Check if the value is not empty
        time.sleep(1)
        
        # Place the bet
        placed_bet = place_bet_and_check_errors(driver, selected_outcome_buttons, amount, row)

        return placed_bet
    else:
        print("Bet amount is empty. Cannot place bet.")

def recheck_button_value(button, selected_outcome_buttons):
    # Re-check value after clicking
    value_span = button.find_element(By.XPATH, ".//span")
    current_value = float(value_span.text.strip())
    if current_value > 1.09:
        button.click()  # Unclick if value changed
        selected_outcome_buttons.remove(button)
        print("Unclicked due to value change after selection")

# Function to place a bet
def place_bet(driver, selected_outcome_buttons):
    try:
        # Check for the presence of the no-bid module
        no_bid_element = driver.find_elements(By.XPATH, "//div[@class='coupon-no-bid-module_couponBids__jnyAzF6g__platform-common' and @data-test='noOutcomePlaceHolder']")
        if no_bid_element:
            print("No bids available. Cannot place a bet.")
            return  # Exit the function if the no-bid element is found
        
        try:
            remove_betslip(driver)
        except Exception as e:
            print("Error removing betslips:", e)

        try:
            # Get the row and button from the first selected outcome button
            if selected_outcome_buttons:
                button = selected_outcome_buttons[0]
                row = button.find_element(By.XPATH, ".//ancestor::div[@data-test='eventTableRow']")
                input_bet(driver, selected_outcome_buttons, row, button)
        except Exception as e:
            print("Error input bet:", e)

    except Exception as e:
        print("Error placing bet:", e)

def process_table_tennis_button(button, row, selected_outcome_buttons):
    try:
        value_span = button.find_element(By.XPATH, ".//span")
        value_text = value_span.text.strip()
        value = float(value_text)
        print(value_text)
        
        if value > 1.09:
            return False

        # Get match status
        period_element = row.find_element(By.XPATH, ".//div[@data-test='eventPeriodAndScore']")
        period_text = period_element.text.strip().lower()
        
        # Check set conditions
        if any(phrase in period_text.lower() for phrase in ["1er set", "2do set", "no iniciado", "break"]):
            return False
            
        if not any(phrase in period_text.lower() for phrase in ["3º set", "4º set", "5º set"]):
            return False

        # Get scores
        team_scores = row.find_elements(By.XPATH, ".//div[contains(@class, 'event-table-additional-results-module_base__ZlPakjl1__platform-common')]")
        team_names = row.find_elements(By.XPATH, ".//div[@data-test='teamName']")
        score_dict = {name.text.strip(): int(score.text.strip()) for name, score in zip(team_names, team_scores)}
        
        # Get selected team name
        selected_team_element = button.find_element(By.XPATH, ".//ancestor::div[contains(@class, 'coupon-bet-market-module_Wrapper__3943a5BB__platform-common')]")
        selected_team_name = selected_team_element.text.replace("Ganador:", "").strip()

        if not check_selected_team_score(selected_team_name, score_dict):
            return False

        # All conditions met
        button.click()
        selected_outcome_buttons.append(button)
        time.sleep(0.5)
        return True

    except Exception as e:
        print(f"Error processing button: {e}")
        return False

def check_selected_team_score(selected_team_name, score_dict):
    """Check if selected team is winning by 3+ points."""
    if selected_team_name in score_dict:
        selected_score = score_dict[selected_team_name]
        for name, score in score_dict.items():
            if name != selected_team_name and (selected_score - score) >= 2:
                return True
    return False

def bet_sel(driver):
    remove_betslip_2(driver)
    selected_outcome_buttons = []
    event_rows = driver.find_elements(By.XPATH, "//div[@data-test='eventTableRow']")
    
    for row in event_rows:
        try:
            market_item = row.find_element(By.XPATH, ".//div[@data-test='marketItem'][1]")
            outcome_buttons = market_item.find_elements(By.XPATH, ".//div[@data-test='outcome']")
            
            for button in outcome_buttons:
                if process_table_tennis_button(button, row, selected_outcome_buttons):
                    time.sleep(0.5)
                else:
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"Error processing row: {e}")
    
    return selected_outcome_buttons

def scrape_full_structure():
    options = Options()
    options.use_chromium = True
    service = Service(r'C:\Users\ignac\Downloads\msedgedriver.exe')
    driver = webdriver.Edge(service=service, options=options)
    driver.get("https://tonybet.com/cl/cabinet/betting-history")
    driver.maximize_window()
    time.sleep(10)
    accessSite(driver)
    email, password = get_user_credentials()
    login(driver, email, password)
    time.sleep(10)
    return driver


def scroll_rows(driver):
    """Iterate through bet history items with dynamic loading and expand their details"""
    try:
        c = 0
        # Scroll to bottom
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Allow time for content loading
            driver.execute_script("window.scrollBy(0, -500);")
            time.sleep(0.5)
            c = c + 1
            print(f"Scroll counter: {c}")
            if c == 170:
                break

        

        time.sleep(3)
        # Process all loaded items
        bet_history_items = driver.find_elements(By.XPATH, "//tbody[@data-test='bet-history-item']")
        print(f"Found {len(bet_history_items)} bet items after scrolling")
        
        for index, item in enumerate(bet_history_items):
            try:
                # Special handling for first item
                if index == 0:
                    # Scroll slightly above the first item to account for headers
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    driver.execute_script("window.scrollBy(0, 200);")
                    time.sleep(1)

                # Wait for expand button in current item
                expand_button = WebDriverWait(item, 10).until(
                    EC.element_to_be_clickable((By.XPATH, ".//button[@data-test='expand']"))
                )
                
                # Use JavaScript click as fallback
                try:
                    expand_button.click()
                except:
                    driver.execute_script("arguments[0].click();", expand_button)
                
                # Add stabilization delay after first click
                if index == 0:
                    time.sleep(2)
                
                print("")
                print("")
                print("-----------------------------------------------")
                print(f"Expanded item {index+1}/{len(bet_history_items)}")
                time.sleep(0.5)  # Short pause for UI update
                bet_type = get_bet_type(item)
                print(f"Bet_type: {bet_type}")
                if bet_type == 1:
                    data = {}
                    data.update(scrape_1(item))
                    data.update(scrape_2(item))
                    data.update(scrape_3(item))
                    data['bet_type'] = 1
                    insert_into_bet_history(data)
                elif bet_type == 2:
                    all_rows = item.find_elements(
                        By.XPATH, 
                        ".//tr[contains(@class, 'rounded-table-module_tr__cneKHX1T__platform-desktop-ui')]"
                    )
                    
                    # Header row (contains bet_id, date, etc.)
                    header_row = all_rows[0]
                    header_data = scrape_1(header_row)
                    
                    # Process matches in groups of subsequent rows
                    match_groups = []
                    current_group = []
                    
                    for row in all_rows[1:]:  # Skip header row
                        if 'details-module_league__' in row.get_attribute('innerHTML'):
                            # League separator row, start new group
                            if current_group:
                                match_groups.append(current_group)
                            current_group = []
                        else:
                            current_group.append(row)
                    
                    if current_group:  # Add last group
                        match_groups.append(current_group)

                    # Process each match group
                    for group in match_groups:
                        if len(group) >= 2:
                            # First row in group contains selection data (scrape_2)
                            # Second row contains result data (scrape_3)
                            group_data = header_data.copy()
                            group_data.update(scrape_2(group[0]))
                            group_data.update(scrape_3(group[1]))
                            group_data['bet_type'] = 2
                            insert_into_bet_history(group_data)
                        elif group:  # Handle partial groups
                            group_data = header_data.copy()
                            group_data.update(scrape_2(group[0]))
                            group_data['bet_type'] = 2
                            #insert_into_bet_history(group_data)
                            if len(group) > 1:
                                group_data = header_data.copy()
                                group_data.update(scrape_3(group[1]))
                                group_data['bet_type'] = 2
                                insert_into_bet_history(group_data)
                
            except Exception as e:
                print(f"Error processing item {index+1}: {str(e)}")
                continue

    except Exception as e:
        print(f"Error in scroll_rows: {str(e)}")


def sel_datepicker_1(driver):
    try:
        # Click the first date picker
        date_picker = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-test='datePicker']"))
        )
        date_picker.click()
        time.sleep(1)  # Wait for calendar to open

        # Click previous month button 5 times
        prev_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                "//button[contains(@class, 'react-datepicker__navigation--previous')]"))
        )
        
        for _ in range(5):
            prev_button.click()
            time.sleep(0.5)  # Short pause between clicks

        # Click the first day of the month
        day_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, 
                "//div[contains(@class, 'react-datepicker__day--001') and not(contains(@class, 'outside-month'))]"))
        )
        day_element.click()
        time.sleep(1)  # Final wait

    except Exception as e:
        print(f"Error in date picker selection: {str(e)}")
        raise


def scrape_2(item):
    try:
        # Get sport ID as integer
        sport_id = get_sport_id(item)  # Assume this returns string like "sport-25"
        #sport_id = int(sport_id_str.split('-')[-1])  # Extract numeric part
        
        # Get league name
        liga_element = item.find_element(By.XPATH, ".//div[contains(@class, 'details-module_league__CSGMiNgP__platform-desktop-ui')]")
        league = liga_element.text.strip()

        print(f"Match Sport ID: {sport_id} ({type(sport_id)})")
        print(f"Match league: {league}")

        return {
            'sport_id': sport_id,  # Integer type
            'league': league if league else None  # NULL if empty
        }
    except Exception as e:
        print(f"Scrape2 error: {str(e)}")
        return {}


def scrape_1(item):
    try:
        bet_id_td = item.find_element(By.XPATH, ".//td[@data-test='betting-history-bet_id']") 
        bet_id = bet_id_td.text.strip()
        # Date parsing fix using correct elements
        date_span = item.find_element(By.XPATH, ".//span[@data-test='eventDate']")
        time_span = item.find_element(By.XPATH, ".//span[@data-test='eventTime']")
        
        # Get cleaned text content
        date_text = date_span.text.strip().replace('\xa0', ' ')
        time_text = time_span.text.strip().replace('\xa0', ' ').replace(',', '').strip()
        
        # Handle European date format
        parsed_date = datetime.strptime(date_text, "%d.%m.%Y").date()
        parsed_time = datetime.strptime(time_text, "%H:%M").time()

        # Numeric field handling
        odds_element = item.find_element(By.XPATH, ".//td[@data-test='betting-history-odds']")
        odds_text = str(odds_element.text).replace(',', '.')  # Convert to string first
        odds = float(odds_text) if odds_text else None

        # Convert numeric fields safely
        stake = get_bet_stake(item)
        #stake = float(str(item.find_element(By.XPATH, ".//div[contains(text(), 'Stake:')]/following-sibling::div").text).replace('$', '').replace(',', ''))
        
        return {
            'bet_id': bet_id,
            'bet_date': parsed_date,
            'bet_time': parsed_time,
            'odds': odds,
            'stake': stake,
            'win_amount': get_win_amount(item),
            'bet_status': get_bet_status(item),
            'sport_id': get_sport_id(item),
            'league': item.find_element(By.XPATH, ".//div[contains(@class, 'details-module_league__CSGMiNgP__platform-desktop-ui')]").text.strip(),
            'team_1': get_teams(item)[0],
            'team_2': get_teams(item)[1],
            'selected_team': get_sel_team(item),
            'match_result': get_match_result(item),
            'point_score': scrape_3(item)['point_score'],
            'set_score': scrape_3(item)['set_score'],
            'bet_type': get_bet_type(item)
        }
    except Exception as e:
        print(f"Scrape1 error: {str(e)}")
        return {}

def scrape_3(item):
    try:
        # Handle missing teams
        teams = get_teams(item) or (None, None)
        team_1, team_2 = teams if teams else (None, None)
        
        # Handle scores with fallback
        scores = (None, None)
        point_score, set_score = scores

        return {
            'team_1': team_1.strip() if team_1 else None,
            'team_2': team_2.strip() if team_2 else None,
            'point_score': point_score,
            'set_score': set_score,
            'selected_team': get_sel_team(item),
            'match_result': get_match_result(item),
            'bet_type': get_bet_type(item)
        }
    except Exception as e:
        print(f"Scrape3 error: {str(e)}")
        return {}


def get_date_time(item):
    bet_date_time = item.find_element(By.XPATH, ".//td[@data-test='betting-history-ts']")
    bet_date = bet_date_time.find_element(By.XPATH, "./span[1]")
    
    bet_time = bet_date_time.find_element(By.XPATH, "./span[2]")
    return bet_date, bet_time


def get_bet_status(item):
    status_text = item.find_element(By.XPATH, ".//td[@data-test='betting-history-status']").text.strip()
    if any(phrase.lower() in status_text.lower() for phrase in ["gan"]):
        bet_status = 1
    elif any(phrase.lower() in status_text.lower() for phrase in ["perdid"]):
        bet_status = 2
    elif any(phrase.lower() in status_text.lower() for phrase in ["pendiente"]):
        bet_status = 0
    
    return bet_status


def get_bet_type(item):
    bet_types = item.find_element(By.XPATH, ".//td[@data-test='betting-history-mode']")
    bet_type = bet_types.text.strip()
    if any(phrase.lower() in bet_type.lower() for phrase in ["simple"]):
        bet_type = 1
        print(f"Bet type: simple")
    elif any(phrase.lower() in bet_type.lower() for phrase in ["múltiple", "multiple"]):
        bet_type = 2
        print(f"Bet type: múltiple")
    return bet_type


def get_sel_team(item):
    """Extract the selected team from the 'Ganador' column"""
    try:
        # Find the cell containing "Ganador"
        ganador_td = item.find_element(
            By.XPATH, 
            ".//td[contains(., 'Ganador:')]"
        )
        
        sel_team = ganador_td.get_attribute("textContent").strip()
        
        if "Ganador:" in sel_team:
            _, remainder = sel_team.split("Ganador:", 1)
            
            # Find score marker positions
            score_pos = remainder.find('-')
            en_dash_pos = remainder.find('–')
            
            # Determine cut position
            valid_positions = [p for p in [score_pos, en_dash_pos] if p != -1]
            cut_pos = min(valid_positions) if valid_positions else None

            if cut_pos is not None:
                # Get text up to score marker and remove trailing digits
                team_text = remainder[:cut_pos].strip()
                clean_team = team_text.rstrip('0123456789').strip()
                return clean_team
            return remainder.strip()
            
        return sel_team
    
    except Exception as e:
        print(f"Error retrieving selected team: {e}")
        return None

def get_match_result(item):
    """Extract the full match result from the results column"""
    try:
        # Find the result span
        result_span = item.find_element(
            By.XPATH, 
            ".//td/span[contains(., '–')]"  # Looks for hyphen character
        )
        return result_span.text.strip()
    
    except Exception as e:
        print(f"Error retrieving match result: {e}")
        return None


def get_bet_stake(item):
    try:
        # Locate the win amount container
        stake_td = item.find_element(
            By.XPATH, 
            ".//td[@data-test='betting-history-stake']"
        )
        
        # Get the numeric value from the second span
        stake_div = stake_td.find_element(
            By.XPATH, 
            ".//div[contains(@class, 'stake-module_amount__HLIXPmqj__platform-desktop-ui')]"
        )
        
        stake = stake_div.find_element(By.XPATH, "./span[2]")
        return stake.text.strip()
    
    except Exception as e:
        print(f"Error retrieving stake: {e}")
        return None


def get_win_amount(item):
    try:
        # Check if win amount container exists
        win_amount_divs = item.find_elements(
            By.XPATH, 
            ".//div[contains(@class, 'win-amount-module_amount__')]"
        )
        
        if not win_amount_divs:
            return 0  # No win amount container found
        
        win_amount_div = win_amount_divs[0]
        
        # Check if the amount span exists
        amount_spans = win_amount_div.find_elements(By.XPATH, "./span[2]")
        if not amount_spans:
            return 0  # No amount text found
        
        amount_text = amount_spans[0].text.strip()
        return int(amount_text) if amount_text else 0
    
    except Exception as e:
        print(f"Error retrieving win amount: {e}")
        return 0  # Return 0 even on exceptions


def get_teams(item):
    try:
        # Find the competitors container
        competitors_td = item.find_element(
            By.XPATH, 
            ".//td[contains(@class, 'details-module_competitors__')]"
        )
        
        # Get both competitor divs
        competitors = competitors_td.find_elements(
            By.XPATH, 
            ".//div[contains(@class, 'competitor-module_competitor__')]"
        )
        
        # Extract team names from spans
        team_1 = competitors[0].find_element(
            By.XPATH, 
            ".//span[contains(@class, 'competitor-module_ellipsis__')]"
        ).text.strip()
        
        team_2 = competitors[1].find_element(
            By.XPATH, 
            ".//span[contains(@class, 'competitor-module_ellipsis__')]"
        ).text.strip()
        
        return team_1, team_2
        
    except Exception as e:
        print(f"Error retrieving teams: {e}")
        return None, None
    


def get_sport_id(item):
    try:
        sport_img = item.find_element(By.XPATH, ".//img[contains(@src, '/assets/sport/')]")
        src = sport_img.get_attribute('src')
        
        # Use regex to find sport ID in URL
        sport_id = re.search(r'sport[/_-](\d+)', src)
        if sport_id:
            return int(sport_id.group(1))
        return None
    except Exception as e:
        print(f"Error retrieving sport ID: {str(e)}")
        return None



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
    original_stdout, log_file = setup_logging()
    try:
        driver = scrape_full_structure()
        driver.get("https://tonybet.com/cl/cabinet/betting-history")
        time.sleep(1)
        sel_datepicker_1(driver)
        time.sleep(3)
        scroll_rows(driver)
        #while True:
            #driver.get("https://tonybet.com/cl/cabinet/betting-history")
            #time.sleep(2)
            #open_bets(driver)
            #balance_value = check_balance(driver)
            #time.sleep(5)
            #selected_outcome_buttons = bet_sel(driver)
            #place_bet(driver, selected_outcome_buttons)
            #time.sleep(5)
        time.sleep(600)

        driver.quit()
    finally:
        # Restore original stdout and close log file
        sys.stdout = original_stdout
        log_file.close()