import datetime
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from pynetdicom import AE, evt, StoragePresentationContexts, VerificationPresentationContexts, QueryRetrievePresentationContexts

def create_modality_worklist(patient_name, patient_id, accession_number, study_instance_uid, patient_sex):
    # 設定DICOM標籤和值
    ds = Dataset()
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.AccessionNumber = accession_number
    ds.StudyInstanceUID = study_instance_uid
    ds.PatientSex = patient_sex  # 新增PatientSex標籤
    ds.Modality = 'CT'
    ds.ScheduledProcedureStepSequence = [Dataset()]
    ds.ScheduledProcedureStepSequence[0].ScheduledStationAETitle = 'LELTEK'
    ds.ScheduledProcedureStepSequence[0].ScheduledProcedureStepStartDate = datetime.date.today().strftime('%Y%m%d')
    ds.ScheduledProcedureStepSequence[0].ScheduledProcedureStepStartTime = datetime.datetime.now().strftime('%H%M%S')
    ds.ScheduledProcedureStepSequence[0].ScheduledPerformingPhysicianName = '' # 醫生名字
    ds.ScheduledProcedureStepSequence[0].ScheduledProcedureStepDescription = '' # 檢查描述(例如：胸部CT)

    # 設定文件訊息
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

    ds.save_as(filename, write_like_original=False, encoding='utf-8')
    print(f"Modality Worklist saved as {filename}")

    return ds

def handle_store(event):
    ds = event.dataset
    ds.file_meta = event.file_meta
    #印出接收到的DICOM數據集
    print(ds)
    return 0x0000

def start_scp():
    ae = AE()
    ae.supported_contexts = StoragePresentationContexts + VerificationPresentationContexts + QueryRetrievePresentationContexts
    handlers = [(evt.EVT_C_STORE, handle_store)]
    ae.start_server(('', 11112), block=True, evt_handlers=handlers)

if __name__ == "__main__":
    # 示例用法
    #mwl = create_modality_worklist('John Doe', '123456', '654321', generate_uid(), 'M') # 新增性別參數
    # 啟動SCP
    start_scp()