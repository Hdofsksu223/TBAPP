from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import getpass  # Import getpass for secure password input

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
            
            if balance_value > 1500:
                print(f"Balance is {balance_value}. Proceeding to place bets...")
                return balance_value  # Return the balance value for further use
            else:
                print("Balance is insufficient. Waiting for balance update...")
                time.sleep(5)  # Wait and retry balance check

        except Exception as e:
            print("Error checking balance:", e)
            time.sleep(5)

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

def check_outcome_button_values(driver, selected_outcome_buttons):
    """Check the values of selected outcome buttons and unclick those above the threshold."""
    values_below_threshold = True  # Flag to check if all values are below 1.1
    for button in selected_outcome_buttons:
        try:
            value_span = button.find_element(By.XPATH, ".//span")
            value_text = value_span.text.strip()
            value = float(value_text)

            if value > 1.09:
                # Unclick the button if the value is above 1.1
                button.click()  # This assumes clicking again will unselect it
                print(f"Unclicked button for value: {value} (above threshold)")
                values_below_threshold = False  # Set flag to false if any value is above 1.1
                time.sleep(1)

        except Exception as e:
            print("Error retrieving value from button:", e)

    return values_below_threshold


def place_bet_and_check_errors(driver, selected_outcome_buttons, amount):

    if not check_bet_amount(driver, amount):
        # Unclick the selected outcome buttons if the bet amount is not sufficient
        for button in selected_outcome_buttons:
            button.click()  # This assumes clicking again will unselect it
            print("Unclicked selected outcome button due to insufficient bet amount.")
        return False  # Exit the function if the bet cannot be placed
    
    """Click the 'Apostar' button and check for error messages."""
    apostar_button = driver.find_element(By.XPATH, "//button[@data-test='betslip-place-bet']//span[contains(text(), 'Apostar')]")
    apostar_button.click()  # Click the "Apostar" button
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
                    print("Unclicked selected outcome button.")
                return placed_bet  # Exit the function after handling the error
        except Exception:
            # If the error message is not found, continue checking
            print("Looking for after-bet errors")
            continue

    if placed_bet:
        print("Bet placed successfully.")
    time.sleep(30)  # Wait for 30 seconds after placing a bet
    return placed_bet

def input_bet(driver, selected_outcome_buttons):
    """Main function to input the bet and place it."""
    amount = set_bet_amount(driver)  # Set the bet amount

    # Check if the input field is not empty
    bet_input = driver.find_element(By.XPATH, "//input[@data-test='betslip-amount']")
    if bet_input.get_attribute("value"):  # Check if the value is not empty
        time.sleep(1)
        
        # Check outcome button values
        values_below_threshold = check_outcome_button_values(driver, selected_outcome_buttons)

        # If all values are below 1.1, place the bet
        if values_below_threshold:
            placed_bet = place_bet_and_check_errors(driver, selected_outcome_buttons, amount)
            return placed_bet
        else:
            print("One or more values were above 1.1. Bet not placed.")
    else:
        print("Bet amount is empty. Cannot place bet.")

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
            input_bet(driver, selected_outcome_buttons)
        except Exception as e:
            print("Error input bet:", e)

    except Exception as e:
        print("Error placing bet:", e)



