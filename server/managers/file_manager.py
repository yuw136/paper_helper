class FileManager:
    def upload_paper(self, local_path, filename):
        # 现在的版本：存本地
        # shutil.copy(local_path, f"/my/local/backup/{filename}")
        
        # 未来的版本：传 GCS
        # bucket.blob(f"papers/{filename}").upload_from_filename(local_path)
        pass

    def upload_report(self, local_path, filename):
        # 现在的版本：存本地
        # ...
        
        # 未来的版本：传 Google Drive API
        # drive_service.files().create(...)
        pass