import datetime
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
from pynetdicom import AE, evt, StoragePresentationContexts

def create_modality_worklist(patient_name, patient_id, accession_number, study_instance_uid):
    # 設定DICOM標籤和值
    ds = Dataset()
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.AccessionNumber = accession_number
    ds.StudyInstanceUID = study_instance_uid
    ds.Modality = 'CT'
    ds.ScheduledProcedureStepSequence = [Dataset()]
    ds.ScheduledProcedureStepSequence[0].ScheduledStationAETitle = 'STATION_AE'
    ds.ScheduledProcedureStepSequence[0].ScheduledProcedureStepStartDate = datetime.date.today().strftime('%Y%m%d')
    ds.ScheduledProcedureStepSequence[0].ScheduledProcedureStepStartTime = datetime.datetime.now().strftime('%H%M%S')
    ds.ScheduledProcedureStepSequence[0].ScheduledPerformingPhysicianName = 'Dr. Who'
    ds.ScheduledProcedureStepSequence[0].ScheduledProcedureStepDescription = 'CT Brain'

    # 設定文件訊息
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.31'
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()

    # 創建DICOM文件
    filename = f'MWL_{patient_id}.dcm'
    ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b'\0' * 128)
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    ds.save_as(filename)
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
    ae.supported_contexts = StoragePresentationContexts
    handlers = [(evt.EVT_C_STORE, handle_store)]
    ae.start_server(('', 11112), block=True, evt_handlers=handlers)

if __name__ == "__main__":
    # 示例用法
    mwl = create_modality_worklist('John Doe', '123456', '654321', generate_uid())
    # 啟動SCP
    start_scp()