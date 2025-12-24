import os
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError
from playwright_stealth import Stealth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL = os.getenv("STRAVA_EMAIL")
PASSWORD = os.getenv("STRAVA_PASSWORD")

if not EMAIL or not PASSWORD:
    print("Error: STRAVA_EMAIL and STRAVA_PASSWORD must be set in .env file.")
    exit(1)

def login(page):
    print("Navigating to Strava login page...")
    page.goto("https://www.strava.com/login")
    
    # Apply stealth to avoid bot detection
    stealth = Stealth(media_codecs=False) # Disable specific codec evasion if it causes issues, but keep others
    stealth.apply_stealth_sync(page)
    
    # Block media resources to prevent video player crash (TypeError: setMuted)
    page.route("**/*.{mp4,webm,mp3,wav,ogg}", lambda route: route.fulfill(status=200, body=b""))

    # Handle Cookie Banner automatically whenever it appears
    # This is much more robust for banners that appear late
    # Handle Cookie Banner manually
    # This is more robust than add_locator_handler which can get stuck waiting for the element to hide
    def handle_cookie_banner(page):
        time.sleep(2)
        print("Checking for cookie banner...")
        try:
            # Strava often uses a "Accept All" button in a modal
            # Selectors based on common cookie banner text
            cookie_btn = page.locator("button:has-text('Accept All'), button:has-text('Accept Cookies'), #onetrust-accept-btn-handler, #CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            if cookie_btn.count() > 0 and cookie_btn.first.is_visible(timeout=2000):
                print(f"Cookie banner detected. Accepting...")
                cookie_btn.first.click()
                print("Cookie banner accepted.")
                time.sleep(1) # Wait for banner to disappear
            else:
                print("No cookie banner found or already accepted.")
        except Exception as e:
            print(f"Cookie banner check skipped or failed: {e}")

    handle_cookie_banner(page)

    print("Filling email...")
    # Wait for email field
    # Strava login page often has two email fields (desktop/mobile), we need the visible one
    email_selector = "input[name='email']:visible" 
    page.wait_for_selector(email_selector)
    
    # Human-like typing for email
    email_field = page.locator(email_selector)
    email_field.click()
    # Use press_sequentially for reliable typing
    email_field.press_sequentially(EMAIL, delay=100)
    
    print("Email field filled.")
    
    print("Waiting before submitting...")
    time.sleep(1)
    
    print("Pressing Enter to submit email...")
    page.keyboard.press("Enter")

    # Check for "Unexpected error" which often happens with bots
    try:
        page.wait_for_load_state("networkidle", timeout=3000)
    except:
        pass
        
    if "An unexpected error occurred. Please try again." in page.locator("body").text_content():
        print("CRITICAL: 'Unexpected error' detected on page!")
        page.screenshot(path="error_page.png")
        with open("error_page.html", "w") as f:
            f.write(page.content())
        
        # Retry logic: refresh and try again
        print("Refreshing and retrying...")
        page.reload()
        page.wait_for_load_state("domcontentloaded")
        
        email_input = page.locator("input[name='email']:visible")
        email_input.click()
        email_input.press_sequentially(EMAIL, delay=100)
            
        time.sleep(1)
        print("Pressing Enter to submit email...")
        page.keyboard.press("Enter")

    # Wait for "Use password instead" button
    print("Waiting for 'Use password instead' button...")
    try:
        # Wait up to 10 seconds for the button to appear
        # Use :visible to ensure we don't pick up hidden mobile buttons
        password_choice_btn = page.locator("button:has-text('Use password instead'):visible, button:has-text('Log in with password'):visible")
        password_choice_btn.first.wait_for(state="visible", timeout=10000)
        print("Found 'Use password instead' button. Clicking...")
        time.sleep(random.uniform(1.0, 2.0))
        password_choice_btn.first.click()
        # Removed wait_for_load_state("networkidle") as it causes unnecessary timeouts
    except Exception as e:
        print(f"'Use password instead' button not found or timed out: {e}")
        print("Checking if we are already on the password screen...")

    print("Waiting for password field...")
    # Use a more specific selector for the password input on the password page
    # The previous page might still be in DOM, so we ensure we get the visible one
    password_selector = "input[name='password']:visible"
    try:
        time.sleep(2)
        page.wait_for_selector(password_selector, timeout=10000)
        
        print("Filling password...")
        # Human-like typing for password
        password_field = page.locator(password_selector)
        password_field.click()
        password_field.press_sequentially(PASSWORD, delay=100)
        
        # Trigger input events to ensure the form detects the value
        page.locator(password_selector).dispatch_event("input")
        page.locator(password_selector).dispatch_event("change")
        
        # Random delay and mouse movement
        time.sleep(random.uniform(1.0, 2.0))
        page.mouse.move(random.randint(0, 500), random.randint(0, 500))
        time.sleep(random.uniform(0.5, 1.0))
        
        print("Logging in...")
        # The login button on the password page is usually type="submit"
        submit_btn = page.locator("button[type='submit']:visible")
        
        # Check if enabled
        if not submit_btn.is_enabled():
            print("Submit button disabled. Trying to enable it...")
            page.keyboard.press("Tab")
            time.sleep(1)
            page.keyboard.press("Enter")
        else:
            # Move mouse to button before clicking
            box = submit_btn.bounding_box()
            if box:
                page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                time.sleep(random.uniform(1.0, 2.0))
            submit_btn.click()

        # Check for immediate error after submission
        try:
            # Wait a bit for server response
            time.sleep(2)
            error_msg = page.locator("#flashMessage")
            if error_msg.is_visible():
                text = error_msg.text_content()
                print(f"Login failed with error: {text}")
        except Exception:
            pass

        # Wait for navigation to dashboard
        try:
            page.wait_for_url("**/dashboard", timeout=20000, wait_until="domcontentloaded")
        except Exception:
            print("Warning: Login navigation timed out. Checking if we are on dashboard...")
            if "Dashboard" in page.title():
                print("We are on the dashboard. Proceeding.")
            else:
                raise

        print("Successfully logged in!")
        
        try:
            # Debug: Listen for console logs - Moved to main()
            
            print(f"User Agent: {page.evaluate('navigator.userAgent')}")

            # Wait for the feed to load
            print("Waiting for feed container...")
            page.wait_for_load_state("networkidle", timeout=15000)
            page.wait_for_selector(".dashboard-mfe", timeout=15000)
            # Wait a bit more for React to hydrate
            time.sleep(5)
            
            # Check if the feed container has content
            feed_html = page.inner_html(".dashboard-mfe")
            if not feed_html.strip():
                print("CRITICAL: .dashboard-mfe is empty! React failed to render.")
            
            page.wait_for_selector('button[data-testid="kudos_button"]', timeout=15000)
        except Exception as e:
            print(f"Warning: Feed might not have loaded correctly: {e}")
            with open("feed_load_fail.html", "w", encoding="utf-8") as f:
                f.write(page.content())

    except TimeoutError:
        print("Password field not found or login failed. Dumping page content.")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        page.screenshot(path="login_failed.png")
        raise
    except Exception as e:
        print(f"An error occurred during password submission: {e}")
        page.screenshot(path="login_error.png")
        raise

def give_kudos(page):
    print("Scanning feed for activities...")
    # Scroll down a bit to load more activities
    time.sleep(2)
    for _ in range(3):
        page.mouse.wheel(0, 1000)
        time.sleep(random.uniform(1.0, 2.0))

    # Select all unclicked kudos buttons
    # Note: Selectors might change, need to be robust. 
    # Usually buttons with 'fill-orange-brand' are already clicked (or similar class).
    # Unclicked often have a specific test-id or class.
    # Strava uses SVG icons for kudos.
    
    # Strategy: Look for buttons that are "kudos" buttons and not yet filled.
    # This selector targets the button that contains the empty kudos icon.
    # Adjust selector based on inspection if needed.
    
    # Common selector for kudos button: [data-testid="kudos_button"]
    # If it has        # Re-query buttons after scroll
    kudos_buttons = page.locator('button[data-testid="kudos_button"]')
    count = kudos_buttons.count()
    print(f"Found {count} potential kudos buttons on page.")
    
    if count == 0:
        print("Warning: No kudos buttons found. Dumping page to empty_feed_debug.html")
        with open("empty_feed_debug.html", "w", encoding="utf-8") as f:
            f.write(page.content())
    
    kudos_given = 0
    for i in range(count):
        button = kudos_buttons.nth(i)
        try:
            # Check if already given (look for filled icon inside or class on button)
            # This is a heuristic; might need adjustment based on actual DOM
            if "fill-orange" in button.inner_html():
                print(f"Activity {i+1}: Kudos already given.")
                continue
            
            # Scroll into view
            button.scroll_into_view_if_needed()
            time.sleep(random.uniform(0.5, 1.0))
            
            button.click()
            print(f"Activity {i+1}: Gave kudos!")
            kudos_given += 1
            time.sleep(random.uniform(0.5, 1.5)) # Random delay between clicks
            
        except Exception as e:
            print(f"Error giving kudos to activity {i+1}: {e}")

    print(f"Finished! Gave {kudos_given} new kudos.")

def main():
    with sync_playwright() as p:
        # Launch browser (headless=False for debugging/visibility as requested)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Debug: Listen for console logs immediately
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        try:
            login(page)
            give_kudos(page)
            
            # Keep browser open for a moment to see results
            time.sleep(2)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            page.screenshot(path="error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