def sport_case(driver, button, associated_alt, events_table, league_name, period_text, game_period, selected_outcome_buttons, row):
    """Handle the logic for different sports based on associated_alt."""
    try:
       # Wait for the game timer element
        game_timer = row.find_element(By.XPATH, ".//div[@data-test='liveTimer']")
        timer_text = game_timer.text.strip()  # Get the timer text

        # Convert timer to total seconds
        minutes, seconds = map(int, timer_text.split(':'))  # Split MM:SS and convert to integers
        total_seconds = minutes * 60 + seconds  # Calculate total seconds

    except Exception as e:
        print("Error finding game timer:", e)
        total_seconds = 0  # Set to 0 if not found

    # Match the associated_alt value to determine the sport logic
    match associated_alt:
        case '1':  # Fútbol
            if total_seconds < 4801 or "no iniciado" in period_text.lower():
                print(f"Skipping button click for league: {league_name} at timer: {timer_text}")
                return  # Move on to the next case or iteration
            
            if total_seconds > 4800:  # 80 minutes in seconds
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '2':  # Basket
            if total_seconds < 2101 or "no iniciado" in period_text.lower():
                print(f"Skipping button click for league: {league_name} at timer: {timer_text}")
                return  # Move on to the next case or iteration
            
            if total_seconds > 2100:  # 35 minutes in seconds
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '3':  # Tenis
            stbk_text = ""
            stbk = game_period.find_element(By.XPATH, ".//span")
            stbk_text = stbk.text.strip()

            try:
                if not stbk == "":
                    print(f"Last set: {stbk_text}")
                else:
                    print(f"No super tie break yet ,,{stbk_text},,,")
            except Exception as e:
                print(f"Error: ", e)
            
            if "1er set" in period_text.lower() or "no iniciado" in period_text.lower():
                print(f"Skipping button click for league: {league_name} at timer: {period_text} because it's in the 1er set.")
                return  # Move on to the next case or iteration

            if any(phrase.lower() in period_text.lower() for phrase in ["3º set", "4º set", "5º set"]) and any(phrase.lower() in league_name.lower() for phrase in ["open de australia indiv", "australian open men singles", "australian open women singles"]):
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {period_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button
            elif any(phrase.lower() in period_text.lower() for phrase in ["2do set", "3º set", "4º set", "5º set"]):
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {period_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '4':  # Hockey hielo
            if total_seconds < 3121 or "no iniciado" in period_text.lower():
                print(f"Skipping button click for league: {league_name} at timer: {timer_text}")
                return  # Move on to the next case or iteration
            
            if total_seconds > 3120:  # 52 minutes in seconds
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '7':  # Voleibol
            if any(phrase.lower() in period_text.lower() for phrase in ["3º set", "4º set", "5º set"]):
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {period_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '10':  # Handball
            if total_seconds < 3121 or "no iniciado" in period_text.lower():
                print(f"Skipping button click for league: {league_name} at timer: {timer_text}")
                return  # Move on to the next case or iteration
            
            if total_seconds > 3120:  # 52 minutes in seconds
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '12':  # Badminton
            button.click()
            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
            time.sleep(1)  # Wait for 1 second after clicking
            selected_outcome_buttons.append(button)  # Save clicked button

        case '14':  # Futsal
            if total_seconds < 1921 or "no iniciado" in period_text.lower():
                print(f"Skipping button click for league: {league_name} at timer: {timer_text}")
                return  # Move on to the next case or iteration
            
            if total_seconds > 1920:  # 32 minutes in seconds
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '15':  # Pinpon
            if any(phrase.lower() in period_text.lower() for phrase in ["1er set", "2do set", "no iniciado", "primer", "segundo"]):
                print(f"Skipping button click for league: {league_name} at timer: {period_text} because it's in the first or second set.")
                return  # Move on to the next case or iteration
            
            if any(phrase.lower() in period_text.lower() for phrase in ["3º set", "4º set", "5º set"]):
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {period_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '17':  # Fut americano
            if total_seconds < 3121 or "no iniciado" in period_text.lower():
                print(f"Skipping button click for league: {league_name} at timer: {timer_text}")
                return  # Move on to the next case or iteration
            
            if total_seconds > 3120:  # 52 minutes in seconds
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '22':  # Criquet
            button.click()
            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
            time.sleep(1)  # Wait for 1 second after clicking
            selected_outcome_buttons.append(button)  # Save clicked button

        case '42':  # Golf
            button.click()
            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
            time.sleep(1)  # Wait for 1 second after clicking
            selected_outcome_buttons.append(button)  # Save clicked button

        case '1054':  # CounterStrike
            button.click()
            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
            time.sleep(1)  # Wait for 1 second after clicking
            selected_outcome_buttons.append(button)  # Save clicked button

        case '1056':  # Dota2
            button.click()
            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
            time.sleep(1)  # Wait for 1 second after clicking
            selected_outcome_buttons.append(button)  # Save clicked button

        case '1059':  # Esoccer
            if total_seconds < 361 or "no iniciado" in period_text.lower():
                print(f"Skipping button click for league: {league_name} at timer: {timer_text}")
                return  # Move on to the next case or iteration
            
            if total_seconds > 360:  # 6 minutes in seconds
                button.click()
                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                time.sleep(1)  # Wait for 1 second after clicking
                selected_outcome_buttons.append(button)  # Save clicked button

        case '1067':  # LoL
            button.click()
            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
            time.sleep(1)  # Wait for 1 second after clicking
            selected_outcome_buttons.append(button)  # Save clicked button

        case _:  # Default case if no match found
            print(f"No matching case for associated_alt: {associated_alt}")

# New function to obtain button information
def button_info(driver, button, selected_outcome_buttons, row):
    value_span = button.find_element(By.XPATH, ".//span")
    value_text = value_span.text.strip()
    print(value_text)
    value = float(value_text)

    if value < 1.1:  # Adjusted condition to click buttons with value < 1.1
        events_table = button.find_element(By.XPATH, ".//ancestor::div[@data-test='eventsTable']")
        associated_image = events_table.find_element(By.XPATH, ".//img[@title='Sport']")
        associated_alt = associated_image.get_attribute("alt")

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
        # Inside your main logic where you handle the sports
        sport_case(driver, button, associated_alt, events_table, league_name, game_period, period_text, selected_outcome_buttons, row)

# Function to select bets based on conditions
def bet_sel(driver):
    remove_betslip(driver)
    selected_outcome_buttons = []  # Array to store selected outcome buttons
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
                    button_info(driver, button, selected_outcome_buttons, row)
                    
                    time.sleep(0.5)  # Optional: wait a moment before checking again

                except Exception as e:
                    print(f"Error processing button:", e)

        except Exception as e:
            print(f"Error processing event row:", e)

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

# Example usage
if __name__ == "__main__":
    # List of URLs to check
    urls = [
        #"https://tonybet.com/cl/live?top=1",
        "https://tonybet.com/cl/live/tennis",
        #"https://tonybet.com/cl/live/football",
        #"https://tonybet.com/cl/live/basketball",
        #"https://tonybet.com/cl/live/volleyball",
        #"https://tonybet.com/cl/live/badminton",
        #"https://tonybet.com/cl/live/table-tennis"
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

            # Run the check_balance function
            balance_value = check_balance(driver)  # Check balance logic here

            # Call bet_sel to click buttons
            #button_clicked = bet_sel(driver)

            # Call bet_sel to click buttons and get selected outcome buttons
            selected_outcome_buttons = bet_sel(driver)

            place_bet(driver, selected_outcome_buttons)

            # Place a bet only after visiting the last URL and returning to the first
            #if index == len(urls) - 1:  # If it's the last URL
            #    place_bet(driver)  # Place a bet after checking all URLs

            # Wait before checking the next URL or re-checking
            time.sleep(1)  # Adjust as necessary

    driver.quit()
