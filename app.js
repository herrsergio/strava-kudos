const puppeteer = require('puppeteer');

let StravaURL = 'https://www.strava.com/login/';
let kudosBtns = [];
const KUDOS_INTERVAL = 1000; // in milliseconds
const KUDOS_LOCKOUT = 100; // https://github.com/o2dazone/StravaKudos/issues/13#issuecomment-356319221
let viewingAthleteId, els = '[data-testid=\'unfilled_kudos\']';

// https://intoli.com/blog/scrape-infinite-scroll/

async function extractItems(page) {
  console.log('Inside the extractItems');
  const items = [];
  try {
    const extractedElements = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('[data-testid="activity-feed-card"]'), element => element.innerText);
    });

    items.push(...extractedElements);
  } catch (e) {
    console.log(e);
  }

  return items;
}

async function scrapeInfiniteScrollItems(page, extractItems, itemTargetCount, scrollDelay = 10000) {
  console.log('Dentro de scrapeInfiniteScrollItems');
  let counter = 1;
  let items = [];
  try {
    let previousHeight;

    while (items.length < itemTargetCount) {
      await page.evaluate(() => {
        document.querySelectorAll('[data-testid="kudos_button"]').forEach(node => node.click());
      });
      console.log('Giving kudos for page %d', counter);
      console.log('items.length = %d, itemTargetCount = %d', items.length, itemTargetCount);
      items = await extractItems(page);
      previousHeight = await page.evaluate('document.body.scrollHeight');
      await page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
      await page.waitForFunction(`document.body.scrollHeight > ${previousHeight}`);
      await page.waitFor(scrollDelay);
      counter++;
    }
  } catch (e) {
    console.log(e);
  }
  return items;
}

(async () => {
  const browser = await puppeteer.launch({
    // For MacOs
    //executablePath: '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome',
    headless: true
  });
  console.log('Opening browser');
  const page = await browser.newPage();
  await page.setViewport({
    width: 1920,
    height: 926
  });
  await page.goto(StravaURL);
  console.log('Login into %s', StravaURL);

  await page.type('#email', 'youremail@email.com');
  await page.type('#password', 'yourpassword');
  console.log('Inserting user and password');
  await page.click('#login-button');

  await page.waitForNavigation();

  console.log('Starting giving kudos');
  const items = await scrapeInfiniteScrollItems(page, extractItems, 5);

  await browser.close();
})();
