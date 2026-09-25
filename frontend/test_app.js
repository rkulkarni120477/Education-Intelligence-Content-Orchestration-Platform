const playwright = require('playwright');

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:3000');
  await page.waitForLoadState('networkidle');
  
  // Take screenshot
  await page.screenshot({ path: 'app_screenshot.png', fullPage: true });
  console.log('✓ Screenshot taken: app_screenshot.png');
  
  // Get page title
  const title = await page.title();
  console.log('✓ Page Title:', title);
  
  // Get main heading
  const heading = await page.locator('h1').textContent();
  console.log('✓ Main Heading:', heading);
  
  // Check if workflow dropdown exists
  const dropdown = await page.locator('button.w-full').count();
  console.log('✓ Dropdown elements found:', dropdown);
  
  await browser.close();
  console.log('✓ App is running successfully!');
})();
