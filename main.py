import os
import time
import firebase_admin
from firebase_admin import credentials, db
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 1. Firebase 설정
firebase_config = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n") if os.getenv("FIREBASE_PRIVATE_KEY") else None,
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
}

database_url = os.getenv("DATABASE_URL")

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    "databaseURL": database_url
})

app = FastAPI()

# 2. 전송받을 데이터 포맷 정의 (라즈베리파이가 쏘는 정규화 데이터)
class InsoleData(BaseModel):
    name: str
    side: str          # "left" 또는 "right" 
    timestamp: float = None
    s1: float          # 뒤꿈치 (CH3 / CH7)
    s2: float          # 안쪽 (CH1 / CH5)
    s3: float          # 바깥쪽 (CH2 / CH6)
    s4: float          # 발가락 (CH0 / CH4)

# 가상 상수: 정규화 수치(0~1)를 시안과 매핑하기 위한 설정 (serverspec.md 기준)
MAX_KPA = 150.0
TH_HIGH = 40.0   # 디딤 임계값
TH_LOW = 10.0    # 뗌 임계값

@app.post("/update")
async def update_data(data: InsoleData):
    uid = data.name
    side = data.side
    current_time = data.timestamp if data.timestamp else time.time()
    
    # ----------------------------------------------------
    # [가공 1] kPa 변환 및 Opacity(불투명도) 매핑
    # ----------------------------------------------------
    kpa_s1 = round(data.s1 * MAX_KPA, 1)
    kpa_s2 = round(data.s2 * MAX_KPA, 1)
    kpa_s3 = round(data.s3 * MAX_KPA, 1)
    kpa_s4 = round(data.s4 * MAX_KPA, 1)
    
    # Opacity 계산 (0.0 ~ 1.0): 히트맵 시각화용
    opacity_s1 = round(min(kpa_s1 / MAX_KPA, 1.0), 2)
    opacity_s2 = round(min(kpa_s2 / MAX_KPA, 1.0), 2)
    opacity_s3 = round(min(kpa_s3 / MAX_KPA, 1.0), 2)
    opacity_s4 = round(min(kpa_s4 / MAX_KPA, 1.0), 2)
    
    # 해당 발의 총합 압력 연산 (체중 분산 비율 계산용)
    total_foot_pressure = kpa_s1 + kpa_s2 + kpa_s3 + kpa_s4
    
    # 해당 발 데이터 객체화
    foot_data = {
        "timestamp": current_time,
        "total_pressure": total_foot_pressure,
        "sensors": {
            "s1_kpa": kpa_s1, "s1_opacity": opacity_s1,
            "s2_kpa": kpa_s2, "s2_opacity": opacity_s2,
            "s3_kpa": kpa_s3, "s3_opacity": opacity_s3,
            "s4_kpa": kpa_s4, "s4_opacity": opacity_s4
        }
    }
    
    # 가공 데이터를 독립 노드에 저장
    db.reference(f'insole_live/{uid}/{side}').set(foot_data)
    
    # ----------------------------------------------------
    # [가공 2] 좌우 밸런스, 불균형률, 최대 압력, 과부하 경고 계산
    # ----------------------------------------------------
    opposite_side = "right" if side == "left" else "left"
    opposite_node = db.reference(f'insole_live/{uid}/{opposite_side}').get()
    
    # 반대편 데이터가 있으면 가져옴
    if opposite_node:
        opp_sensors = opposite_node.get("sensors", {})
        opposite_pressure = opposite_node.get("total_pressure", 0)
        opp_kpas = {
            "CH3" if opposite_side == "left" else "CH7": opp_sensors.get("s1_kpa", 0),
            "CH1" if opposite_side == "left" else "CH5": opp_sensors.get("s2_kpa", 0),
            "CH2" if opposite_side == "left" else "CH6": opp_sensors.get("s3_kpa", 0),
            "CH0" if opposite_side == "left" else "CH4": opp_sensors.get("s4_kpa", 0),
        }
    else:
        opposite_pressure = 0
        opp_kpas = {}

    # 현재 발의 kpa 매핑
    curr_kpas = {
        "CH3" if side == "left" else "CH7": kpa_s1,
        "CH1" if side == "left" else "CH5": kpa_s2,
        "CH2" if side == "left" else "CH6": kpa_s3,
        "CH0" if side == "left" else "CH4": kpa_s4,
    }
    
    # 8개 센서 통합 (최대 압력 및 과부하 계산용)
    all_kpas = {**curr_kpas, **opp_kpas}
    
    # 최대 압력 및 해당 채널 찾기
    max_val = 0
    max_ch = "N/A"
    if all_kpas:
        max_ch = max(all_kpas, key=all_kpas.get)
        max_val = all_kpas[max_ch]

    # 좌우 비율 계산
    left_p = total_foot_pressure if side == "left" else opposite_pressure
    right_p = total_foot_pressure if side == "right" else opposite_pressure
    total_p = left_p + right_p
    
    if total_p > 0:
        left_ratio = round((left_p / total_p) * 100, 1)
        right_ratio = round(100.0 - left_ratio, 1)
    else:
        left_ratio, right_ratio = 50.0, 50.0
        
    imbalance_percent = round(abs(left_ratio - 50.0) * 2, 1)
    
    # 과부하 경고 (150 kPa 초과 시 횟수 누적)
    balance_ref = db.reference(f'insole_live/{uid}/balance')
    prev_balance = balance_ref.get() or {}
    overload_count = prev_balance.get("overload_count", 0)
    
    # 현재 전송된 데이터 중 150을 넘는게 있는지 확인 (한 번의 요청에 한 번만 카운트)
    if any(v >= MAX_KPA for v in [kpa_s1, kpa_s2, kpa_s3, kpa_s4]):
        overload_count += 1

    balance_data = {
        "left_ratio": left_ratio,
        "right_ratio": right_ratio,
        "imbalance_percent": imbalance_percent,
        "max_pressure": max_val,
        "max_channel": max_ch,
        "overload_count": overload_count,
        "updated_at": current_time
    }
    balance_ref.set(balance_data)

    # ----------------------------------------------------
    # [가공 3] 걸음 수 카운트 (Peak Detection 알고리즘)
    # ----------------------------------------------------
    gait_ref = db.reference(f'insole_live/{uid}/gait')
    gait_data = gait_ref.get() or {"count": 0, "is_stepping_left": False, "is_stepping_right": False}
    
    is_stepping_key = f"is_stepping_{side}"
    is_stepping = gait_data.get(is_stepping_key, False)
    
    if not is_stepping and kpa_s1 > TH_HIGH:
        gait_data["count"] += 1
        gait_data[is_stepping_key] = True
    elif is_stepping and kpa_s1 < TH_LOW:
        gait_data[is_stepping_key] = False
        
    gait_ref.set(gait_data)

    # ----------------------------------------------------
    # [가공 4] 시간대별 이력 데이터 저장 (History)
    # ----------------------------------------------------
    # 데이터 용량을 위해 1분 단위 등으로 제한할 수 있으나, 여기서는 매 업데이트 기록
    history_entry = {
        "timestamp": current_time,
        "side": side,
        "sensors": foot_data["sensors"],
        "balance": {
            "left_ratio": left_ratio,
            "right_ratio": right_ratio
        }
    }
    db.reference(f'insole_history/{uid}').push(history_entry)

    # ----------------------------------------------------
    # [가공 5] 실시간 보행 진단 알고리즘 (Rule-based)
    # ----------------------------------------------------
    diagnosis_ref = db.reference(f'insole_live/{uid}/diagnosis/{side}')
    
    # 기본값 (정상)
    diag_status = "정상 보행"
    diag_issue_zone = "N/A"
    diag_solution = "균형 잡힌 보행을 유지하고 있습니다. 현재의 보행 습관을 유지하십시오."
    is_alert = False
    alert_level = "info" # info, warning, critical
    
    # 과내전 (Overpronation) 체크
    # s2: 안쪽, s3: 바깥쪽
    if kpa_s2 > (kpa_s3 * 1.5) and kpa_s2 > 30.0:
        diag_status = "과내전 위험 감지"
        diag_issue_zone = "안쪽 아치 중심 (CH1)" if side == "left" else "안쪽 아치 중심 (CH5)"
        diag_solution = "발목이 안쪽으로 무너지고 있습니다. 기능성 아치 패드 사용 및 의도적으로 발가락 바깥쪽에 힘을 주는 보행을 권장합니다."
        is_alert = True
        alert_level = "warning"
    
    # 외내전 (Supination/Underpronation) 체크
    elif kpa_s3 > (kpa_s2 * 1.5) and kpa_s3 > 30.0:
        diag_status = "외내전(요족) 위험 감지"
        diag_issue_zone = "바깥쪽 아치 중심 (CH2)" if side == "left" else "바깥쪽 아치 중심 (CH6)"
        diag_solution = "발이 바깥쪽으로 기울고 있습니다. 발가락 안쪽(엄지발가락)에 의도적으로 힘을 주는 보행을 권장합니다."
        is_alert = True
        alert_level = "warning"

    diagnosis_data = {
        "status": diag_status,
        "issue_zone": diag_issue_zone,
        "solution": diag_solution,
        "is_alert": is_alert,
        "alert_level": alert_level,
        "updated_at": current_time
    }
    diagnosis_ref.set(diagnosis_data)
    
    return {
        "status": "success", 
        "msg": f"{uid}'s {side} foot processed and all dashboard data updated!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)