import os
import time
import random
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

async def human_like_typing(page, selector, text, min_delay=50, max_delay=150):
    """Simulate human-like typing with variable speed and occasional mistakes"""
    await page.click(selector)
    await asyncio.sleep(random.uniform(0.5, 1.0))
    
    for char in text:
        # Random typing speed
        delay = random.uniform(min_delay/1000, max_delay/1000)
        await page.type(selector, char, delay=0)
        await asyncio.sleep(delay)
        
        # Occasionally make a typo and correct it (5% chance)
        if random.random() < 0.05:
            # Type a wrong character
            wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            await page.type(selector, wrong_char, delay=0)
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Delete the wrong character
            await page.press(selector, 'Backspace')
            await asyncio.sleep(random.uniform(0.2, 0.4))

async def random_mouse_movement(page, duration=2):
    """Simulate random mouse movements"""
    viewport = await page.viewport_size()
    width, height = viewport['width'], viewport['height']
    
    start_time = time.time()
    while time.time() - start_time < duration:
        x = random.randint(0, width)
        y = random.randint(0, height)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.1, 0.3))

async def enhance_browser_fingerprint(context):
    """Add various scripts to make browser fingerprinting more difficult"""
    # This function will be applied to each new page
    await context.add_init_script("""
    () => {
        // Override properties that detect automation
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'plugins', { 
            get: () => [
                {
                    name: 'Chrome PDF Plugin',
                    filename: 'internal-pdf-viewer',
                    description: 'Portable Document Format'
                },
                {
                    name: 'Chrome PDF Viewer',
                    filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                    description: 'Portable Document Format'
                },
                {
                    name: 'Native Client',
                    filename: 'internal-nacl-plugin',
                    description: ''
                }
            ]
        });
        
        // Override user agent client hints
        if (navigator.userAgentData) {
            Object.defineProperty(navigator.userAgentData, 'brands', {
                get: () => [
                    { brand: 'Not.A.Brand', version: '8' }, 
                    { brand: 'Chromium', version: '114' }, 
                    { brand: 'Google Chrome', version: '114' }
                ]
            });
            
            Object.defineProperty(navigator.userAgentData, 'mobile', {
                get: () => false
            });
        }
        
        // Make detection of automated browser harder
        if (window.chrome) {
            window.chrome.runtime = {};
        }
        
        // Add language settings
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'es']
        });
        
        // Canvas fingerprint diversification
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            if (this.width === 16 && this.height === 16) {
                // Likely a fingerprinting attempt
                const result = originalToDataURL.apply(this, arguments);
                return result.substring(0, result.length - 8) 
                    + (Math.floor(Math.random() * 10000)).toString();
            }
            return originalToDataURL.apply(this, arguments);
        };
    }
    """)

