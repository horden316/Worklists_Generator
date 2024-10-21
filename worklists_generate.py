import datetime
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
import pydicom

def create_modality_worklist(patient_name, patient_id, accession_number, study_instance_uid, patient_sex, patient_birth_date):
    # 設定DICOM標籤和值
    ds = Dataset()
    # 設定特定字符集以支援中文
    ds.SpecificCharacterSet = 'ISO_IR 192'  # UTF-8 編碼
    
    # 直接賦值，pydicom 會自動處理編碼
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.PatientSex = patient_sex
    # 添加病人生日欄位 (格式應為 YYYYMMDD)
    ds.PatientBirthDate = patient_birth_date
    
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
        print(f"Patient Birth Date: {verified_ds.PatientBirthDate}")
        print(f"Accession Number: {verified_ds.AccessionNumber}")
    except Exception as e:
        print(f"Error saving file: {e}")
    
    return ds

if __name__ == "__main__":
    # 測試用例
    mwl = create_modality_worklist(
        '陳x明',
        '123456',
        '654321',
        generate_uid(),
        'M',
        '19800101'  # 生日格式為 YYYYMMDD
    )