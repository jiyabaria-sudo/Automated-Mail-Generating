import argparse
import time
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def parse_args():
    parser = argparse.ArgumentParser(
        description="Automatic Gmail login + compose + send (handles popups and ensures send)"
    )

    parser.add_argument(
        "--email",
        required=True,
        help="Login email ID (e.g., badshah.khalik@associates.scit.edu)",
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Login password for the email ID",
    )
    parser.add_argument(
        "--subject",
        required=True,
        help="Subject of the email",
    )
    parser.add_argument(
        "--body",
        required=True,
        help="Body/content of the email",
    )
    parser.add_argument(
        "--to",
        default="badshah.khalik@associates.scit.edu",
        help="Receiver email address (default: your personal Gmail)",
    )

    return parser.parse_args()


def click_popup_buttons(driver):
    """
    Clicks common Google/Gmail popup buttons like:
    OK, Continue, No thanks, Not now, Skip, Done, Yes, Confirm.
    """
    labels = ["Continue", "No thanks", "Not now", "OK", "Done", "Skip", "Yes", "Confirm"]
    for text in labels:
        try:
            elems = driver.find_elements(
                By.XPATH,
                (
                    "//button[contains(., '{}')]"
                    " | //div[@role='button' and contains(., '{}')]"
                    " | //span[@role='button' and contains(., '{}')]"
                ).format(text, text, text),
            )
            if elems:
                elems[0].click()
                print(f"[INFO] Clicked popup button: {text}")
                time.sleep(1)
        except Exception:
            continue


def login_to_gmail(driver, wait, email, password):
    print("[INFO] Opening Gmail login page...")
    driver.get("https://accounts.google.com/signin/v2/identifier?service=mail")

    # If already logged in
    try:
        print("[INFO] Checking if inbox is already open...")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.T-I.T-I-KE.L3"))
        )
        print("[INFO] Already logged in, skipping login.")
        return
    except Exception:
        print("[INFO] Not logged in, proceeding with email + password...")

    # EMAIL STEP
    email_input = wait.until(
        EC.presence_of_element_located((By.ID, "identifierId"))
    )
    print("[INFO] Typing email...")
    email_input.clear()
    email_input.send_keys(email)
    driver.find_element(By.ID, "identifierNext").click()

    time.sleep(2)
    click_popup_buttons(driver)

    # PASSWORD STEP
    print("[INFO] Waiting for password field...")
    try:
        password_input = wait.until(
            EC.presence_of_element_located((By.NAME, "Passwd"))
        )
    except Exception:
        password_input = wait.until(
            EC.presence_of_element_located((By.NAME, "password"))
        )

    print("[INFO] Typing password...")
    password_input.clear()
    password_input.send_keys(password)
    driver.find_element(By.ID, "passwordNext").click()

    time.sleep(3)
    click_popup_buttons(driver)

    print("[INFO] Waiting for inbox / Gmail to load...")
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.T-I.T-I-KE.L3"))
    )
    print("[INFO] Login successful; inbox loaded.")


def send_with_confirmation(driver, wait):
    """
    Clicks Send button. If that fails, tries Ctrl+Enter.
    Then waits for 'Message sent' confirmation toast.
    """
    print("[INFO] Attempting to click Send button...")
    try:
        send_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='button' and (contains(@aria-label,'Send') or contains(.,'Send'))]")
            )
        )
        send_button.click()
        print("[INFO] Clicked Send button.")
    except Exception as e:
        print("[WARN] Send button click failed, trying Ctrl+Enter shortcut:", e)
        try:
            body_field = driver.find_element(
                By.CSS_SELECTOR, "div[role='textbox']"
            )
            body_field.send_keys(Keys.CONTROL, Keys.ENTER)
            print("[INFO] Sent using Ctrl+Enter.")
        except Exception as e2:
            print("[ERROR] Ctrl+Enter also failed:", e2)
            return

    # Wait for "Message sent" toast
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'Message sent') or contains(text(),'Sent')]")
            )
        )
        print("[INFO] Confirmed: Message sent.")
    except Exception:
        print("[WARN] Could not confirm 'Message sent', but send was attempted.")


def compose_via_url(driver, wait, to_addr, subject, body):
    print("[INFO] Opening Gmail compose view via URL...")
    params = {
        "view": "cm",
        "fs": "1",
        "to": to_addr,
        "su": subject,
        "body": body,
    }
    query = urllib.parse.urlencode(params)
    driver.get("https://mail.google.com/mail/u/0/?" + query)

    # Let page load
    time.sleep(5)
    click_popup_buttons(driver)

    print("[INFO] Waiting for compose textarea to be ready...")
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[role='textbox']")
        )
    )

    send_with_confirmation(driver, wait)


def fallback_compose_shortcut(driver, wait, to_addr, subject, body):
    print("[INFO] Fallback: using 'c' shortcut to open compose...")
    driver.get("https://mail.google.com/mail/u/0/#inbox")
    time.sleep(5)
    click_popup_buttons(driver)

    # Focus body and press 'c' to open compose
    body_element = driver.find_element(By.TAG_NAME, "body")
    body_element.send_keys("c")
    time.sleep(3)

    print("[INFO] Filling email fields in fallback compose...")
    to_field = wait.until(EC.presence_of_element_located((By.NAME, "to")))
    to_field.send_keys(to_addr)

    subject_field = driver.find_element(By.NAME, "subjectbox")
    subject_field.send_keys(subject)

    body_field = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[role='textbox']")
        )
    )
    body_field.click()
    body_field.send_keys(body)

    send_with_confirmation(driver, wait)


def main():
    args = parse_args()

    print("[INFO] Launching Chrome browser...")
    service = Service()
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 120)

    try:
        login_to_gmail(driver, wait, args.email, args.password)
        click_popup_buttons(driver)

        # Try direct compose URL first
        try:
            compose_via_url(driver, wait, args.to, args.subject, args.body)
        except Exception as e1:
            print("[WARN] Compose via URL failed, trying fallback:", e1)
            try:
                fallback_compose_shortcut(
                    driver, wait, args.to, args.subject, args.body
                )
            except Exception as e2:
                print("[ERROR] Fallback compose also failed:", e2)

        print("[INFO] All steps attempted.")
    except Exception as e:
        print("[ERROR] Something went wrong in main flow:", e)
    finally:
        print("[INFO] Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
