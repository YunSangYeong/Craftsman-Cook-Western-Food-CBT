"""AI-assisted original bank. No scraped exam questions. Stable IDs and ordering.
Run from repository root: python3 scripts/generate_bank.py
Decimal arithmetic here is independently checked by JS inverse equations in tests.
"""
import csv
import collections
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://github.com/YunSangYeong/Craftsman-Cook-Western-Food-CBT'
SUBJECT = '양식 재료관리, 음식조리 및 위생관리'
D = Decimal

def fmt(n):
    return format(D(str(n)).quantize(D('.01'), rounding=ROUND_HALF_UP).normalize(), 'f')

def make(qid, topic, question, correct, wrong, explanation, family=None, calculation=None):
    choices = [correct, *wrong]
    shift = sum(qid.encode()) % 4
    choices = choices[shift:] + choices[:shift]
    assert len(set(choices)) == 4
    return dict(id=qid, subject=SUBJECT, topic=topic, question=question,
                choices=choices, answer=choices.index(correct)+1, explanation=explanation,
                difficulty='중' if family else '하', year=None, session=None,
                type='original', sourceUrl=SOURCE, verificationStatus='reviewed',
                reviewNote=('AI 일반 지식으로 자체 작성. 문장·정답의 내부 검토. 외부 문헌 대조·전문가 검수 없음.' if not family else
                '자체 제작 계산 변형. 명시된 조건·산술 관계의 내부 검토와 역산 테스트. 외부 전문가·공식 출제기준 대조 없음.'),
                version='western-main', rights='자체 제작 · CC BY 4.0 · AI 보조 작성, 저장소 기여자 표기 및 변경 고지',
                **({'family': family, 'calculation': calculation} if family else {}))

bank=[]
for i,line in enumerate(x for x in (ROOT/'scripts/concepts.txt').read_text().splitlines() if x and not x.startswith('#')):
    topic,q,c,w1,w2,w3,e=line.split('|')
    bank.append(make(f'WES-C-{i+1:03}',topic,q,c,[w1,w2,w3],e))
assert len(bank)==103

