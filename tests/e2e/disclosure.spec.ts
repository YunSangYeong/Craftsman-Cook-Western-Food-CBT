import { test, expect } from "@playwright/test";

test("모든 화면의 상단 상시 배너 부재·저장 실패 경고·PC/모바일 화면", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("");
  await expect(page.getByRole("heading", { name: "양식조리기능사 필기 CBT", exact: true })).toBeVisible();
  await page.screenshot({ path: test.info().outputPath("dashboard.png"), fullPage: true });
  for (const label of ["실전 모의시험", "랜덤 문제풀이", "오답노트", "북마크", "학습 통계", "문제은행 관리", "학습 대시보드"]) {
    const open = page.getByRole("button", { name: "메뉴 열기" });
    if (await open.isVisible()) await open.click();
    await page.getByRole("navigation").getByRole("button", { name: label, exact: true }).click();
    await expect(page.locator(".criteria-note")).toHaveCount(0);
    await expect(page.getByLabel("학습 기준")).toHaveCount(0);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
  await page.getByRole("button", { name: "문제풀이 시작하기", exact: true }).click();
  await page.screenshot({ path: test.info().outputPath("practice.png"), fullPage: true });
  // A real storage failure remains actionable despite removal of informational banners.
  await page.evaluate(() => {
    Storage.prototype.setItem = () => { throw new DOMException("quota", "QuotaExceededError"); };
  });
  await page.getByRole("group", { name: "답안 선택" }).getByRole("button").first().click();
  await expect(page.getByRole("alert")).toContainText("기록을 저장하지 못했습니다");
  await expect(page.locator(".criteria-note")).toHaveCount(0);
  expect(errors).toEqual([]);
});
