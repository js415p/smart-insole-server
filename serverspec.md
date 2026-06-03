# 🧮 Smart Insole 대시보드 차트 데이터 계산 알고리즘 및 로직 명세서 (v1.0)

본 문서는 FastAPI 백엔드 서버에서 하드웨어 센서 데이터를 가공하여 대시보드의 각 차트 및 시각화 컴포넌트(히트맵, 밸런스 바, 시계열 이력 차트)에 필요한 수치를 계산하는 알고리즘 로직을 정의합니다.

---

## 1. 전제 조건 및 기초 가공 (Data Normalization)
라즈베리파이(MCP3008)로부터 들어오는 `0.0 ~ 1.0` 사이의 정규화된 아날로그 전압 값(`raw_value`)을 실제 압력 단위인 **`kPa(킬로파스칼)`** 단위로 1차 치환합니다.

* **최대 설계 임계값 ($P_{max}$):** $150.0\ kPa$
* **변환 공식:** $$kPa = raw\_value \times 150.0$$

---

## 2. 컴포넌트별 데이터 계산 로직 및 알고리즘

### ① 실시간 압력 히트맵 (발바닥 8개 센서 노드)
프론트엔드 단에서 시각적 효과(원의 크기 및 불투명도)를 백엔드 연산 없이 직관적으로 제어할 수 있도록 **불투명도(Opacity)** 매핑용 비율 가공 값을 함께 계산합니다.

* **입력 데이터:** 8개 채널별 `kPa` 값
* **출력 데이터:** `opacity` (0.0 ~ 1.0)
* **계산 공식:**
  $$opacity = \min\left(\frac{kPa}{150.0}, 1.0\right)$$
  *(예: 특정 센서가 75 kPa이면 opacity는 0.5로 계산하여 전달)*

### ② 좌우 체중 분산 비율 (밸런스 바 게이지 차트)
현재 사용자의 체중이 왼발과 오른발에 각각 몇 %씩 분산되어 있는지 실시간으로 계산합니다. 단, 분모가 0이 되어 발생하는 ZeroDivisionError를 방지하는 예외 처리가 필수적입니다.

* **알고리즘 단계:**
  1. 왼발 4개 센서의 kPa 합산: $Total_{Left} = s1 + s2 + s3 + s4$
  2. 오른발 4개 센서의 kPa 합산: $Total_{Right} = s1 + s2 + s3 + s4$
  3. 전체 압력 합산: $Total_{All} = Total_{Left} + Total_{Right}$
* **계산 공식 (백분율 비율):**
  * 만약 $Total_{All} == 0$ 이면: `left_ratio = 50.0`, `right_ratio = 50.0` (기본값)
  * 그 외의 경우:
    $$left\_ratio = \left(\frac{Total_{Left}}{Total_{All}}\right) \times 100$$
    $$right\_ratio = 100.0 - left\_ratio$$
* **출력 형식:** 소수점 첫째 자리 반올림 (`round(value, 1)`)

### ③ 입력 불균형률 (Imbalance Percent 통계 차트)
좌우 체중 균형 상태가 완벽한 중심(50:50)으로부터 얼마나 벗어났는지를 절대적인 수치(%)로 도출합니다.

* **계산 공식:**
  $$imbalance\_percent = |left\_ratio - 50.0| \times 2$$
* **로직 예시:**
  * 좌우 비율이 `50% : 50%` 이면: $|50 - 50| \times 2 = 0\%$ (완벽한 균형)
  * 좌우 비율이 `47% : 53%` 이면: $|47 - 50| \times 2 = 6\%$ (경미한 불균형)
  * 좌우 비율이 `30% : 70%` 이면: $|30 - 50| \times 2 = 40\%$ (심각한 불균형)

### ④ 실시간 걸음 수 카운트 (Peak Detection 알고리즘)
시안 내 통계 데이터를 위해 뒤꿈치 센서의 압력 변화 궤적을 추적하여 걸음 수(`gait_count`)를 누적 연산합니다. 고주파 노이즈로 인한 중복 카운팅을 막기 위해 **임계값(Threshold)과 디바운스 타임(Debounce Time)** 기법을 적용합니다.

* **상태 변수 (State):** `is_stepping = False` (전역 혹은 세션 변수로 관리)
* **설정 상수:** * 디딤 임계값 ($Th_{high}$): $40.0\ kPa$ (발을 디뎠다고 판단하는 기준)
  * 뗌 임계값 ($Th_{low}$): $10.0\ kPa$ (발을 뗐다고 판단하는 기준)
* **알고리즘 로직:**
  ```python
  # 현재 루프의 뒤꿈치 압력 수치 확인
  current_heel_pressure = data.left.sensors.s1_kpa # 혹은 오른발 s1_kpa
  
  if not is_stepping and current_heel_pressure > Th_high:
      # 발을 딛는 순간 (Peak 진입) -> 걸음 수 1 증가
      gait_count += 1
      is_stepping = True  # 플래그 락 (중복 카운트 방지)
      
  elif is_stepping and current_heel_pressure < Th_low:
      # 발을 완전히 지면에서 뗀 순간 -> 플래그 해제
      is_stepping = False