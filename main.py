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
# 환경 변수에서 Firebase 서비스 계정 정보를 가져옵니다.
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

# 데이터베이스 URL도 환경 변수에서 가져옵니다.
database_url = os.getenv("DATABASE_URL")

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    "databaseURL": database_url
})

app = FastAPI()

# 2. 전송받을 데이터 포맷 정의 (말씀하신 간단한 구조)
class InsoleData(BaseModel):
    name: str
    side: str  # "left" 또는 "right" 
    timestamp: float = None  # 시간이 없으면 서버 시간을 사용
    s1: float
    s2: float
    s3: float
    s4: float

@app.post("/update")
async def update_data(data: InsoleData):
    # 만약 라즈베리파이에서 시간을 안 보내주면 현재 서버 시간을 입력
    current_time = data.timestamp if data.timestamp else time.time()
    
    # Firebase 저장용 데이터 조립
    save_data = {
        "name": data.name,
        "side": data.side,
        "timestamp": current_time,
        "sensors": {
            "s1": data.s1,
            "s2": data.s2,
            "s3": data.s3,
            "s4": data.s4
        }
    }
    
    # 3. Firebase 실시간 DB에 저장 (최신 데이터 덮어쓰기)
    ref = db.reference(f'insole_live/{data.name}')
    ref.set(save_data)
    
    return {"status": "success", "msg": f"{data.name}'s data updated!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)