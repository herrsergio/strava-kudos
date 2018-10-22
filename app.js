const puppeteer = require('puppeteer');

let StravaURL = 'https://www.strava.com/login/';

// https://intoli.com/blog/scrape-infinite-scroll/

function extractItems() {
    //const extractedElements = document.querySelectorAll('#boxes > div.box');
    const extractedElements = document.querySelectorAll('#dashboard-feed');
    const items = [];
    for (let element of extractedElements) {
        items.push(element.innerText);
    }
    return items;
}

async function scrapeInfiniteScrollItems(
  page,
  extractItems,
  itemTargetCount,
  scrollDelay = 10000,
) {
    let counter = 1;
    let items = [];
    try {
        let previousHeight;
        while (items.length < itemTargetCount) {
            await page.evaluate(() => {
                document.querySelectorAll('button.js-add-kudo').forEach(node => node.click())
            });
            console.log('Giving kudos for page %d', counter)
            console.log('items.length = %d, itemTargetCount = %d', items.length, itemTargetCount);
            items = await page.evaluate(extractItems);
            previousHeight = await page.evaluate('document.body.scrollHeight');
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
            await page.waitForFunction(`document.body.scrollHeight > ${previousHeight}`);
            await page.waitFor(scrollDelay);
            counter++;
        }
    } catch(e) { }
    return items;
}


(async () => {
    const browser = await puppeteer.launch({ headless: true});
    console.log('Opening browser')
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 926 });
    await page.goto(StravaURL);
    console.log('Login into %s', StravaURL);

    await page.type( '#email', 'youremail@email.com' );
    await page.type( '#password', 'yourpassword' );
    console.log('Inserting user and password');
    await page.click( '#login-button' );

    await page.waitForNavigation();

    console.log('Starting giving kudos');
    const items = await scrapeInfiniteScrollItems(page, extractItems, 5);

    await browser.close();

})();
