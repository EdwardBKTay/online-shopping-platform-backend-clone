# https://riskledger.com/resources/approach-virus-scanning-files
import io


# Upload the File onto Blob Storage and Scan it for viruses if virus is found, change the file status to "Virus Found" and delete the file from Blob Storage
class FileUploadService:
    def __init__(self, file: io.BytesIO):
        self.file = file
        
    async def scan_virus(self):
        return
