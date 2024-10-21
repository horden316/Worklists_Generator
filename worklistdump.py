import pydicom
import os
import argparse
from pathlib import Path

def read_dicom_to_dump(input_path):
    """
    讀取DICOM檔案並將其內容輸出成dump檔
    
    Parameters:
        input_path (str): DICOM檔案的路徑
    """
    try:
        # 使用Path來處理跨平台的路徑問題
        input_path = Path(input_path)
        
        # 檢查輸入檔案是否存在
        if not input_path.exists():
            raise FileNotFoundError(f"找不到檔案: {input_path}")
            
        # 讀取DICOM檔案
        ds = pydicom.dcmread(str(input_path))
        
        # 建立輸出檔案路徑 (與輸入檔案同目錄)
        output_path = input_path.with_suffix('.dump')
        
        # 將DICOM資料寫入dump檔
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(ds))
            
        print(f"成功將DICOM資料寫入: {output_path}")
        return ds
        
    except Exception as e:
        print(f"處理DICOM檔案時發生錯誤: {str(e)}")
        return None

def main():
    # 設定命令列參數
    parser = argparse.ArgumentParser(description='讀取DICOM檔案並輸出成dump檔')
    parser.add_argument('path', help='DICOM檔案的路徑')
    args = parser.parse_args()
    
    # 讀取檔案並輸出
    ds = read_dicom_to_dump(args.path)
    
    # 如果成功讀取,顯示DICOM內容
    if ds is not None:
        print("\nDICOM檔案內容:")
        print(ds)

if __name__ == "__main__":
    main()