async def main():
    """Enhanced Salesforce login script with advanced bot detection bypass"""
    print("\n=== Enhanced Salesforce Login Script ===\n")
    
    # Get credentials from environment
    url = os.getenv('TARGET_URL', '')
    username = os.getenv('USERNAME', '')
    password = os.getenv('PASSWORD', '')
    
    # Print configuration (with password masked)
    print(f"URL: {url}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    
    async with async_playwright() as p:
        # Launch browser with more realistic settings
        print("\n[1] Launching browser with enhanced settings...")
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--window-size=1920,1080',
                '--start-maximized',
                # Disable password manager popups that can interfere
                '--password-store=basic'
            ]
        )
        
        # Create context with enhanced fingerprinting resistance
        print("[2] Creating stealth browser context...")
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            has_touch=False,
            is_mobile=False,
            locale="en-US",
            timezone_id="America/New_York",
            color_scheme="light",
            reduced_motion="no-preference",
            forced_colors="none",
            
            # HTTP headers to make requests look more natural
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Upgrade-Insecure-Requests": "1"
            }
        )
        
        # Apply browser fingerprint enhancement
        await enhance_browser_fingerprint(context)
        
        # Create page and start session
        page = await context.new_page()
        
        # Enable request interception for any needed modifications
        await page.route("**/*", lambda route: route.continue_())
        
        try:
            # Navigate to login page with caching enabled
            print(f"\n[3] Navigating to Salesforce login: {url}")
            await page.goto(url, wait_until="networkidle")
            
            # Simulate real user behavior: looking at the page
            print("[4] Simulating natural user behavior...")
            await asyncio.sleep(random.uniform(2, 4))
            
            # Move mouse randomly around the page
            await random_mouse_movement(page, 2)
            
            # Check if login form exists
            username_exists = await page.is_visible("#username")
            password_exists = await page.is_visible("#password")
            login_btn_exists = await page.is_visible("#Login")
            
            print(f"\n[5] Login form components check:")
            print(f"  - Username field found: {username_exists}")
            print(f"  - Password field found: {password_exists}")
            print(f"  - Login button found: {login_btn_exists}")
            
            if not (username_exists and password_exists and login_btn_exists):
                print("\n[ERROR] Some login form elements not found!")
                screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshot_dir, f"enhanced_form_not_found_{time.strftime('%Y%m%d_%H%M%S')}.png")
                await page.screenshot(path=screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")
                
                # Print page content for debugging
                content = await page.content()
                print("\nPage HTML content (first 500 chars):")
                print(content[:500] + "...")
                
            else:
                # Simulate a human-like interaction pattern
                print("\n[6] Filling login form with human-like behavior...")
                
                # Look at username field first
                await page.hover("#username")
                await asyncio.sleep(random.uniform(0.5, 1.0))
                
                # Type username with human-like variations
                print("  - Typing username with human-like pattern...")
                await human_like_typing(page, "#username", username)
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                # Tab to password field sometimes, click other times
                if random.random() < 0.5:
                    await page.press("#username", "Tab")
                    await asyncio.sleep(random.uniform(0.3, 0.7))
                else:
                    await page.hover("#password")
                    await asyncio.sleep(random.uniform(0.3, 0.7))
                    await page.click("#password")
                
                # Type password with human-like variations
                print("  - Typing password with human-like pattern...")
                await human_like_typing(page, "#password", password)
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                # Take screenshot before clicking login
                screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshot_dir, f"enhanced_before_login_{time.strftime('%Y%m%d_%H%M%S')}.png")
                await page.screenshot(path=screenshot_path)
                print(f"  - Screenshot saved before login: {screenshot_path}")
                
                # Hover over login button first (like a human would)
                await page.hover("#Login")
                await asyncio.sleep(random.uniform(0.3, 0.8))
                
                # Click login button
                print("\n[7] Clicking login button...")
                await page.click("#Login", delay=random.randint(10, 50))
                
                # Wait for navigation/login process in a more human-like way
                print("[8] Waiting for login process to complete...")
                try:
                    # Wait for navigation or timeout after 15 seconds
                    await page.wait_for_navigation(timeout=15000)
                except:
                    print("  - Navigation timeout - checking page state...")
                
                # Add another wait to ensure page is settled
                await asyncio.sleep(random.uniform(3, 5))
                
                # Analyze post-login state
                print("\n[9] Checking post-login state:")
                current_url = page.url
                print(f"  - Current URL: {current_url}")
                
                # Take screenshot after login attempt
                screenshot_path = os.path.join(screenshot_dir, f"enhanced_after_login_{time.strftime('%Y%m%d_%H%M%S')}.png")
                await page.screenshot(path=screenshot_path)
                print(f"  - Screenshot saved after login: {screenshot_path}")
                
                # Check for specific success indicators
                success_selectors = [
                    ".setupcontent", 
                    "#setupPanel", 
                    "header.flexipageHeader",
                    ".slds-global-header",  # Lightning UI header
                    ".oneHeader",  # Another Lightning UI indicator
                    "#oneHeader",  # Another header variation
                    ".desktop.container"  # Salesforce classic container
                ]
                success_detected = False
                
                print("\n[10] Checking for login success indicators:")
                for selector in success_selectors:
                    try:
                        found = await page.is_visible(selector, timeout=1000)
                        print(f"  - '{selector}' found: {found}")
                        if found:
                            success_detected = True
                    except:
                        print(f"  - '{selector}' not found or error checking")
                
                # Extended page analysis for additional clues
                page_title = await page.title()
                print(f"  - Page title: {page_title}")
                
                # Check for common Salesforce URLs
                salesforce_domains = ["lightning.force.com", "salesforce.com/setup", "salesforce.com/home"]
                domain_match = any(domain in current_url for domain in salesforce_domains)
                if domain_match:
                    success_detected = True
                    print(f"  - Salesforce domain detected in URL: {current_url}")
                
                if success_detected:
                    print("\n✅ SUCCESS: Login appears successful!")
                else:
                    print("\n❌ Login verification failed - No success indicators found")
                    
                    # Check for error messages
                    for error_selector in ["#error", ".loginError", ".error", "#errorDiv"]:
                        error_msg = await page.is_visible(error_selector)
                        if error_msg:
                            error_text = await page.text_content(error_selector)
                            print(f"\nError message found: {error_text}")
                            break
            
            # Wait for user to inspect
            print("\n[11] Enhanced login session complete.")
            print("Checking for security challenges or additional verifications...")
            
            # Look for common challenge/verification elements
            challenge_selectors = [
                "#smc", # Security code challenge
                "#emc", # Email verification
                "#challenge", # Generic challenge
                "#verification", # Generic verification
                "input[name=verificationCode]" # Verification code input
            ]
            
            for selector in challenge_selectors:
                if await page.is_visible(selector):
                    print(f"⚠️ ADDITIONAL VERIFICATION REQUIRED: '{selector}' detected")
                    print("The login process requires additional verification steps.")
                    break
            
            print("\nThe browser will stay open for 60 seconds for inspection...")
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"\n[ERROR] Exception occurred: {e}")
            
            # Take error screenshot
            try:
                screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshot_dir, f"enhanced_error_{time.strftime('%Y%m%d_%H%M%S')}.png")
                await page.screenshot(path=screenshot_path)
                print(f"Error screenshot saved to: {screenshot_path}")
            except:
                print("Could not save error screenshot")
        
        finally:
            print("\nClosing browser...")
            await browser.close()
            print("Enhanced login session ended.")


if __name__ == "__main__":
    asyncio.run(main()) 