# Each formula is written directly into its question and explanation; no legal limits.
for kind in range(15):
    for j in range(59 if kind < 3 else 60):
        a = D(12+j); b = D(4+j%5); c = D(60+j%25)
        if kind==0:
            v=[int(a*10),int(b),int(b+3)]
            x,n,m=map(D,v); r=x*m/n; unit='g'; topic='레시피 배율'
            q=f'{fmt(n)}인분 수프에 버터 {fmt(x)} g을 쓴다. 1인분당 사용량을 유지해 {fmt(m)}인분을 만들 때 버터는 몇 g인가?'
            e=f'총 사용량 = 기존 사용량 × 새 인분 ÷ 기존 인분. {fmt(x)} × {fmt(m)} ÷ {fmt(n)} = {fmt(r)} g.'
        elif kind==1:
            v=[int((a+10)*b),int(b)]
            x,n=map(D,v); r=x/n; unit='g'; topic='1인분 배분'
            q=f'완성된 감자 퓌레 {fmt(x)} g을 {fmt(n)}인분으로 똑같이 나눈다. 손실이 없을 때 1인분은 몇 g인가?'
            e=f'1인분 질량 = 완성 총질량 ÷ 인분 수. {fmt(x)} ÷ {fmt(n)} = {fmt(r)} g. 동일한 크기로 나누며 분배 손실은 없는 조건이다.'
        elif kind==2:
            v=[int(a*20),int(c)]
            x,y=map(D,v); r=x*y/100; unit='g'; topic='가식부 산출량'
            q=f'채소 구입량 {fmt(x)} g의 가식부 수율이 {fmt(y)}%이다. 사용할 수 있는 가식부는 몇 g인가?'
            e=f'가식량 = 구매량 × 수율 ÷ 100. {fmt(x)} × {fmt(y)} ÷ 100 = {fmt(r)} g. 수율은 구매 질량에 대한 비율이다.'
        elif kind==3:
            v=[int(a*10),int(c)]
            x,y=map(D,v); r=x*100/y; unit='g'; topic='필요 구매량'
            q=f'가식부 {fmt(x)} g이 필요하고 손질 수율은 {fmt(y)}%이다. 필요한 구매량은 몇 g인가? 모든 답은 소수 둘째 자리까지 일반 반올림한다.'
            e=f'구매량 × 수율/100 = 가식량이므로 구매량 = {fmt(x)} × 100 ÷ {fmt(y)} = {fmt(r)} g (소수 둘째 자리 반올림).'
        elif kind==4:
            v=[int(a*100),int(a*100*(100-c)/100)]
            x,l=map(D,v); r=l*100/x; unit='%'; topic='손질 손실률'
            q=f'구매한 채소 {fmt(x)} g 중 손질 손실은 {fmt(l)} g이다. 구매량 기준 손실률은 몇 %인가?'
            e=f'손실률 = 손실 질량 ÷ 구매 질량 × 100. {fmt(l)} ÷ {fmt(x)} × 100 = {fmt(r)}%. 가식부 수율과 합하면 100%이다.'
        elif kind==5:
            v=[int(a*100),int(a*c)]
            x,y=map(D,v); r=y*100/x; unit='%'; topic='가열 수율'
            q=f'가열 전 육류 {fmt(x)} g이 가열 후 {fmt(y)} g이 되었다. 가열 전 질량 기준 가열 수율은 몇 %인가?'
            e=f'가열 수율 = 가열 후 질량 ÷ 가열 전 질량 × 100. {fmt(y)} ÷ {fmt(x)} × 100 = {fmt(r)}%. 추가 재료의 질량은 없다는 조건이다.'
        elif kind==6:
            v=[int(a*10),int((j+10)*100)]
            x,p=map(D,v); r=x*p/1000; unit='원'; topic='식재료 사용 원가'
            q=f'1 kg 가격이 {fmt(p)}원인 재료를 {fmt(x)} g 사용했다. g 단위로 비례 계산하며 포장·폐기 비용이 없을 때 사용 원가는 몇 원인가?'
            e=f'1 kg = 1,000 g. 사용 원가 = {fmt(p)} × ({fmt(x)} ÷ 1,000) = {fmt(r)}원. 이 문제에서는 재료 질량에 비례해 비용을 계산한다.'
        elif kind==7:
            v=[int(a*100),int(a*400)]
            x,s=map(D,v); r=x*100/s; unit='%'; topic='식재료 원가율'
            q=f'식재료 원가가 {fmt(x)}원, 같은 음식 판매액이 {fmt(s)}원이다. 식재료 원가율은 몇 %인가? 다른 비용은 계산에 넣지 않는다.'
            e=f'식재료 원가율 = 식재료 원가 ÷ 판매액 × 100. {fmt(x)} ÷ {fmt(s)} × 100 = {fmt(r)}%. 총이익률이나 영업이익률과 구별한다.'
        elif kind==8:
            v=[int(a*100),int(25+j%20)]
            x,y=map(D,v); r=x*100/y; unit='원'; topic='목표 원가율 판매가'
            q=f'음식의 식재료 원가가 {fmt(x)}원이다. 목표 식재료 원가율을 {fmt(y)}%로 맞출 때 이론상 판매가는 몇 원인가? 세금 등은 제외하고 소수 둘째 자리까지 반올림한다.'
            e=f'원가 ÷ 판매가 × 100 = 목표 원가율. 판매가 = {fmt(x)} × 100 ÷ {fmt(y)} = {fmt(r)}원 (소수 둘째 자리 반올림). 실제 가격 결정에는 다른 비용도 고려한다.'
        elif kind==9:
            v=[int(a*100),int((a+3)*50),int((a+5)*20),int(b)]
            x,y,z,n=map(D,v); r=(x+y+z)/n; unit='원'; topic='배치당 원가 배분'
            q=f'{fmt(n)}인분 수프 한 배치의 재료별 사용 원가가 각각 {fmt(x)}원, {fmt(y)}원, {fmt(z)}원이다. 다른 비용 없이 균등 배분한 1인분 식재료 원가는 몇 원인가? 소수 둘째 자리까지 반올림한다.'
            e=f'총 재료비 = {fmt(x)} + {fmt(y)} + {fmt(z)} = {fmt(x+y+z)}원. 1인분 = {fmt(x+y+z)} ÷ {fmt(n)} = {fmt(r)}원 (소수 둘째 자리 반올림).'
        elif kind==10:
            v=[int(a*10),int(1+j%5)]
            x,p=map(D,v); r=x*p/100; unit='g'; topic='소금 질량비'
            q=f'소금 질량비 {fmt(p)}%인 소금물 {fmt(x)} g을 만들려고 한다. 최종 질량 기준이며 다른 용질이 없을 때 필요한 소금은 몇 g인가?'
            e=f'질량 백분율 = 소금 질량 ÷ 소금물 질량 × 100. 소금 질량 = {fmt(x)} × {fmt(p)} ÷ 100 = {fmt(r)} g. 물의 양이 아닌 최종 소금물 질량이 기준이다.'
        elif kind==11:
            v=[int(a*10),int(10+j%5),int(2+j%3)]
            x,hi,lo=map(D,v); r=x*hi/lo-x; unit='g'; topic='희석용 물 첨가'
            q=f'소금 질량비 {fmt(hi)}%인 소금물 {fmt(x)} g에 물만 더해 {fmt(lo)}%로 희석한다. 소금 손실이 없을 때 추가할 물은 몇 g인가? 소수 둘째 자리까지 반올림한다.'
            e=f'소금 보존: 기존 소금량 = {fmt(x)} × {fmt(hi)}/100 g. 최종 질량 = {fmt(x)} × {fmt(hi)} ÷ {fmt(lo)} g. 추가 물 = 최종 질량 − {fmt(x)} = {fmt(r)} g (소수 둘째 자리 반올림).'
        elif kind==12:
            v=[int(a*20),int(2+j%4),int(a*10)]
            x,p,f=map(D,v); r=x*p/f; unit='%'; topic='증발 후 농도'
            q=f'소금 질량비 {fmt(p)}%인 소금물 {fmt(x)} g에서 물만 증발하여 최종 질량이 {fmt(f)} g이 되었다. 소금 손실이 없을 때 최종 소금 질량비는 몇 %인가?'
            e=f'소금량 = {fmt(x)} × {fmt(p)}/100 g으로 일정하다. 최종 질량비 = ({fmt(x)} × {fmt(p)}/100) ÷ {fmt(f)} × 100 = {fmt(r)}%.'
        elif kind==13:
            v=[int(a),int(b),int(2+j%7)]
            carb,pro,fat=map(D,v); r=(carb+pro)*4+fat*9; unit='kcal'; topic='에너지 환산 연습'
            q=f'탄수화물 {fmt(carb)} g, 단백질 {fmt(pro)} g, 지방 {fmt(fat)} g인 음식이다. 이 문제에서 각각 1 g당 4, 4, 9 kcal로 가정할 때 합계 에너지는 몇 kcal인가? 다른 성분은 제외한다.'
            e=f'주어진 환산 계수로 계산한다. {fmt(carb)} × 4 + {fmt(pro)} × 4 + {fmt(fat)} × 9 = {fmt(r)} kcal. 제품 표시나 분석값을 대신하는 계산은 아니다.'
        else:
            v=[float(a/10)]
            x=D(str(v[0])); r=x*1000; unit='g'; topic='질량 단위 환산'
            q=f'레시피에 적힌 밀가루 {fmt(x)} kg을 g으로 환산하면 몇 g인가?'
            e=f'1 kg = 1,000 g이므로 {fmt(x)} kg × 1,000 g/kg = {fmt(r)} g. 단위 kg이 약분되며 부피 환산이나 밀도 가정은 필요하지 않다.'
        if '반올림' not in q:
            q += ' 계산값이 소수이면 소수 둘째 자리까지 일반 반올림한다.'
        result=D(fmt(r)); delta=max(D(1),result/D(10))
        options=[fmt(result+delta*k)+' '+unit for k in (1,2,3)]
        qid=f'WES-N-{kind+1:02}-{j+1:03}'
        bank.append(make(qid,topic,q,fmt(result)+' '+unit,options,e,
                    f'WES-F-{kind+1:02}',dict(kind=str(kind+1), values=v, result=float(result), unit=unit, precision=2)))
