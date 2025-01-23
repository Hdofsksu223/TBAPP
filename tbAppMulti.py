from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import getpass  # Import getpass for secure password input
import concurrent.futures

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

        email_input = driver.find_element(By.XPATH, "//input[@placeholder='Correo electrónico']")
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='Contraseña']")
        
        email_input.send_keys(email)
        password_input.send_keys(password)

        # Click the submit button to log in
        submit_button = driver.find_element(By.XPATH, "//button[@data-test='submitLogin' and contains(., 'Iniciar sesión')]")
        submit_button.click()
    except Exception as e:
        print("Error logging in:", e)

# Function to check the balance
def check_balance(driver):
    while True:
        try:
            # Locate the balance element
            balance_element = driver.find_element(By.XPATH, "//div[contains(@class, 'customer-balance-module_text')]")
            balance_text = balance_element.text.strip()
            balance_value = int(balance_text.replace('$', '').replace(',', '').strip())
            return balance_value  # Return the balance value for further use
        except Exception as e:
            print("Error checking balance:", e)
            time.sleep(30)

# Function to place a bet
def place_bet(driver):
    try:
        no_bid_element = driver.find_elements(By.XPATH, "//div[@class='coupon-no-bid-module_couponBids__jnyAzF6g__platform-common' and @data-test='noOutcomePlaceHolder']")
        if not no_bid_element:
            print("No bids available. Cannot place a bet.")
            return  # Exit the function if the no-bid element is found

        # Locate the bet amount input field
        bet_input = driver.find_element(By.XPATH, "//input[@data-test='betslip-amount']")
        bet_input.clear()  # Clear any existing value
        
        # Set the value to 90% of the balance (assuming balance_value is passed)
        # bet_amount = balance_value * 0.9
        # bet_input.send_keys(str(bet_amount))  # Set the value to 90% of the balance

        # For demonstration, let's set a fixed value (you can uncomment the above lines for dynamic value)
        bet_input.send_keys("500")  # Set the value to 500

        # Locate the "Apostar" button
        apostar_button = driver.find_element(By.XPATH, "//button[@data-test='betslip-place-bet']//span[contains(text(), 'Apostar')]")

        # Check if the input field is not empty
        if bet_input.get_attribute("value"):  # Check if the value is not empty
            time.sleep(30)  # Optional: wait before placing the bet
            apostar_button.click()  # Click the "Apostar" button
            print("Bet placed successfully.")
            time.sleep(300)  # Wait for 5 minutes after placing a bet
        else:
            print("Bet amount is empty. Cannot place bet.")

    except Exception as e:
        print("Error placing bet:", e)

