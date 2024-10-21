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
    ds.PatientSex = patient_sex
    
    # 檢查資訊
    ds.StudyInstanceUID = study_instance_uid
    ds.AccessionNumber = accession_number
    ds.StudyDate = datetime.date.today().strftime('%Y%m%d')
    ds.StudyTime = datetime.datetime.now().strftime('%H%M%S')
    ds.Modality = 'CT'
    
    # Scheduled Procedure Step Sequence
    ds.ScheduledProcedureStepSequence = [Dataset()]
    sps = ds.ScheduledProcedureStepSequence[0]
    sps.ScheduledStationAETitle = 'LELTEK'
    sps.ScheduledProcedureStepStartDate = datetime.date.today().strftime('%Y%m%d')
    sps.ScheduledProcedureStepStartTime = datetime.datetime.now().strftime('%H%M%S')
    sps.ScheduledPerformingPhysicianName = ''
    sps.ScheduledProcedureStepDescription = 'CT SCAN'
    sps.ScheduledProcedureStepID = accession_number
    sps.Modality = 'CT'
    
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.31'
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = '1.2.3.4.5.6.7.8.9.0'
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
        
        # 讀取並印出文件內容以驗證
        print("\nVerifying file contents:")
        verified_ds = pydicom.dcmread(filename)
        print(f"Patient Name: {verified_ds.PatientName}")
        print(f"Patient ID: {verified_ds.PatientID}")
        print(f"Accession Number: {verified_ds.AccessionNumber}")
        
    except Exception as e:
        print(f"Error saving file: {e}")
    
    return ds

def handle_store(event):
    try:
        ds = event.dataset
        ds.file_meta = event.file_meta
        if hasattr(ds, 'SpecificCharacterSet'):
            print(f"Received dataset with character set: {ds.SpecificCharacterSet}")
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

if __name__ == "__main__":
    # 測試用例
    mwl = create_modality_worklist('陳x明', '123456', '654321', generate_uid(), 'M')