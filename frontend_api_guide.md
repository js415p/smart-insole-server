# 📊 Smart Insole 대시보드 프론트엔드 연동 가이드 (v1.1)

본 문서는 FastAPI 백엔드에서 가공하여 Firebase Realtime Database에 저장하는 데이터 구조와 프론트엔드 대시보드 컴포넌트 간의 매핑 가이드를 제공합니다.

---

## 1. Firebase 데이터베이스 구조 (Realtime Database)

모든 실시간 데이터는 `insole_live/{user_name}/` 경로 하위에 저장되며, 이력 데이터는 `insole_history/{user_name}/`에 누적됩니다.

### ① 실시간 발 데이터 (Heatmap용)
*   **경로**: `insole_live/{user_name}/left` 또는 `insole_live/{user_name}/right`
*   **데이터 구조**:
    ```json
    {
      "timestamp": 1717056000.123,
      "total_pressure": 210.5,
      "sensors": {
        "s1_kpa": 75.0, "s1_opacity": 0.50, // 뒤꿈치 (CH3/CH7)
        "s2_kpa": 60.0, "s2_opacity": 0.40, // 안쪽 (CH1/CH5)
        "s3_kpa": 45.0, "s3_opacity": 0.30, // 바깥쪽 (CH2/CH6)
        "s4_kpa": 30.0, "s4_opacity": 0.20  // 발가락 (CH0/CH4)
      }
    }
    ```
*   **UI 매핑**: `opacity` 값을 원의 투명도(0~1)로 사용하고, `kpa` 값을 툴팁이나 라벨에 표시하십시오.

### ② 밸런스 및 상태 통계 (Balance Bar & Stats용)
*   **경로**: `insole_live/{user_name}/balance`
*   **데이터 구조**:
    ```json
    {
      "left_ratio": 47.5,
      "right_ratio": 52.5,
      "imbalance_percent": 5.0,
      "max_pressure": 141.2,
      "max_channel": "CH7",
      "overload_count": 3,
      "updated_at": 1717056000.123
    }
    ```
*   **UI 매핑**:
    *   `left_ratio`, `right_ratio`: 하단 밸런스 바 게이지
    *   `imbalance_percent`: "압력 불균형률" 수치
    *   `max_pressure` & `max_channel`: "최대 압력" 영역
    *   `overload_count`: "과부하 경고" 횟수

### ③ 실시간 보행 진단 및 알림 (Diagnosis & Alert용)
*   **경로**: `insole_live/{user_name}/diagnosis/left` 및 `right`
*   **데이터 구조**:
    ```json
    {
      "status": "과내전 위험 감지",
      "issue_zone": "안쪽 아치 중심 (CH1)",
      "solution": "발목이 안쪽으로 무너지고 있습니다. ...",
      "is_alert": true,
      "alert_level": "warning",
      "updated_at": 1717056000.123
    }
    ```
*   **UI 매핑**:
    *   `status`: 진단명 표시 (예: "정상", "과내전 위험" 등)
    *   `is_alert`: `true`일 경우 대시보드에 **팝업 또는 토스트 알림**을 발생시키십시오.
    *   `alert_level`: 알림의 색상/심각도 제어 (`info`: 파랑, `warning`: 노랑/주황, `critical`: 빨강)
    *   `solution`: 상세 보기 클릭 시 나타나는 가이드 텍스트

### ④ 걸음 수 데이터 (Gait Counter용)
*   **경로**: `insole_live/{user_name}/gait`
*   **데이터 구조**:
    ```json
    {
      "count": 6284,
      "is_stepping_left": false,
      "is_stepping_right": false
    }
    ```
*   **UI 매핑**: `count` 값을 상단 메인 걸음 수 수치에 표시하십시오.

### ④ 시간대별 압력 이력 (History Chart용)
*   **경로**: `insole_history/{user_name}/`
*   **특징**: 해당 노드 하위에 `push()`로 생성된 랜덤 키값들과 함께 스냅샷 데이터가 누적됩니다.
*   **UI 매핑**: 하단 `시간대별 압력 이력 (KPA)` 차트 구현 시, 해당 경로의 리스트를 읽어와 `timestamp`와 각 `sensors` 값을 시계열로 렌더링하십시오.

---

## 2. 프론트엔드 연동 팁

1.  **실시간 업데이트**: Firebase SDK의 `onValue` (또는 리액트의 경우 `useObject` 등)를 사용하여 `insole_live/{user_name}` 전체를 구독하면 모든 대시보드 위젯을 한 번에 업데이트할 수 있습니다.
2.  **채널 매핑**:
    *   **왼발**: CH0(발가락), CH1(안쪽), CH2(바깥쪽), CH3(뒤꿈치)
    *   **오른발**: CH4(발가락), CH5(안쪽), CH6(바깥쪽), CH7(뒤꿈치)
3.  **단위**: 모든 압력 수치는 `kPa` 단위로 서버에서 가공되어 전송됩니다.

---

## 3. 백엔드 API 정보

*   **Endpoint**: `POST /update`
*   **Payload (라즈베리파이 송신용)**:
    ```json
    {
      "name": "Taeyoung",
      "side": "left",
      "s1": 0.85, "s2": 0.45, "s3": 0.60, "s4": 0.30
    }
    ```
    *(프론트엔드에서는 직접 호출할 필요 없으나, 데이터 흐름 이해를 위해 기재함)*