# Function to select bets based on conditions
def bet_sel(driver):
    while True:
        outcome_buttons = driver.find_elements(By.XPATH, "//div[@data-test='outcome']")
        if not outcome_buttons:
            print("No outcome buttons found.")
            time.sleep(5)
            continue

        for button in outcome_buttons:
            try:
                value_span = button.find_element(By.XPATH, ".//span")
                value_text = value_span.text.strip()
                value = float(value_text)

                # Match-case logic for different sports
                # (Add your match-case logic here based on the value and other conditions)
                # Example:
                if value > 5:  # Adjusted condition to click buttons with value < 1.1
                    events_table = button.find_element(By.XPATH, ".//ancestor::div[@data-test='eventsTable']")
                    associated_image = events_table.find_element(By.XPATH, ".//img[@title='Sport']")
                    associated_alt = associated_image.get_attribute("alt")

                    # Find the league name from the corresponding 'a' tag
                    league_name_element = events_table.find_element(By.XPATH, ".//a[@data-test='leagueLink']")  # Locate the league link
                    league_name = league_name_element.text.strip()  # Get the league name text

                    # Get the period text
                    try:
                        game_period = events_table.find_element(By.XPATH, ".//div[@data-test='eventPeriodAndScore']")
                        period_text = game_period.text.strip()
                        print(f"Game period text: {period_text}")  # Debugging statement
                    except Exception as e:
                        print("Error finding game period:", e)
                        period_text = ""  # Set to empty if not found

                    try:
                        # Get the timer value
                        game_timer = events_table.find_element(By.XPATH, ".//div[@data-test='liveTimer']")
                        timer_text = game_timer.text.strip()  # Get the timer text

                        # Convert timer to total seconds
                        minutes, seconds = map(int, timer_text.split(':'))  # Split MM:SS and convert to integers
                        total_seconds = minutes * 60 + seconds  # Calculate total seconds
                    except Exception as e:
                        print("Error finding game timer:", e)
                        total_seconds = 0  # Set to 0 if not found

                    print(f"Associated alt value: {associated_alt}")  # Debugging statement
                    print(f"League name: {league_name}")  # Debugging statement

                    match associated_alt:
                        case '1':  # Fútbol
                            if total_seconds > 4800:  # 80 minutes in seconds
                                button.click()
                                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                                time.sleep(1)  # Wait for 1 second after clicking
                                button_clicked = True  # Set the flag to True

                        case '2':  # Basket
                            if total_seconds > 2100:  # 35 minutes in seconds
                                button.click()
                                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                                time.sleep(1)  # Wait for 1 second after clicking
                                button_clicked = True  # Set the flag to True

                        case '3':  # Tenis
                            if "2do set" in period_text or "3º set" in period_text:
                                button.click()
                                print(f"Button clicked for league: {league_name} at timer: {period_text}")
                                time.sleep(1)  # Wait for 1 second after clicking
                                button_clicked = True  # Set the flag to True

                        case '4':  # Hockey hielo
                            if total_seconds > 3120:  # 52 minutes in seconds
                                button.click()
                                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                                time.sleep(1)  # Wait for 1 second after clicking
                                button_clicked = True  # Set the flag to True

                        case '7':  # Voleibol
                            if "2do set" in period_text or "3º set" in period_text:
                                button.click()
                                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                                time.sleep(1)  # Wait for 1 second after clicking
                                button_clicked = True  # Set the flag to True

                        case '10':  # Handball
                            if total_seconds > 3120:  # 52 minutes in seconds
                                button.click()
                                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                                time.sleep(1)  # Wait for 1 second after clicking
                                button_clicked = True  # Set the flag to True

                        case '12':  # Badminton
                            button.click()
                            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                            time.sleep(1)  # Wait for 1 second after clicking
                            button_clicked = True  # Set the flag to True

                        case '14':  # Futsal
                            if total_seconds > 1920:  # 32 minutes in seconds
                                button.click()
                                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                                time.sleep(1)  # Wait for 1 second after clicking
                                button_clicked = True  # Set the flag to True

                        case '15':  # Pinpon
                            if "2do set" in period_text or "3º set" in period_text:
                                button.click()
                                print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                                time.sleep(1)  # Wait for 1 second after clicking
                                button_clicked = True  # Set the flag to True

                        case '17':  # Fut americano
                            button.click()
                            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                            time.sleep(1)  # Wait for 1 second after clicking
                            button_clicked = True  # Set the flag to True

                        case '22':  # Criquet
                            button.click()
                            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                            time.sleep(1)  # Wait for 1 second after clicking
                            button_clicked = True  # Set the flag to True

                        case '42':  # Golf
                            button.click()
                            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                            time.sleep(1)  # Wait for 1 second after clicking
                            button_clicked = True  # Set the flag to True

                        case '1054':  # CounterStrike
                            button.click()
                            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                            time.sleep(1)  # Wait for 1 second after clicking
                            button_clicked = True  # Set the flag to True

                        case '1056':  # Dota2
                            button.click()
                            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                            time.sleep(1)  # Wait for 1 second after clicking
                            button_clicked = True  # Set the flag to True

                        case '1059':  # Esoccer
                            button.click()
                            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                            time.sleep(1)  # Wait for 1 second after clicking
                            button_clicked = True  # Set the flag to True

                        case '1067':  # LoL
                            button.click()
                            print(f"Button clicked for league: {league_name} at timer: {timer_text}")
                            time.sleep(1)  # Wait for 1 second after clicking
                            button_clicked = True  # Set the flag to True
                    time.sleep(1)  # Wait for 1 second after clicking
            except Exception as e:
                print("Error retrieving value from button:", e)
        time.sleep(30)

# Function to scrape a single URL
def scrape_url(url, driver):
    driver.get(url)
    while True:
        bet_sel(driver)  # Continuously check for outcome buttons
        time.sleep(5)  # Adjust as necessary

# Function to initialize the driver and scrape URLs
def initialize_and_scrape(url):
    options = Options()
    options.use_chromium = True
    service = Service(r'C:\Users\ignac\Downloads\msedgedriver.exe')  # Use raw string
    driver = webdriver.Edge(service=service, options=options)

    driver.get(url)
    # Maximize the browser window to full screen
    driver.maximize_window()  # Open the browser in full-screen mode
    time.sleep(5)
    accessSite(driver)

    return driver

if __name__ == "__main__":
    # List of URLs to check
    urls = [
        "https://tonybet.com/cl/live?top=1",
        "https://tonybet.com/cl/live/tennis",
        "https://tonybet.com/cl/live/football",
        "https://tonybet.com/cl/live/basketball",
        "https://tonybet.com/cl/live/volleyball",
        "https://tonybet.com/cl/live/badminton",
        "https://tonybet.com/cl/live/table-tennis",
        "https://tonybet.com/cl/live/cricket",
        "https://tonybet.com/cl/live/esport-fifa",
        "https://tonybet.com/cl/live/snooker",
        "https://tonybet.com/cl/live/dota-2",
        "https://tonybet.com/cl/live/league-of-legends",
        "https://tonybet.com/cl/live/counter-strike"
    ]

    # Initialize the driver and log in
    driver = initialize_and_scrape(urls[0])  # Use the first URL for initialization
    time.sleep(5)
    email, password = get_user_credentials()
    time.sleep(5)
    login(driver, email, password)
    time.sleep(5)

    # Start scraping all URLs simultaneously after logging in
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(scrape_url, url, driver): url for url in urls}

        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                future.result()  # This will raise an exception if the function failed
            except Exception as e:
                print(f"Error occurred while scraping {url}: {e}")
