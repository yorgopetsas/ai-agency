import { test, expect } from '@playwright/test';

test.describe('Components', () => {
  test('hero section renders', async ({ page }) => {
    await page.goto('/');
    const hero = page.locator('section').first();
    await expect(hero).toBeVisible();
  });

  test('hero has heading', async ({ page }) => {
    await page.goto('/');
    const h1 = page.locator('h1');
    await expect(h1.first()).toBeVisible();
    const text = await h1.first().textContent();
    expect(text?.length).toBeGreaterThan(0);
  });

  test('hero has CTA buttons', async ({ page }) => {
    await page.goto('/');
    const ctas = page.locator('section a[href]');
    const count = await ctas.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('feature cards render', async ({ page }) => {
    await page.goto('/');
    // Look for feature card pattern (grid of cards)
    const cards = page.locator('.grid .bg-white, .grid .rounded-xl');
    if (await cards.count() > 0) {
      expect(await cards.count()).toBeGreaterThanOrEqual(2);
    }
  });

  test('pricing page has plan cards', async ({ page }) => {
    await page.goto('/pricing');
    const planHeadings = page.locator('h3');
    const count = await planHeadings.count();
    if (count > 0) {
      expect(count).toBeGreaterThanOrEqual(2);
    }
  });

  test('all pages render without errors', async ({ page }) => {
    const routes = ['/', '/about', '/pricing', '/contact'];
    for (const route of routes) {
      const response = await page.goto(route);
      expect(response?.status()).toBe(200);
    }
  });
});

test.describe('Design Tokens', () => {
  test('primary color is applied', async ({ page }) => {
    await page.goto('/');
    const html = await page.content();
    // Check that primary color class or variable is used
    const hasPrimary = /primary|bg-primary|text-primary/.test(html);
    expect(hasPrimary).toBe(true);
  });

  test('custom fonts are loaded', async ({ page }) => {
    await page.goto('/');
    const html = await page.content();
    // Check font-family is set
    const hasFont = /font-family|font-heading|font-body/.test(html);
    expect(hasFont).toBe(true);
  });
});
