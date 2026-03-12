const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();

    page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
    page.on('pageerror', error => console.log('BROWSER ERROR:', error.message));

    await page.goto('http://localhost:8000');
    console.log("Page loaded");

    await page.waitForTimeout(1000);

    await page.click('#analyze-btn');
    console.log("Clicked analyze");

    await page.waitForTimeout(2000); // Wait for animations/charts

    await browser.close();
})();