assert len(bank)==1000
assert len({q['id'] for q in bank})==1000
fingerprints={''.join((q['question']+'|'+ '|'.join(sorted(q['choices']))).split()).casefold() for q in bank}
assert len(fingerprints)==1000
(ROOT/'src/data/questions.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
# Standalone import examples are not part of default bank, nor past exam claims.
template={**bank[0], 'id':'LOCAL-EXAMPLE-001', 'question':'사용자가 작성한 손 씻기 연습문항: 비누로 씻는 주된 목적은?', 'verificationStatus':'pending', 'reviewNote':'직접 확인한 근거를 기록하세요.'}
p=ROOT/'public/templates';p.mkdir(parents=True,exist_ok=True)
(p/'questions.json').write_text(json.dumps([template],ensure_ascii=False,indent=2)+'\n')
entries={k:v for k,v in template.items() if k!='choices'}
entries.update({f'choice{i+1}':s for i,s in enumerate(template['choices'])})
with (p/'questions.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(entries),lineterminator="\n");writer.writeheader();writer.writerow(entries)
print(f'Generated {len(bank)}: 103 concepts + 897 numeric variants (15 families).')

# Keep counts and content hash synchronized whenever the bank is regenerated.
audit = {
    'total': len(bank), 'reviewed': sum(q['verificationStatus']=='reviewed' for q in bank),
    'pending': sum(q['verificationStatus']=='pending' for q in bank), 'target': 1000,
    'shortfall': max(0, 1000-sum(q['verificationStatus']=='reviewed' for q in bank)),
    'types': dict(collections.Counter(q['type'] for q in bank)),
    'concepts': sum('family' not in q for q in bank),
    'numericVariants': sum('family' in q for q in bank),
    'families': dict(sorted(collections.Counter(q['family'] for q in bank if 'family' in q).items())),
    'subjects': dict(collections.Counter(q['subject'] for q in bank)),
    'topics': dict(collections.Counter(q['topic'] for q in bank)),
    'sha256': hashlib.sha256((ROOT/'src/data/questions.json').read_bytes()).hexdigest(),
    'externalExpertReview': False, 'officialRulesVerified': False,
}
(ROOT/'docs').mkdir(exist_ok=True)
(ROOT/'docs/bank-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
