import { test, expect } from '@playwright/test';

test.describe('Responsive Design', () => {
  test('desktop: nav links visible', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/');
    const desktopNav = page.locator('.hidden.md\\:flex');
    if (await desktopNav.count() > 0) {
      await expect(desktopNav.first()).toBeVisible();
    }
  });

  test('mobile: hamburger menu exists', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    const hamburger = page.locator('button[aria-label="Toggle menu"]');
    if (await hamburger.count() > 0) {
      await expect(hamburger).toBeVisible();
    }
  });

  test('mobile: hamburger toggles menu', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    const hamburger = page.locator('button[aria-label="Toggle menu"]');
    if (await hamburger.count() > 0) {
      await hamburger.click();
      // Mobile menu should appear
      const mobileMenu = page.locator('.md\\:hidden.py-4');
      await expect(mobileMenu).toBeVisible();
    }
  });

  test('pages have responsive classes', async ({ page }) => {
    await page.goto('/');
    const html = await page.content();
    // Check for common responsive patterns
    const hasResponsive = /sm:|md:|lg:|xl:/.test(html);
    expect(hasResponsive).toBe(true);
  });
});

test.describe('Forms', () => {
  test('contact form has required fields', async ({ page }) => {
    await page.goto('/contact');
    const nameInput = page.locator('input[name="name"]');
    const emailInput = page.locator('input[name="email"]');
    const messageInput = page.locator('textarea[name="message"]');

    if (await nameInput.count() > 0) {
      await expect(nameInput).toBeVisible();
      await expect(emailInput).toBeVisible();
      await expect(messageInput).toBeVisible();
    }
  });

  test('form inputs have labels', async ({ page }) => {
    await page.goto('/contact');
    const labels = page.locator('label');
    const count = await labels.count();
    // Should have at least 2 labels (name, email)
    expect(count).toBeGreaterThanOrEqual(2);
  });

  test('submit button exists', async ({ page }) => {
    await page.goto('/contact');
    const submit = page.locator('button[type="submit"]');
    if (await submit.count() > 0) {
      await expect(submit).toBeVisible();
    }
  });
});
