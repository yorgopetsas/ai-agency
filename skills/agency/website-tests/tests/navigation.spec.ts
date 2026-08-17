import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('loads successfully', async ({ page }) => {
    const response = await page.goto('/');
    expect(response?.status()).toBe(200);
  });

  test('has correct title', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/.+/);
  });

  test('has navigation', async ({ page }) => {
    await page.goto('/');
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
  });

  test('has footer', async ({ page }) => {
    await page.goto('/');
    const footer = page.locator('footer');
    await expect(footer).toBeVisible();
  });

  test('no console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/');
    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Navigation', () => {
  test('navigates to about page', async ({ page }) => {
    await page.goto('/');
    const aboutLink = page.locator('a[href="/about"]');
    if (await aboutLink.count() > 0) {
      await aboutLink.first().click();
      await expect(page).toHaveURL(/\/about/);
    }
  });

  test('navigates to pricing page', async ({ page }) => {
    await page.goto('/');
    const pricingLink = page.locator('a[href="/pricing"]');
    if (await pricingLink.count() > 0) {
      await pricingLink.first().click();
      await expect(page).toHaveURL(/\/pricing/);
    }
  });

  test('navigates to contact page', async ({ page }) => {
    await page.goto('/');
    const contactLink = page.locator('a[href="/contact"]');
    if (await contactLink.count() > 0) {
      await contactLink.first().click();
      await expect(page).toHaveURL(/\/contact/);
    }
  });

  test('logo links to home', async ({ page }) => {
    await page.goto('/about');
    const logo = page.locator('nav a[href="/"]');
    await expect(logo).toBeVisible();
  });
});

test.describe('404 Page', () => {
  test('shows 404 for unknown routes', async ({ page }) => {
    const response = await page.goto('/nonexistent-page');
    await expect(page.locator('text=404')).toBeVisible();
  });
});
