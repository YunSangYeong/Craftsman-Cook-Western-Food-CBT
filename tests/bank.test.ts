import { describe, expect, it } from "vitest";
import { BASE_BANK as bank, fingerprint, validateQuestion } from "../src/model";
import { PROFILE } from "../src/qualification";

describe("양식 문제은행의 출처·중복·계산 검수", () => {
  it("실등록 1000개: 개념 103개, 수치 변형 897개, 연도·회차 창작 없음", () => {
    expect(bank).toHaveLength(1000);
    expect(new Set(bank.map(q => q.id)).size).toBe(1000);
    expect(new Set(bank.map(fingerprint)).size).toBe(1000);
    expect(bank.filter(q => !q.family)).toHaveLength(103);
    expect(bank.filter(q => q.family)).toHaveLength(897);
    for (const q of bank) {
      expect(() => validateQuestion(q)).not.toThrow();
      expect(q.type).toBe("original");
      expect(q.year).toBeNull();
      expect(q.session).toBeNull();
      expect(q.verificationStatus).toBe("reviewed");
      expect(q.reviewNote).toContain("외부");
    }
  });
  it("공식 확인과 내부 검토를 구분한다", () => {
    expect(PROFILE.rulesVerificationStatus).toBe("pending");
    expect(bank.every(q => q.reviewNote.includes("외부"))).toBe(true);
  });
  for (let family = 1; family <= 15; family++) {
    it(`유형 ${family}: 모든 조건을 독립 역산하고 정답 보기·단위를 확인한다`, () => {
      const qs = bank.filter(q => q.calculation?.kind === String(family));
      expect(qs).toHaveLength(family <= 3 ? 59 : 60);
      expect(new Set(qs.map(q => JSON.stringify(q.calculation!.values))).size).toBe(qs.length);
      for (const q of qs) {
        const { result: r, values: v, unit } = q.calculation!;
        const [a, b, c, d] = v;
        // Inverse relationships, independent from Python Decimal forward generation.
        // Bound the residual by half a displayed hundredth propagated through the equation.
        let actual: number, expected: number, factor: number;
        switch (family) {
          case 1: actual = r*b/c; expected = a; factor = b/c; break;
          case 2: actual = r*b; expected = a; factor = b; break;
          case 3: actual = r*100/b; expected = a; factor = 100/b; break;
          case 4: actual = r*b/100; expected = a; factor = b/100; break;
          case 5: actual = r*a/100; expected = b; factor = a/100; break;
          case 6: actual = r*a/100; expected = b; factor = a/100; break;
          case 7: actual = r*1000/b; expected = a; factor = 1000/b; break;
          case 8: actual = r*b/100; expected = a; factor = b/100; break;
          case 9: actual = r*b/100; expected = a; factor = b/100; break;
          case 10: actual = r*d; expected = a+b+c; factor = d; break;
          case 11: actual = r*100/b; expected = a; factor = 100/b; break;
          case 12: actual = (r+a)*c/100; expected = a*b/100; factor = c/100; break;
          case 13: actual = r*c/100; expected = a*b/100; factor = c/100; break;
          case 14: actual = r-4*a-4*b; expected = 9*c; factor = 1; break;
          case 15: actual = r/1000; expected = a; factor = 1/1000; break;
          default: throw new Error("unknown family");
        }
        expect(Math.abs(actual-expected), q.id).toBeLessThanOrEqual(.005*factor + 1e-8);
        const numbers = q.choices.map(choice => {
          expect(choice.endsWith(` ${unit}`), q.id).toBe(true);
          return Number(choice.slice(0, -unit.length).trim());
        });
        expect(numbers.every(Number.isFinite)).toBe(true);
        expect(new Set(numbers).size).toBe(4);
        expect(numbers[q.answer-1]).toBe(r);
        expect(numbers.filter(n => Math.abs(n-r) < 1e-8)).toHaveLength(1);
        expect(q.explanation).toContain(String(r));
      }
    });
  }
});
