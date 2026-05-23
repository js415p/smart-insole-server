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

# 가상 상수: 정규화 수치(0~1)를 시안과 매핑하기 위한 최대 압력 기준값 (예: 150 kPa)
MAX_KPA = 150

@app.post("/update")
async def update_data(data: InsoleData):
    uid = data.name
    side = data.side
    current_time = data.timestamp if data.timestamp else time.time()
    
    # ----------------------------------------------------
    # [가공 1] 정규화 값(0.0~1.0) -> 시안용 kPa 단위로 변환
    # ----------------------------------------------------
    kpa_s1 = round(data.s1 * MAX_KPA, 1)
    kpa_s2 = round(data.s2 * MAX_KPA, 1)
    kpa_s3 = round(data.s3 * MAX_KPA, 1)
    kpa_s4 = round(data.s4 * MAX_KPA, 1)
    
    # 해당 발의 총합 압력 연산 (체중 분산 비율 계산용)
    total_foot_pressure = kpa_s1 + kpa_s2 + kpa_s3 + kpa_s4
    
    # 해당 발 데이터 객체화
    foot_data = {
        "timestamp": current_time,
        "total_pressure": total_foot_pressure,
        "sensors": {
            "s1_kpa": kpa_s1,
            "s2_kpa": kpa_s2,
            "s3_kpa": kpa_s3,
            "s4_kpa": kpa_s4
        }
    }
    
    # ----------------------------------------------------
    # [가공 2] 해당 발의 가공 데이터를 각각의 독립 노드에 저장
    # 경로 예시: insole_live/Taeyoung/left
    # ----------------------------------------------------
    db.reference(f'insole_live/{uid}/{side}').set(foot_data)
    
    # ----------------------------------------------------
    # [가공 3] 반대편 발의 기존 데이터를 읽어와서 좌우 밸런스 실시간 계산
    # ----------------------------------------------------
    opposite_side = "right" if side == "left" else "left"
    opposite_node = db.reference(f'insole_live/{uid}/{opposite_side}').get()
    
    # 반대편 발의 데이터가 이미 있으면 그 총합을 가져오고, 없으면 0으로 처리
    opposite_pressure = opposite_node.get("total_pressure", 0) if opposite_node else 0
    
    # 현재 시점의 왼발, 오른발 총 압력 매핑
    left_p = total_foot_pressure if side == "left" else opposite_pressure
    right_p = total_foot_pressure if side == "right" else opposite_pressure
    total_p = left_p + right_p
    
    # 좌우 체중 분산 백분율 및 불균형률 계산
    if total_p > 0:
        left_ratio = round((left_p / total_p) * 100, 1)
        right_ratio = round((right_p / total_p) * 100, 1)
    else:
        left_ratio, right_ratio = 50.0, 50.0 # 누르지 않을 때의 기본 밸런스
        
    imbalance_percent = round(abs(left_ratio - right_ratio), 1)
    
    # 공통 통계 데이터 노드(`balance`)에 가공 완료된 연산 결과 저장
    # 경로 예시: insole_live/Taeyoung/balance
    balance_data = {
        "left_ratio": left_ratio,
        "right_ratio": right_ratio,
        "imbalance_percent": imbalance_percent,
        "updated_at": current_time
    }
    db.reference(f'insole_live/{uid}/balance').set(balance_data)
    
    return {
        "status": "success", 
        "msg": f"{uid}'s {side} foot processed and balance updated!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)