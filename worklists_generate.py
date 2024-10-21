import datetime
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
import pydicom

def create_modality_worklist(patient_name, patient_id, accession_number, patient_sex, patient_birth_date):
    # 參數驗證
    if not all([patient_name, patient_id, accession_number, patient_sex, patient_birth_date]):
        raise ValueError("所有參數都不能為空")
    
    try:
        datetime.datetime.strptime(patient_birth_date, '%Y%m%d')
    except ValueError:
        raise ValueError("生日格式必須為 YYYYMMDD")
    
    if patient_sex not in ['M', 'F', 'O']:
        raise ValueError("性別必須為 'M'、'F' 或 'O'")

    # 設定DICOM標籤和值
    ds = Dataset()
    ds.SpecificCharacterSet = 'ISO_IR 192'  # UTF-8 編碼

    # 病人資訊
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.PatientSex = patient_sex
    ds.PatientBirthDate = patient_birth_date

    # 檢查資訊
    ds.StudyInstanceUID = generate_uid()
    ds.AccessionNumber = accession_number
    ds.StudyDate = datetime.date.today().strftime('%Y%m%d')
    ds.StudyTime = datetime.datetime.now().strftime('%H%M%S')
    ds.StudyDescription = "ULTRASOUND STUDY"
    ds.Modality = 'US'
    ds.RequestedProcedureID = accession_number
    ds.RequestedProcedureDescription = "ULTRASOUND SCAN"

    # Scheduled Procedure Step Sequence
    ds.ScheduledProcedureStepSequence = [Dataset()]
    sps = ds.ScheduledProcedureStepSequence[0]
    sps.ScheduledStationAETitle = 'LELTEK'
    sps.ScheduledProcedureStepStartDate = datetime.date.today().strftime('%Y%m%d')
    sps.ScheduledProcedureStepStartTime = datetime.datetime.now().strftime('%H%M%S')
    sps.ScheduledPerformingPhysicianName = ''
    sps.ScheduledProcedureStepDescription = 'ULTRASOUND SCAN'
    sps.ScheduledProcedureStepID = accession_number
    sps.Modality = 'US'

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
        ds.save_as(filename, write_like_original=False)
        print(f"Modality Worklist saved as {filename}")

        # 驗證文件
        verified_ds = pydicom.dcmread(filename)
        print("\nVerifying file contents:")
        required_fields = {
            'PatientName': verified_ds.PatientName,
            'PatientID': verified_ds.PatientID,
            'PatientBirthDate': verified_ds.PatientBirthDate,
            'PatientSex': verified_ds.PatientSex,
            'AccessionNumber': verified_ds.AccessionNumber,
            'StudyInstanceUID': verified_ds.StudyInstanceUID,
            'StudyDate': verified_ds.StudyDate
        }
        
        for field, value in required_fields.items():
            print(f"{field}: {value}")

    except Exception as e:
        print(f"Error saving file: {str(e)}")
        raise

    return ds

if __name__ == "__main__":
    try:
        mwl = create_modality_worklist(
            '陳x明',
            '123456',
            '654321',
            'M',
            '19800101'
        )
    except Exception as e:
        print(f"Error creating modality worklist: {str(e)}")