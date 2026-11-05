import { test, expect, type Page } from "@playwright/test";

async function touchSwipe(page: Page, fromY: number, toY: number) {
  const client = await page.context().newCDPSession(page);
  await client.send("Emulation.setTouchEmulationEnabled", { enabled: true });
  await client.send("Input.dispatchTouchEvent", {
    type: "touchStart", touchPoints: [{ x: 120, y: fromY }],
  });
  for (let i = 1; i <= 12; i++) {
    await client.send("Input.dispatchTouchEvent", {
      type: "touchMove",
      touchPoints: [{ x: 120, y: fromY + (toY - fromY) * i / 12 }],
    });
    await page.waitForTimeout(20);
  }
  await client.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await client.detach();
}

for (const viewport of [{ width: 390, height: 480 }, { width: 740, height: 360 }]) {
  test(`${viewport.width}×${viewport.height}: 휠·터치로 메뉴 하단과 상단 접근`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto("");
    await page.getByRole("button", { name: "메뉴 열기" }).click();
    const menu = page.locator(".sidebar");
    await expect(menu).toHaveClass(/open/);
    await page.waitForTimeout(250); // Finish the 200 ms slide before input coordinates are used.
    const initialPageY = await page.evaluate(() => window.scrollY);
    expect(await menu.evaluate(el => el.scrollHeight > el.clientHeight)).toBe(true);

    // Wheel input, not assigning scrollTop. Backup must be visible before click auto-scroll.
    await page.mouse.move(120, viewport.height / 2);
    await page.mouse.wheel(0, 1400);
    await expect.poll(() => menu.evaluate(el => el.scrollTop)).toBeGreaterThan(0);
    const backup = page.getByRole("button", { name: "학습 기록 백업", exact: true });
    const reset = page.getByRole("button", { name: "데이터 초기화", exact: true });
    await expect(backup).toBeInViewport();
    await expect(reset).toBeInViewport();
    const downloaded = page.waitForEvent("download");
    await backup.click();
    expect((await downloaded).suggestedFilename()).toBe("western-cook-study-backup.json");
    await reset.click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await page.getByRole("button", { name: "돌아가기", exact: true }).click();
    await page.mouse.move(120, viewport.height / 2);
    await page.mouse.wheel(0, -1800);
    await expect.poll(() => menu.evaluate(el => el.scrollTop)).toBe(0);
    const home = page.getByRole("navigation").getByRole("button", { name: "학습 대시보드", exact: true });
    await expect(home).toBeInViewport();
    await home.click();
    await expect(menu).not.toHaveClass(/open/);

    // Independent touch path: real Chromium touchStart/move/end, not mouse-wheel emulation.
    await page.getByRole("button", { name: "메뉴 열기" }).click();
    await page.waitForTimeout(250);
    for (let i = 0; i < 4; i++) await touchSwipe(page, viewport.height - 55, 70);
    await expect.poll(() => menu.evaluate(el => el.scrollTop)).toBeGreaterThan(0);
    await expect(backup).toBeInViewport();
    await expect(reset).toBeInViewport();
    await page.screenshot({ path: test.info().outputPath("menu-bottom.png") });
    const touchDownload = page.waitForEvent("download");
    const tapSession = await page.context().newCDPSession(page);
    const box = (await backup.boundingBox())!;
    await tapSession.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: box.x + box.width/2, y: box.y + box.height/2 }] });
    await tapSession.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await tapSession.detach();
    await touchDownload;
    for (let i = 0; i < 5; i++) await touchSwipe(page, 70, viewport.height - 55);
    await expect.poll(() => menu.evaluate(el => el.scrollTop)).toBe(0);
    await expect(home).toBeInViewport();
    // CDP makes touch available in the desktop project, but Playwright's tap requires hasTouch.
    await home.click();
    await expect(menu).not.toHaveClass(/open/);
    expect(await page.evaluate(() => window.scrollY)).toBe(initialPageY);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);

    // Enlarged text still preserves independent scrolling and reachable tools.
    await page.addStyleTag({ content: ".sidebar { font-size: 150%; } .sidebar nav button { font-size: 20px; min-height: 65px; }" });
    await page.getByRole("button", { name: "메뉴 열기" }).click();
    await page.waitForTimeout(250);
    await page.mouse.move(120, viewport.height / 2);
    await page.mouse.wheel(0, 3000);
    await expect(reset).toBeInViewport();
    await page.mouse.wheel(0, -3000);
    await expect.poll(() => menu.evaluate(el => el.scrollTop)).toBe(0);
    await expect(home).toBeInViewport();
  });
}
