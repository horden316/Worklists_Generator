import subprocess
from fastapi import FastAPI
from pydantic import BaseModel
import os

# 創建 FastAPI 應用程式
app = FastAPI()

# 定義一個模型來接收請求中的參數
class WorklistRequest(BaseModel):
    patient_name: str
    patient_id: str
    accession_number: str
    study_instance_uid: str
    patient_sex: str

# API 端點：接收資料並呼叫你的 Script
@app.post("/create_worklist/")
async def create_worklist(worklist: WorklistRequest):
    try:
        # 呼叫你的 Python Script，將參數傳入
        patient_name = worklist.patient_name
        patient_id = worklist.patient_id
        accession_number = worklist.accession_number
        study_instance_uid = worklist.study_instance_uid
        patient_sex = worklist.patient_sex

        # 呼叫 Script 的函數，或者你也可以選擇用 subprocess 來呼叫外部 Script
        from .worklists_generate import create_modality_worklist
        create_modality_worklist(patient_name, patient_id, accession_number, study_instance_uid, patient_sex)

        return {"status": "Success", "message": f"Worklist for {patient_name} created successfully."}
    except Exception as e:
        return {"status": "Failed", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)