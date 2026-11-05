// Q-Net 원문 접근이 차단되어 공식 확인 전까지 학습용 설정으로 관리한다.
export const PROFILE = {
  name: "양식조리기능사",
  subjects: ["양식 재료관리, 음식조리 및 위생관리"] as const,
  questionCount: 60,
  durationMinutes: 60,
  choiceCount: 4,
  passScore: 60,
  maxScore: 100,
  hasSubjectCutoff: false,
  rulesVerificationStatus: "pending",
  source: "https://www.q-net.or.kr/crf005.do?id=crf00503&jmCd=7910",
  selectionPolicy: "통합 무작위 추출. 숫자 변형 family 우선 1개. 공식 단원별 분포 재현 아님.",
  storageKey: "western-cook-cbt:v1",
} as const;
