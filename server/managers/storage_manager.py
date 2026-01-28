import os
import aiofiles
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
PAPERS_BUCKET = os.getenv("SUPABASE_PAPERS_BUCKET", "papers")
REPORTS_BUCKET = os.getenv("SUPABASE_REPORTS_BUCKET", "reports")

_supabase_client = None


def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError(
                "Supabase configuration missing. "
                "Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env"
            )
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_client


class StorageManager:
    
    @staticmethod
    def is_supabase_mode() -> bool:
        return USE_SUPABASE
    
    @staticmethod
    async def upload_paper(
        file_content: bytes,
        filename: str,
        topic: str = "uploads"
    ) -> Tuple[str, str]:

        display_path = f"pdfs/{topic}/{filename}"
        
        if USE_SUPABASE:
            # Supabase Storage
            client = get_supabase_client()
            storage_path = f"pdfs/{topic}/{filename}"
            
            result = client.storage.from_(PAPERS_BUCKET).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": "application/pdf"}
            )
            
            storage_url = f"{PAPERS_BUCKET}/{storage_path}"
            print(f"Uploaded to Supabase Storage: {storage_url}")
            
        else:
            # local storage
            from config import PDF_DIR
            local_dir = PDF_DIR / topic
            local_dir.mkdir(parents=True, exist_ok=True)
            local_path = local_dir / filename
            
            async with aiofiles.open(local_path, 'wb') as f:
                await f.write(file_content)
            
            storage_url = str(local_path)
            print(f"Saved to local: {storage_url}")
        
        return display_path, storage_url
    
    # @staticmethod
    # async def upload_report(
    #     file_content: bytes,
    #     filename: str,
    #     subfolder: str = ""
    # ) -> Tuple[str, str]:
       
    #     if subfolder:
    #         display_path = f"weekly_reports/{subfolder}/{filename}"
    #     else:
    #         display_path = f"weekly_reports/{filename}"
        
    #     if USE_SUPABASE:
    #         client = get_supabase_client()
    #         storage_path = display_path
            
    #         result = client.storage.from_(REPORTS_BUCKET).upload(
    #             path=storage_path,
    #             file=file_content,
    #             file_options={"content-type": "application/pdf"}
    #         )
            
    #         storage_url = f"{REPORTS_BUCKET}/{storage_path}"
    #         print(f"Uploaded report to Supabase: {storage_url}")
            
    #     else:
    #         from config import REPORT_DIR
    #         if subfolder:
    #             local_dir = REPORT_DIR / subfolder
    #         else:
    #             local_dir = REPORT_DIR
    #         local_dir.mkdir(parents=True, exist_ok=True)
    #         local_path = local_dir / filename
            
    #         async with aiofiles.open(local_path, 'wb') as f:
    #             await f.write(file_content)
            
    #         storage_url = str(local_path)
    #         print(f" Saved report to local: {storage_url}")
        
    #     return display_path, storage_url
    
    @staticmethod
    def get_signed_url(storage_url: str, expires_in: int = 3600) -> str:
        if not USE_SUPABASE:
            raise ValueError("get_signed_url only works in Supabase mode")
        
        # parse bucket_name and object_path
        parts = storage_url.split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid storage_url format: {storage_url}")
        
        bucket_name, object_path = parts
        
        client = get_supabase_client()
        result = client.storage.from_(bucket_name).create_signed_url(
            path=object_path,
            expires_in=expires_in
        )
        
        return result["signedURL"]
    
    @staticmethod
    def get_public_url(storage_url: str) -> str:
        if not USE_SUPABASE:
            raise ValueError("get_public_url only works in Supabase mode")
        
        parts = storage_url.split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid storage_url format: {storage_url}")
        
        bucket_name, object_path = parts
        
        client = get_supabase_client()
        result = client.storage.from_(bucket_name).get_public_url(object_path)
        
        return result
    
    @staticmethod
    async def delete_file(storage_url: str) -> bool:
        if USE_SUPABASE:
            parts = storage_url.split("/", 1)
            if len(parts) != 2:
                return False
            
            bucket_name, object_path = parts
            client = get_supabase_client()
            
            try:
                client.storage.from_(bucket_name).remove([object_path])
                print(f" Deleted from Supabase: {storage_url}")
                return True
            except Exception as e:
                print(f" Failed to delete from Supabase: {e}")
                return False
        else:
            # local delete
            try:
                if os.path.exists(storage_url):
                    os.remove(storage_url)
                    print(f"Deleted local file: {storage_url}")
                    return True
                return False
            except Exception as e:
                print(f"Failed to delete local file: {e}")
                return False
    
    @staticmethod
    def file_exists(storage_url: str) -> bool:
        if USE_SUPABASE:
            # Supabase doesn't have a direct exists method, try to get URL
            try:
                parts = storage_url.split("/", 1)
                if len(parts) != 2:
                    return False
                bucket_name, object_path = parts
                client = get_supabase_client()
                # try to create signed URL, if file doesn't exist, it will throw an exception
                client.storage.from_(bucket_name).create_signed_url(object_path, 60)
                return True
            except Exception:
                return False
        else:
            return os.path.exists(storage_url)
