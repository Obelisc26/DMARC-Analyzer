import os
import zipfile
import tarfile
import gzip
import shutil
import email
from email import policy
from pathlib import Path
import extract_msg  # Nueva librería

class FileExtractor:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def extract_all(self, input_dir):
        """Recorre el directorio de entrada y extrae archivos soportados."""
        input_path = Path(input_dir)
        extracted_files = []
        
        print(f"🔍 Scanning directory: {input_dir}")

        for file_path in input_path.rglob('*'):
            if file_path.is_file():
                # Evitar procesar archivos ocultos o de sistema
                if file_path.name.startswith('.'):
                    continue
                    
                filename = file_path.name.lower()
                
                try:
                    if filename.endswith('.zip'):
                        self._extract_zip(file_path)
                    elif filename.endswith('.tar') or filename.endswith('.tar.gz') or filename.endswith('.tgz'):
                        self._extract_tar(file_path)
                    elif filename.endswith('.gz') and not filename.endswith('.tar.gz'):
                        self._extract_gz(file_path)
                    elif filename.endswith('.eml'):
                        self._extract_eml(file_path)
                    elif filename.endswith('.msg'): # NUEVO: Soporte para Outlook
                        self._extract_msg(file_path)
                    elif filename.endswith('.xml') or filename.endswith('.html'):
                        # Copiar directamente si ya es el formato final
                        shutil.copy2(file_path, os.path.join(self.output_dir, file_path.name))
                        extracted_files.append(file_path.name)
                        print(f"   ✓ Copied: {file_path.name}")
                except Exception as e:
                    print(f"   ❌ Error extracting {filename}: {str(e)}")

        return os.listdir(self.output_dir)

    def _extract_zip(self, file_path):
        print(f"📦 Extracting ZIP: {file_path.name}")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(self.output_dir)
            
    def _extract_tar(self, file_path):
        print(f"📦 Extracting TAR: {file_path.name}")
        with tarfile.open(file_path, 'r:*') as tar_ref:
            tar_ref.extractall(self.output_dir)

    def _extract_gz(self, file_path):
        print(f"📦 Extracting GZ: {file_path.name}")
        output_filename = file_path.stem
        with gzip.open(file_path, 'rb') as f_in:
            with open(os.path.join(self.output_dir, output_filename), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"   ✓ Extracted: {output_filename}")

    def _extract_eml(self, file_path):
        """Extrae adjuntos de archivos .eml estándar"""
        print(f"📧 Processing EML: {file_path.name}")
        with open(file_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
            
        self._process_email_attachments(msg, file_path.stem)

    def _extract_msg(self, file_path):
        """NUEVO: Extrae adjuntos de archivos .msg de Outlook"""
        print(f"📧 Processing MSG (Outlook): {file_path.name}")
        try:
            msg = extract_msg.Message(file_path)
            if msg.attachments:
                for attachment in msg.attachments:
                    # Guardar el adjunto
                    save_path = os.path.join(self.output_dir, attachment.longFilename)
                    attachment.save(customPath=self.output_dir)
                    print(f"   📎 Attachment extracted: {attachment.longFilename}")
                    
                    # RECURSIVIDAD: Si el adjunto es un ZIP/GZ/XML, debemos procesarlo también
                    # Chequeo rápido para descomprimir si el adjunto es un comprimido
                    lower_name = attachment.longFilename.lower()
                    if lower_name.endswith('.zip'):
                        self._extract_zip(Path(save_path))
                    elif lower_name.endswith('.gz'):
                        self._extract_gz(Path(save_path))
            else:
                print(f"   ⚠️ MSG file has no attachments")
            msg.close()
        except Exception as e:
            print(f"   ❌ Error processing MSG: {e}")

    def _process_email_attachments(self, msg, prefix):
        """Helper para procesar adjuntos de objetos email (usado por EML)"""
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
                
            filename = part.get_filename()
            if filename:
                output_path = os.path.join(self.output_dir, filename)
                with open(output_path, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                print(f"   ✓ Attachment extracted: {filename}")
                
                # Recursividad simple para EML también
                if filename.lower().endswith('.zip'):
                    self._extract_zip(Path(output_path))
                elif filename.lower().endswith('.gz'):
                    self._extract_gz(Path(output_path))
    
    def get_statistics(self):
        # Cuenta simple de archivos en el output
        files = os.listdir(self.output_dir)
        return {
            'total_files': len(files),
            'xml_files': len([f for f in files if f.endswith('.xml')]),
            'html_files': len([f for f in files if f.endswith('.html')])
        }
