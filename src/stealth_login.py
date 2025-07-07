import os
import time
import random
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

# Collection of realistic user agents
USER_AGENTS = [
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:110.0) Gecko/20100101 Firefox/116.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    # Edge on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
]

# Cookie management
def get_cookie_path():
    """Get path to store cookies"""
    cookie_dir = Path(__file__).parent.parent / "data"
    cookie_dir.mkdir(exist_ok=True)
    return cookie_dir / "cookies.json"

async def save_cookies(context):
    """Save cookies from current session"""
    cookies = await context.cookies()
    cookie_path = get_cookie_path()
    with open(cookie_path, "w") as f:
        json.dump(cookies, f)
    print(f"Cookies saved to {cookie_path}")

async def load_cookies(context):
    """Load cookies from previous session if available"""
    cookie_path = get_cookie_path()
    if cookie_path.exists():
        try:
            with open(cookie_path, "r") as f:
                cookies = json.load(f)
            
            # Filter out expired cookies
            now = datetime.now().timestamp()
            valid_cookies = [c for c in cookies if "expires" not in c or c["expires"] > now]
            
            if valid_cookies:
                await context.add_cookies(valid_cookies)
                print(f"Loaded {len(valid_cookies)} cookies from previous session")
                return True
        except Exception as e:
            print(f"Error loading cookies: {e}")
    
    print("No valid cookies found or could not load cookies")
    return False

async def delay_with_jitter(base_delay=1.0, jitter_factor=0.25):
    """Sleep with randomized jitter to appear more human-like"""
    jitter = random.uniform(-jitter_factor, jitter_factor) * base_delay
    delay = max(0.1, base_delay + jitter)  # Ensure minimum delay of 0.1s
    await asyncio.sleep(delay)

