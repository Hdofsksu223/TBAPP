from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import getpass

# Access site function
def accessSite(driver):
    try:
        config_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Configuración de cookies')]")
        config_button.click()
        time.sleep(5)
        reject_all_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Rechazarlas todas')]")
        reject_all_button.click()
    except Exception as e:
        print("Error managing cookies:", e)

# Get credentials function
def get_user_credentials():
    email = input("Please enter your email: ")
    password = getpass.getpass("Please enter your password: ")
    return email, password

# Login function
def login(driver, email, password):
    try:
        login_button = driver.find_element(By.XPATH, "//button[@data-test='login' and contains(., 'Iniciar sesión')]")
        login_button.click()
        time.sleep(5)
        email_input = driver.find_element(By.XPATH, "//input[@placeholder='Correo electrónico']")
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='Contraseña']")
        email_input.send_keys(email)
        password_input.send_keys(password)
        submit_button = driver.find_element(By.XPATH, "//button[@data-test='submitLogin' and contains(., 'Iniciar sesión')]")
        submit_button.click()
    except Exception as e:
        print("Error logging in:", e)

# Balance check function
def check_balance(driver):
    try:
        balance_element = driver.find_element(By.XPATH, "//div[contains(@class, 'customer-balance-module_text')]")
        balance_text = balance_element.text.strip()
        balance_value = int(balance_text.replace('$', '').replace(',', '').strip())
        if balance_value > 500:
            return True
    except Exception as e:
        print("Error checking balance:", e)
    return False

# Place bet function
def place_bet(driver, button_clicked):
    if button_clicked:
        try:
            bet_input = driver.find_element(By.XPATH, "//input[@data-test='betslip-amount']")
            bet_input.clear()
            bet_input.send_keys("500")
            apostar_button = driver.find_element(By.XPATH, "//button[@data-test='betslip-place-bet']//span[contains(text(), 'Apostar')]")
            if bet_input.get_attribute("value"):
                time.sleep(60)
                apostar_button.click()
                print("Bet placed successfully.")
                return True
        except Exception as e:
            print("Error placing bet:", e)
    return False

# Betting selection function
def bet_sel(driver):
    button_clicked = False
    try:
        outcome_buttons = driver.find_elements(By.XPATH, "//div[@data-test='outcome']")
        for button in outcome_buttons:
            try:
                value_span = button.find_element(By.XPATH, ".//span")
                value = float(value_span.text.strip())
                if value < 1.1:
                    button.click()
                    button_clicked = True
            except Exception as e:
                print("Error processing button:", e)
    except Exception as e:
        print("Error in bet selection:", e)
    return button_clicked

# Main function to scrape and interact with the website
def scrape_full_structure(urls):
    options = Options()
    options.use_chromium = True
    service = Service(r'C:\Users\ignac\Downloads\msedgedriver.exe')
    driver = webdriver.Edge(service=service, options=options)
    driver.maximize_window()

    accessSite(driver)
    email, password = get_user_credentials()
    login(driver, email, password)

    for url in urls:
        driver.get(url)
        while True:
            if check_balance(driver):
                if bet_sel(driver):
                    place_bet(driver, True)
                    time.sleep(300)  # Wait 5 minutes
                else:
                    time.sleep(30)  # Wait 30 seconds
            else:
                time.sleep(15)  # Wait 15 seconds
                print("Error in main loop:")
        
        
            time.sleep(30)  # Wait 30 seconds before retrying
    driver.quit()

# Example usage
if __name__ == "__main__":
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
        "https://tonybet.com/cl/live/league-of-legends"
    ]
    scrape_full_structure(urls)
