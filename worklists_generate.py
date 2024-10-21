import datetime
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from pynetdicom import AE, evt, StoragePresentationContexts, VerificationPresentationContexts, QueryRetrievePresentationContexts
import pydicom

def create_modality_worklist(patient_name, patient_id, accession_number, study_instance_uid, patient_sex):
    # 設定DICOM標籤和值
    ds = Dataset()
    
    # 設定特定字符集以支持中文
    ds.SpecificCharacterSet = 'ISO_IR 192'  # UTF-8 編碼
    
    # 直接賦值，pydicom 會自動處理編碼
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.AccessionNumber = accession_number
    ds.StudyInstanceUID = study_instance_uid
    ds.PatientSex = patient_sex  # 新增PatientSex標籤
    ds.Modality = 'CT'
    ds.ScheduledProcedureStepSequence = [Dataset()]
    sps = ds.ScheduledProcedureStepSequence[0]
    sps.ScheduledStationAETitle = 'LELTEK'
    sps.ScheduledProcedureStepStartDate = datetime.date.today().strftime('%Y%m%d')
    sps.ScheduledProcedureStepStartTime = datetime.datetime.now().strftime('%H%M%S')
    
    # 中文字段直接賦值
    sps.ScheduledPerformingPhysicianName = ''
    sps.ScheduledProcedureStepDescription = ''
    
    # 設定文件元信息
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.31'
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = '1.2.3.4.5.6.7.8.9.0'  # 固定的UID
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    # 創建DICOM文件
    filename = f'MWL_{patient_id}.wl'
    ds = FileDataset(filename, ds, file_meta=file_meta, preamble=b'\0' * 128)
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    
    try:
        # 使用UTF-8保存文件
        ds.save_as(filename, write_like_original=False)
        print(f"Modality Worklist saved as {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")
    
    return ds

def handle_store(event):
    try:
        ds = event.dataset
        ds.file_meta = event.file_meta
        
        # 檢查字符集
        if hasattr(ds, 'SpecificCharacterSet'):
            print(f"Received dataset with character set: {ds.SpecificCharacterSet}")
        
        # 印出接收到的DICOM數據集
        print(ds)
        return 0x0000
    except Exception as e:
        print(f"Error handling store: {e}")
        return 0xC000

def start_scp():
    ae = AE()
    ae.supported_contexts = StoragePresentationContexts + VerificationPresentationContexts + QueryRetrievePresentationContexts
    handlers = [(evt.EVT_C_STORE, handle_store)]
    
    try:
        ae.start_server(('', 11112), block=True, evt_handlers=handlers)
    except Exception as e:
        print(f"Error starting server: {e}")

#if __name__ == "__main__":
    # 示例用法
    #mwl = create_modality_worklist('張三', '123456', '654321', generate_uid(), 'M')
    # 啟動SCP
    #start_scp()