class SalesforceStealthLogin:
    def __init__(self):
        self.url = os.getenv('TARGET_URL', '')
        self.username = os.getenv('USERNAME', '')
        self.password = os.getenv('PASSWORD', '')
        self.user_agent = random.choice(USER_AGENTS)
        self.screenshots_dir = Path(__file__).parent.parent / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
    
    async def take_screenshot(self, page, name):
        """Take a screenshot with proper naming"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        path = self.screenshots_dir / f"stealth_{name}_{timestamp}.png"
        await page.screenshot(path=str(path))
        print(f"Screenshot saved: {path}")
        return path
    
    async def human_typing(self, page, selector, text):
        """Human-like typing with variable speed and occasional corrections"""
        await page.click(selector)
        await delay_with_jitter(1.0)
        
        for char_idx, char in enumerate(text):
            # Variable typing speed with occasional "thinking" pauses
            if char_idx > 0 and random.random() < 0.1:
                # Occasionally pause longer as if thinking
                await delay_with_jitter(random.uniform(0.5, 1.5))
            else:
                # Normal typing delay
                typing_delay = random.uniform(0.05, 0.2)
                await delay_with_jitter(typing_delay)
            
            # Type the character
            await page.type(selector, char, delay=0)
            
            # Occasionally make a mistake and correct it (3% chance)
            if random.random() < 0.03:
                # Type a wrong character
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                await page.type(selector, wrong_char, delay=0)
                await delay_with_jitter(0.3)
                
                # Delete the wrong character
                await page.press(selector, 'Backspace')
                await delay_with_jitter(0.3)
                
                # Retype the correct character with a longer thinking delay
                await delay_with_jitter(0.5)
                await page.type(selector, char, delay=0)
    
    async def setup_stealth_context(self, browser):
        """Create a browser context with enhanced stealth features"""
        print(f"Setting up stealth context with user agent: {self.user_agent}")
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.user_agent,
            locale="en-US",
            timezone_id="America/New_York",
            
            # HTTP headers that make requests appear more natural
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate", 
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            }
        )
        
        # Add stealth scripts
        await context.add_init_script("""
        () => {
            // Override properties that detect automation
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            
            // Add plugins
            Object.defineProperty(navigator, 'plugins', { 
                get: () => {
                    const plugins = [
                        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format' },
                        { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
                    ];
                    
                    // Make plugins iterable
                    plugins.forEach((plugin, i) => {
                        Object.defineProperty(plugins, i, {
                            value: plugin,
                            enumerable: true
                        });
                    });
                    
                    plugins.namedItem = name => plugins.find(p => p.name === name) || null;
                    plugins.refresh = () => {};
                    plugins.item = idx => typeof idx === 'number' ? plugins[idx] : null;
                    plugins.length = plugins.length;
                    return plugins;
                }
            });
            
            // Add language settings
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Add mimeTypes
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => {
                    const mimeTypes = [
                        { type: 'application/pdf', suffixes: 'pdf', description: '', enabledPlugin: { name: 'Chrome PDF Plugin' } },
                        { type: 'application/x-google-chrome-pdf', suffixes: 'pdf', description: 'Portable Document Format', enabledPlugin: { name: 'Chrome PDF Viewer' } },
                        { type: 'application/x-nacl', suffixes: '', description: 'Native Client Executable', enabledPlugin: { name: 'Native Client' } }
                    ];
                    
                    mimeTypes.namedItem = name => mimeTypes.find(m => m.type === name) || null;
                    mimeTypes.item = idx => typeof idx === 'number' ? mimeTypes[idx] : null;
                    mimeTypes.length = mimeTypes.length;
                    return mimeTypes;
                }
            });
            
            // Add chrome runtime
            if (window.chrome) {
                window.chrome.app = {
                    InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
                    RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' },
                    getDetails: () => null,
                    getIsInstalled: () => false,
                    runningState: () => 'cannot_run'
                };
                
                window.chrome.runtime = {
                    OnInstalledReason: { CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update' },
                    OnRestartRequiredReason: { APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic' },
                    PlatformArch: { ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
                    PlatformNaclArch: { ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
                    PlatformOs: { ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win' },
                    RequestUpdateCheckStatus: { NO_UPDATE: 'no_update', THROTTLED: 'throttled', UPDATE_AVAILABLE: 'update_available' }
                };
            }
            
            // Random modification to WebGL parameters
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
        }
        """)
        
        # Attempt to load cookies from previous session
        has_cookies = await load_cookies(context)
        return context, has_cookies
    
    async def navigate_with_preloading(self, page):
        """Navigate with preloading and caching behavior like a real browser"""
        print(f"Navigating to: {self.url}")
        
        # First make a request to domain root to establish connection and get cookies
        domain_parts = self.url.split('/')
        domain_root = f"{domain_parts[0]}//{domain_parts[2]}/"
        
        if domain_root != self.url:
            print(f"Pre-connecting to domain root: {domain_root}")
            await page.goto(domain_root, wait_until="domcontentloaded")
            await delay_with_jitter(1.5)
        
        # Now navigate to actual URL with proper wait conditions
        print(f"Navigating to target URL: {self.url}")
        
        try:
            # Try to wait for networkidle first for 10 seconds
            await page.goto(self.url, wait_until="networkidle", timeout=10000)
        except:
            # If timeout, use domcontentloaded instead
            print("Network not idle after 10s, waiting for DOM content loaded...")
            await page.goto(self.url, wait_until="domcontentloaded")
            # Still wait a bit for asynchronous resources
            await delay_with_jitter(3.0)
        
        print("Page loaded")
    
    async def attempt_login(self):
        """Attempt to login to Salesforce with enhanced stealth techniques"""
        print("\n=== Stealth Salesforce Login Attempt ===\n")
        print(f"URL: {self.url}")
        print(f"Username: {self.username}")
        print(f"Password: {'*' * len(self.password)}")
        
        async with async_playwright() as p:
            # Launch browser with enhanced stealth settings
            print("\n[1] Launching browser with stealth settings...")
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--window-size=1920,1080',
                    # Make window size non-standard to avoid fingerprinting
                    f'--window-size={1920 + random.randint(-5, 5)},{1080 + random.randint(-5, 5)}',
                    '--start-maximized',
                    '--no-default-browser-check',
                    '--disable-sync',
                    '--disable-notifications',
                    '--password-store=basic'
                ]
            )
            
            # Set up the stealth context with enhanced privacy features
            context, has_cookies = await self.setup_stealth_context(browser)
            page = await context.new_page()
            
            try:
                # Navigate to the login page
                await self.navigate_with_preloading(page)
                
                # Take a screenshot of initial page state
                await self.take_screenshot(page, "initial_page")
                
                # Check if already logged in (if we had cookies)
                if has_cookies:
                    print("[2] Checking if previous session cookies still valid...")
                    
                    # Check for indicators of already being logged in
                    success_selectors = [".slds-global-header", ".oneHeader", "#oneHeader", ".desktop.container"]
                    already_logged_in = False
                    
                    for selector in success_selectors:
                        if await page.is_visible(selector, timeout=2000):
                            already_logged_in = True
                            break
                    
                    if already_logged_in:
                        print("✅ Already logged in from previous session cookies!")
                        await self.take_screenshot(page, "already_logged_in")
                        return True
                    else:
                        print("Previous cookies expired or invalid, proceeding with login")
                
                # Check if we're on the login page
                login_form_exists = await page.is_visible("#username") and await page.is_visible("#password")
                
                if not login_form_exists:
                    print("[!] Login form not found on current page")
                    print("Current URL:", page.url)
                    
                    # Check if we're on a different page that might require different handling
                    if "verification" in page.url.lower() or "challenge" in page.url.lower():
                        print("⚠️ Detected verification or challenge page!")
                        await self.take_screenshot(page, "verification_challenge")
                        return False
                    
                    # Try to find and click on login links
                    login_links = [
                        "text=Log In", 
                        "text=Login", 
                        "text=Sign In",
                        "[href*='login']",
                        "button:has-text('Log In')"
                    ]
                    
                    for link in login_links:
                        if await page.is_visible(link):
                            print(f"Found login link: {link}, clicking...")
                            await page.click(link)
                            await delay_with_jitter(3.0)
                            
                            # Check again for login form
                            login_form_exists = await page.is_visible("#username") and await page.is_visible("#password")
                            if login_form_exists:
                                break
                
                if not login_form_exists:
                    print("[ERROR] Cannot find login form even after trying login links")
                    await self.take_screenshot(page, "login_form_not_found")
                    return False
                
                # Generate random viewing and interaction pattern to look human
                print("\n[3] Simulating human browsing behavior before login...")
                
                # Look at the page for a bit
                await delay_with_jitter(random.uniform(1.0, 3.0))
                
                # Move mouse randomly around the page
                viewport = await page.viewport_size()
                for _ in range(random.randint(3, 6)):
                    x = random.randint(0, viewport['width'])
                    y = random.randint(0, viewport['height'])
                    await page.mouse.move(x, y)
                    await delay_with_jitter(random.uniform(0.2, 0.7))
                
                # Sometimes hover over remember me checkbox (if exists)
                remember_me = await page.is_visible("#rememberUn")
                if remember_me and random.random() < 0.7:
                    await page.hover("#rememberUn")
                    await delay_with_jitter(0.5)
                    # Sometimes toggle it
                    if random.random() < 0.5:
                        await page.click("#rememberUn")
                        await delay_with_jitter(0.5)
                
                # Focus on username field
                print("\n[4] Filling login form with human-like behavior...")
                await page.hover("#username")
                await delay_with_jitter(0.5)
                
                # Type username with human-like timing
                await self.human_typing(page, "#username", self.username)
                await delay_with_jitter(random.uniform(0.8, 1.5))
                
                # Move to password field - sometimes using tab, sometimes clicking
                if random.random() < 0.4:
                    await page.press("#username", "Tab")
                    await delay_with_jitter(0.3)
                else:
                    await page.hover("#password")
                    await delay_with_jitter(0.3)
                    await page.click("#password")
                
                # Type password with human-like timing
                await self.human_typing(page, "#password", self.password)
                await delay_with_jitter(random.uniform(0.8, 1.5))
                
                # Take screenshot before login
                await self.take_screenshot(page, "before_login")
                
                # Hover over the login button first
                await page.hover("#Login")
                await delay_with_jitter(random.uniform(0.3, 0.8))
                
                # Click login button
                print("\n[5] Clicking login button...")
                await page.click("#Login", delay=random.randint(10, 30))
                
                # Wait for login process with proper handling
                print("[6] Waiting for login process to complete...")
                try:
                    # First try to wait for navigation
                    await page.wait_for_navigation(timeout=10000)
                except:
                    print("Navigation timeout - checking page state...")
                
                # Wait additional time for any redirects or async resources
                await delay_with_jitter(random.uniform(3.0, 5.0))
                
                # Take screenshot after login
                await self.take_screenshot(page, "after_login")
                
                # Check if login was successful
                print("\n[7] Analyzing login result...")
                current_url = page.url
                page_title = await page.title()
                print(f"Current URL: {current_url}")
                print(f"Page title: {page_title}")
                
                # Check for success indicators
                success_selectors = [
                    ".slds-global-header",  # Lightning UI header
                    ".oneHeader",  # Another Lightning UI indicator
                    "#oneHeader",  # Another header variation
                    ".desktop.container",  # Salesforce classic container
                    ".setupcontent", 
                    "#setupPanel", 
                    "header.flexipageHeader"
                ]
                
                success_detected = False
                for selector in success_selectors:
                    try:
                        if await page.is_visible(selector, timeout=1000):
                            print(f"Success indicator found: {selector}")
                            success_detected = True
                            break
                    except:
                        pass
                
                # Also check URL patterns for success
                sf_domains = ["lightning.force.com", "/home/", "/setup/", "salesforce.com/home", 
                             "salesforce.com/setup", "my.salesforce.com"]
                if any(domain in current_url for domain in sf_domains) and "login" not in current_url:
                    success_detected = True
                    print(f"Successful login detected by URL pattern: {current_url}")
                
                # Handle the final result
                if success_detected:
                    print("\n✅ SUCCESS: Login successful!")
                    # Save cookies for future sessions
                    await save_cookies(context)
                    return True
                else:
                    print("\n❌ Login verification failed")
                    
                    # Check for error messages
                    error_selectors = ["#error", ".loginError", ".error", "#errorDiv", "#theloginerror"]
                    for selector in error_selectors:
                        if await page.is_visible(selector):
                            error_text = await page.text_content(selector)
                            print(f"Error message found: {error_text.strip()}")
                            break
                    
                    # Check for additional verification required
                    verification_selectors = [
                        "#smc", # Security code challenge
                        "#emc", # Email verification
                        "#challenge", # Generic challenge
                        "#verification", # Generic verification
                        "input[name=verificationCode]", # Verification code input
                        "#challengeContent" # Challenge content container
                    ]
                    
                    for selector in verification_selectors:
                        if await page.is_visible(selector):
                            print(f"⚠️ ADDITIONAL VERIFICATION REQUIRED: '{selector}' detected")
                            print("The login process requires additional verification steps.")
                            await self.take_screenshot(page, "verification_required")
                            break
                
                # Wait for user to inspect
                print("\n[8] Stealth login attempt complete.")
                print("The browser will stay open for 60 seconds for inspection...")
                await asyncio.sleep(60)
                
                return success_detected
                
            except Exception as e:
                print(f"\n[ERROR] Exception occurred: {e}")
                await self.take_screenshot(page, "error")
                return False
            
            finally:
                print("\nClosing browser...")
                await browser.close()
                print("Stealth login session ended.")


async def main():
    """Main function to run the stealth login"""
    stealth_login = SalesforceStealthLogin()
    success = await stealth_login.attempt_login()
    
    if success:
        print("\n✅ Stealth login completed successfully!")
    else:
        print("\n❌ Stealth login attempt failed.")


if __name__ == "__main__":
    asyncio.run(main()) 