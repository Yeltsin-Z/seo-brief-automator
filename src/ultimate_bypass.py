import os
import time
import random
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

# Define the configuration
STRATEGIES = {
    "HUMAN_BEHAVIOR": True,     # Human-like typing and mouse movements
    "FINGERPRINT_SPOOFING": True,  # Browser fingerprint manipulation
    "COOKIE_PERSISTENCE": True,    # Save and reuse cookies
    "HEADERS_MANIPULATION": True,  # Modify request headers
    "PRE_WARM": True,              # Pre-warm connection to domain
    "RANDOMIZATION": True,         # Add randomness to actions
    "EXTENDED_VERIFICATION": True  # Better validation of success/failure
}

# Collection of realistic user agents
USER_AGENTS = [
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15",
]

# Path management
COOKIE_PATH = Path(__file__).parent.parent / "data" / "cookies.json"
COOKIE_PATH.parent.mkdir(exist_ok=True)
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

class UltimateBypass:
    def __init__(self):
        self.url = os.getenv('TARGET_URL', '')
        self.username = os.getenv('USERNAME', '')
        self.password = os.getenv('PASSWORD', '')
        self.user_agent = random.choice(USER_AGENTS)
        self.start_time = time.time()
        print("\n=== Ultimate Salesforce Login Bypass ===\n")
        self._log_config()
    
    def _log_config(self):
        """Log configuration information"""
        print(f"URL: {self.url}")
        print(f"Username: {self.username}")
        print(f"Password: {'*' * len(self.password)}")
        print(f"User Agent: {self.user_agent}")
        print("\nActive strategies:")
        for strategy, enabled in STRATEGIES.items():
            print(f"  - {strategy}: {'✅' if enabled else '❌'}")
    
    async def take_screenshot(self, page, name):
        """Take a screenshot with timestamp"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        path = SCREENSHOTS_DIR / f"ultimate_{name}_{timestamp}.png"
        await page.screenshot(path=str(path))
        print(f"Screenshot saved: {path}")
    
    async def save_cookies(self, context):
        """Save cookies for future sessions"""
        if not STRATEGIES["COOKIE_PERSISTENCE"]:
            return
        
        cookies = await context.cookies()
        with open(COOKIE_PATH, "w") as f:
            json.dump(cookies, f)
        print(f"Cookies saved to {COOKIE_PATH}")
    
    async def load_cookies(self, context):
        """Load cookies from previous session"""
        if not STRATEGIES["COOKIE_PERSISTENCE"] or not COOKIE_PATH.exists():
            return False
        
        try:
            with open(COOKIE_PATH, "r") as f:
                cookies = json.load(f)
            
            # Filter out expired cookies
            now = datetime.now().timestamp()
            valid_cookies = [c for c in cookies if "expires" not in c or c["expires"] > now]
            
            if valid_cookies:
                await context.add_cookies(valid_cookies)
                print(f"Loaded {len(valid_cookies)} cookies from previous session")
                return True
            else:
                print("No valid cookies found")
        except Exception as e:
            print(f"Error loading cookies: {e}")
        
        return False
    
    async def delay_with_jitter(self, base_delay=1.0, jitter_factor=0.25):
        """Add natural timing variations"""
        if not STRATEGIES["RANDOMIZATION"]:
            await asyncio.sleep(base_delay)
            return
        
        jitter = random.uniform(-jitter_factor, jitter_factor) * base_delay
        delay = max(0.1, base_delay + jitter)
        await asyncio.sleep(delay)
    
    async def human_typing(self, page, selector, text):
        """Simulate human-like typing"""
        if not STRATEGIES["HUMAN_BEHAVIOR"]:
            await page.fill(selector, text)
            return
        
        await page.click(selector)
        await self.delay_with_jitter(0.8)
        
        # First clear the field if needed
        await page.fill(selector, "")
        await self.delay_with_jitter(0.5)
        
        for char_idx, char in enumerate(text):
            # Randomize typing speed
            typing_delay = random.uniform(0.08, 0.2) 
            
            # Occasional longer pause
            if char_idx > 0 and random.random() < 0.08:
                await self.delay_with_jitter(random.uniform(0.5, 1.2))
            
            # Type the character
            await page.type(selector, char, delay=0)
            await self.delay_with_jitter(typing_delay)
            
            # Occasionally make a mistake (3% chance)
            if STRATEGIES["RANDOMIZATION"] and random.random() < 0.03:
                # Type a wrong character
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                await page.type(selector, wrong_char, delay=0)
                await self.delay_with_jitter(0.3)
                
                # Delete the wrong character
                await page.press(selector, 'Backspace')
                await self.delay_with_jitter(0.4)
                
                # Type the correct character again
                await page.type(selector, char, delay=0)
    
    async def random_mouse_movements(self, page, num_moves=5):
        """Simulate natural mouse movements"""
        if not STRATEGIES["HUMAN_BEHAVIOR"]:
            return
            
        viewport = await page.viewport_size()
        width, height = viewport['width'], viewport['height']
        
        for _ in range(random.randint(3, num_moves)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            await page.mouse.move(x, y)
            await self.delay_with_jitter(random.uniform(0.2, 0.5))
    
    async def enhance_browser_fingerprint(self, context):
        """Apply advanced fingerprint masking"""
        if not STRATEGIES["FINGERPRINT_SPOOFING"]:
            return
            
        await context.add_init_script("""
        () => {
            // Override navigator properties
            const overrideProperties = {
                webdriver: undefined,
                languages: ['en-US', 'en'],
                platform: 'MacIntel',
                hardwareConcurrency: 8,
                deviceMemory: 8,
                userActivation: {hasBeenActive: true, isActive: true},
                scheduling: {isInputPending: () => false},
                credentials: {preventSilentAccess: () => Promise.resolve(true)}
            };
            
            // Apply all overrides
            for (const [key, value] of Object.entries(overrideProperties)) {
                if (key in Navigator.prototype) {
                    Object.defineProperty(Navigator.prototype, key, {
                        get: () => value
                    });
                }
            }
            
            // Plugins
            if ('plugins' in Navigator.prototype) {
                Object.defineProperty(Navigator.prototype, 'plugins', {
                    get: () => {
                        const plugins = [
                            {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                            {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format'},
                            {name: 'Native Client', filename: 'internal-nacl-plugin', description: 'Native Client Executable'}
                        ];
                        
                        // Make it iterable
                        plugins.forEach((plugin, i) => {
                            Object.defineProperty(plugins, i, {
                                value: plugin,
                                enumerable: true
                            });
                        });
                        
                        // Add functions
                        plugins.namedItem = name => plugins.find(p => p.name === name) || null;
                        plugins.refresh = () => {};
                        plugins.item = i => plugins[i] || null;
                        plugins.length = plugins.length;
                        
                        return plugins;
                    }
                });
            }
            
            // Override WebGL fingerprinting
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // UNMASKED_VENDOR_WEBGL or UNMASKED_RENDERER_WEBGL
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return originalGetParameter.call(this, parameter);
            };
            
            // Add some randomization to canvas fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const result = originalToDataURL.apply(this, arguments);
                
                // Only modify if likely fingerprinting (small canvas)
                if (this.width <= 16 && this.height <= 16) {
                    const randChar = Math.floor(Math.random() * 10);
                    return result.replace(/.$/, randChar);
                }
                
                return result;
            };
            
            // Chrome object
            if (window.chrome) {
                window.chrome.runtime = {
                    // Add expected properties and methods
                    connect: () => ({
                        postMessage: () => {},
                        disconnect: () => {}
                    }),
                    sendMessage: () => {}
                };
            }
            
            // Permission behavior
            const originalQuery = Permissions.prototype.query;
            Permissions.prototype.query = function(options) {
                return originalQuery.call(this, options)
                    .then(result => {
                        if (options.name === 'notifications') {
                            result.state = 'prompt';
                        }
                        return result;
                    });
            };
        }
        """)
    
    async def pre_warm_connection(self, page):
        """Pre-warm connection to domain before actual login"""
        if not STRATEGIES["PRE_WARM"]:
            return
            
        try:
            # Extract domain
            domain_parts = self.url.split('/')
            domain_root = f"{domain_parts[0]}//{domain_parts[2]}/"
            
            if domain_root != self.url:
                print(f"Pre-warming connection to: {domain_root}")
                await page.goto(domain_root, wait_until="domcontentloaded")
                await self.delay_with_jitter(1.0)
                
                # Make some random mouse movements
                await self.random_mouse_movements(page, 3)
        except Exception as e:
            print(f"Error during pre-warming: {e}")
    
    async def check_success(self, page):
        """Advanced success detection"""
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        # Take screenshot
        await self.take_screenshot(page, "post_login")
        
        # Get page title
        try:
            page_title = await page.title()
            print(f"Page title: {page_title}")
        except:
            page_title = ""
        
        # Success indicators - check various Salesforce UI elements
        success_selectors = [
            ".slds-global-header",      # Lightning UI header
            ".oneHeader",               # Another Lightning UI indicator
            "#oneHeader",               # Another header variation
            ".desktop.container",       # Salesforce classic container
            ".setupcontent",            # Setup content
            "#setupPanel",              # Setup panel
            "header.flexipageHeader",   # Flex page header
            "#home_Tab",                # Home tab
            ".sidebarModule",           # Sidebar module in classic
            "[data-aura-class]"         # Any Aura component (Lightning)
        ]
        
        # Check for success indicators
        success_detected = False
        for selector in success_selectors:
            try:
                if await page.is_visible(selector, timeout=1000):
                    print(f"Success indicator found: {selector}")
                    success_detected = True
                    break
            except:
                pass
        
        # Check URL patterns that indicate success
        sf_domains = [
            "lightning.force.com", 
            "/home/", 
            "/setup/", 
            "salesforce.com/home", 
            "salesforce.com/setup", 
            "my.salesforce.com",
            "salesforce.com/_ui",
            "/lightning/",
            "/one/"
        ]
        
        if not success_detected and any(domain in current_url for domain in sf_domains) and "login" not in current_url:
            success_detected = True
            print(f"Success detected via URL pattern: {current_url}")
        
        # Check for common success terms in title
        success_title_terms = ["Home", "Salesforce -", "Setup", "Lightning", "- Salesforce", "Service Console"]
        if not success_detected and any(term in page_title for term in success_title_terms):
            success_detected = True
            print(f"Success detected via page title: {page_title}")
        
        # If unsuccessful, check for error messages or security verification
        if not success_detected:
            print("Login verification failed - checking error messages")
            
            # Check for error messages
            error_selectors = ["#error", ".loginError", ".error", "#errorDiv", "#theloginerror", ".uiOutputRichText"]
            error_found = False
            
            for selector in error_selectors:
                if await page.is_visible(selector):
                    error_text = await page.text_content(selector)
                    print(f"Error message found: {error_text.strip()}")
                    error_found = True
                    break
            
            # Check for security verification
            verification_selectors = [
                "#smc",                      # Security code challenge
                "#emc",                      # Email verification
                "#challenge",                # Generic challenge
                "#verification",             # Generic verification
                "input[name=verificationCode]", # Verification code input
                "#challengeContent",         # Challenge content container
                "#forgotPassword",           # User might need to reset password
                "#usernamegroup",            # Login page sends back to start
                ".challengemeterpanel"       # Challenge meter panel
            ]
            
            for selector in verification_selectors:
                if await page.is_visible(selector):
                    print(f"⚠️ VERIFICATION REQUIRED: '{selector}' detected")
                    print("The login process requires additional verification steps.")
                    await self.take_screenshot(page, "verification_required")
                    break
        
        return success_detected
    
    async def attempt_login(self):
        """Main login method using combined approaches"""
        async with async_playwright() as p:
            # Launch browser with enhanced settings
            print("\n[1] Launching browser with enhanced settings...")
            
            # Setup browser arguments for maximum stealth
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                f'--window-size={1920 + random.randint(-5, 5)},{1080 + random.randint(-5, 5)}',
                '--no-default-browser-check',
                '--disable-sync',
                '--password-store=basic'
            ]
            
            browser = await p.chromium.launch(
                headless=False,
                args=browser_args,
                ignore_default_args=["--enable-automation"]
            )
            
            # Create context with enhanced stealth features
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self.user_agent,
                locale="en-US",
                timezone_id="America/New_York",
                
                # HTTP headers to make requests look more natural
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate", 
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1"
                } if STRATEGIES["HEADERS_MANIPULATION"] else {}
            )
            
            # Apply fingerprint spoofing
            await self.enhance_browser_fingerprint(context)
            
            # Try to load cookies from previous session
            had_cookies = await self.load_cookies(context)
            
            # Create page and begin navigation
            page = await context.new_page()
            
            try:
                # Pre-warm connection to the domain
                await self.pre_warm_connection(page)
                
                # Navigate to the login page with appropriate wait
                print(f"\n[2] Navigating to Salesforce login: {self.url}")
                try:
                    await page.goto(self.url, wait_until="networkidle", timeout=10000)
                except:
                    await page.goto(self.url, wait_until="domcontentloaded")
                    # Still wait a bit for async resources
                    await self.delay_with_jitter(3.0)
                
                await self.take_screenshot(page, "initial_load")
                
                # Check if already logged in with cookies
                if had_cookies:
                    print("[3] Checking if already logged in...")
                    
                    # Look for any success indicators
                    already_logged_in = await self.check_success(page)
                    
                    if already_logged_in:
                        print("✅ Already logged in from previous session cookies!")
                        await self.save_cookies(context)  # Update cookies
                        return True
                    
                    print("Previous session expired - proceeding with login")
                
                # Verify login form is present
                print("\n[4] Verifying login form...")
                username_exists = await page.is_visible("#username")
                password_exists = await page.is_visible("#password")
                login_btn_exists = await page.is_visible("#Login")
                
                print(f"  - Username field found: {username_exists}")
                print(f"  - Password field found: {password_exists}")
                print(f"  - Login button found: {login_btn_exists}")
                
                if not (username_exists and password_exists and login_btn_exists):
                    print("❌ Login form not found. This could be:")
                    print("   - Already logged in but not detected")
                    print("   - Redirect to unexpected page")
                    print("   - Challenge/verification page")
                    
                    # Take screenshot and check what happened
                    await self.take_screenshot(page, "form_not_found")
                    current_url = page.url
                    print(f"Current URL: {current_url}")
                    
                    # Check if we're already successful despite missing form
                    success = await self.check_success(page)
                    if success:
                        return True
                    
                    return False
                
                # Human-like interaction with the page
                print("\n[5] Simulating user browsing behavior...")
                await self.random_mouse_movements(page)
                
                # Sometimes check "Remember me" checkbox
                if STRATEGIES["RANDOMIZATION"]:
                    remember_me = await page.is_visible("#rememberUn")
                    if remember_me and random.random() < 0.6:
                        await page.hover("#rememberUn")
                        await self.delay_with_jitter(0.5)
                        if random.random() < 0.4:
                            await page.click("#rememberUn")
                            await self.delay_with_jitter(0.5)
                
                # Fill the login form
                print("\n[6] Filling login form with human-like behavior...")
                
                # Type username with human-like behavior
                print("  - Typing username...")
                await self.human_typing(page, "#username", self.username)
                await self.delay_with_jitter(random.uniform(0.8, 1.5) if STRATEGIES["RANDOMIZATION"] else 1.0)
                
                # Move to password field - sometimes tab, sometimes click
                if STRATEGIES["HUMAN_BEHAVIOR"] and STRATEGIES["RANDOMIZATION"] and random.random() < 0.4:
                    await page.press("#username", "Tab")
                    await self.delay_with_jitter(0.3)
                else:
                    await page.hover("#password")
                    await self.delay_with_jitter(0.3)
                    await page.click("#password")
                
                # Type password with human-like behavior
                print("  - Typing password...")
                await self.human_typing(page, "#password", self.password)
                await self.delay_with_jitter(random.uniform(0.8, 1.5) if STRATEGIES["RANDOMIZATION"] else 1.0)
                
                # Take screenshot before login
                await self.take_screenshot(page, "before_login")
                
                # Click login button with human-like behavior
                if STRATEGIES["HUMAN_BEHAVIOR"]:
                    await page.hover("#Login")
                    await self.delay_with_jitter(random.uniform(0.3, 0.8))
                
                print("\n[7] Submitting login form...")
                await page.click("#Login", delay=random.randint(20, 80) if STRATEGIES["RANDOMIZATION"] else 0)
                
                # Wait for login process to complete
                print("[8] Waiting for login process to complete...")
                try:
                    await page.wait_for_navigation(timeout=15000)
                except:
                    print("  - Navigation timeout - checking page state...")
                
                # Add another wait to ensure page is fully loaded
                await self.delay_with_jitter(random.uniform(3.0, 5.0) if STRATEGIES["RANDOMIZATION"] else 3.0)
                
                # Check if login was successful
                print("\n[9] Analyzing login result...")
                success = await self.check_success(page)
                
                if success:
                    print("\n✅ SUCCESS: Login successful!")
                    # Save cookies for future use
                    await self.save_cookies(context)
                else:
                    print("\n❌ Login unsuccessful")
                
                # Wait for inspection
                print(f"\n[10] Login attempt complete ({round(time.time() - self.start_time, 1)}s)")
                print("The browser will stay open for 60 seconds for inspection...")
                await asyncio.sleep(60)
                
                return success
                
            except Exception as e:
                print(f"\n[ERROR] Exception occurred: {e}")
                
                # Take error screenshot
                try:
                    await self.take_screenshot(page, "error")
                except:
                    print("Could not save error screenshot")
                
                return False
            
            finally:
                print("\nClosing browser...")
                await browser.close()


async def main():
    """Main function"""
    bypass = UltimateBypass()
    success = await bypass.attempt_login()
    
    if success:
        print("\n✅ Ultimate bypass login completed successfully!")
    else:
        print("\n❌ Ultimate bypass login attempt failed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nLogin attempt interrupted by user.")
        sys.exit(0) 