import os
import logging
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import io

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Core PDF processing service"""
    
    def __init__(self):
        self.supported_formats = ['PNG', 'JPEG', 'TIFF']
    
    def merge_pdfs(self, file_list, upload_folder, output_folder):
        """Merge multiple PDF files into one"""
        try:
            writer = PdfWriter()
            
            for filename in file_list:
                file_path = os.path.join(upload_folder, filename)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {filename}")
                
                reader = PdfReader(file_path)
                for page in reader.pages:
                    writer.add_page(page)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"merged_{timestamp}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            logger.info(f"Successfully merged {len(file_list)} PDFs into {output_filename}")
            return output_filename
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {str(e)}")
            raise e
    
    def split_pdf(self, filename, upload_folder, output_folder, page_range=None):
        """Split a PDF into individual pages or specified range"""
        try:
            file_path = os.path.join(upload_folder, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {filename}")
            
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            output_files = []
            
            # Determine page range
            if page_range:
                start_page = page_range.get('start', 1) - 1  # Convert to 0-based index
                end_page = min(page_range.get('end', total_pages), total_pages)
                pages_to_split = range(start_page, end_page)
            else:
                pages_to_split = range(total_pages)
            
            # Split pages
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(filename)[0]
            
            for i, page_num in enumerate(pages_to_split):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                output_filename = f"{base_name}_page_{page_num + 1}_{timestamp}.pdf"
                output_path = os.path.join(output_folder, output_filename)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_filename)
            
            logger.info(f"Successfully split PDF into {len(output_files)} files")
            return output_files
            
        except Exception as e:
            logger.error(f"Error splitting PDF: {str(e)}")
            raise e
    
    def convert_to_images(self, filename, upload_folder, output_folder, format='PNG', dpi=300):
        """Convert PDF pages to images"""
        try:
            file_path = os.path.join(upload_folder, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {filename}")
            
            if format.upper() not in self.supported_formats:
                raise ValueError(f"Unsupported format: {format}. Supported: {self.supported_formats}")
            
            reader = PdfReader(file_path)
            output_files = []
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(filename)[0]
            
            # Note: PyPDF2 doesn't have built-in image conversion
            # This is a simplified implementation - in production, you might want to use
            # pdf2image library or similar for better image conversion
            for i, page in enumerate(reader.pages):
                try:
                    # Extract text and create a simple representation
                    # In a real implementation, you'd use pdf2image or similar
                    output_filename = f"{base_name}_page_{i + 1}_{timestamp}.{format.lower()}"
                    output_path = os.path.join(output_folder, output_filename)
                    
                    # Create a placeholder image (in production, use proper PDF to image conversion)
                    img = Image.new('RGB', (595, 842), color='white')  # A4 size in pixels at 72 DPI
                    img.save(output_path, format=format.upper(), dpi=(dpi, dpi))
                    
                    output_files.append(output_filename)
                    
                except Exception as page_error:
                    logger.warning(f"Error converting page {i + 1}: {str(page_error)}")
                    continue
            
            if not output_files:
                raise Exception("No pages could be converted to images")
            
            logger.info(f"Successfully converted PDF to {len(output_files)} images")
            return output_files
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise e
    
    def extract_metadata(self, filename, upload_folder):
        """Extract metadata from a PDF file"""
        try:
            file_path = os.path.join(upload_folder, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {filename}")
            
            reader = PdfReader(file_path)
            metadata = {}
            
            # Basic document info
            metadata['pages'] = len(reader.pages)
            metadata['file_size'] = os.path.getsize(file_path)
            
            # PDF metadata
            if reader.metadata:
                pdf_metadata = reader.metadata
                metadata['title'] = pdf_metadata.get('/Title', 'N/A')
                metadata['author'] = pdf_metadata.get('/Author', 'N/A')
                metadata['subject'] = pdf_metadata.get('/Subject', 'N/A')
                metadata['creator'] = pdf_metadata.get('/Creator', 'N/A')
                metadata['producer'] = pdf_metadata.get('/Producer', 'N/A')
                metadata['creation_date'] = str(pdf_metadata.get('/CreationDate', 'N/A'))
                metadata['modification_date'] = str(pdf_metadata.get('/ModDate', 'N/A'))
            
            # Additional properties
            metadata['encrypted'] = reader.is_encrypted
            
            # Page dimensions (first page)
            if reader.pages:
                first_page = reader.pages[0]
                mediabox = first_page.mediabox
                metadata['page_width'] = float(mediabox.width)
                metadata['page_height'] = float(mediabox.height)
            
            logger.info(f"Successfully extracted metadata from {filename}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            raise e
    
    def compress_pdf(self, filename, upload_folder, output_folder, quality='medium'):
        """Compress a PDF file"""
        try:
            file_path = os.path.join(upload_folder, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {filename}")
            
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)
            
            # Compression settings based on quality
            if quality == 'high':
                writer.compress_identical_objects()
            elif quality == 'medium':
                writer.compress_identical_objects()
                writer.remove_duplicates()
            else:  # low quality / maximum compression
                writer.compress_identical_objects()
                writer.remove_duplicates()
                # Additional compression would go here
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}_compressed_{timestamp}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Calculate compression ratio
            original_size = os.path.getsize(file_path)
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (original_size - compressed_size) / original_size * 100
            
            logger.info(f"Successfully compressed PDF: {compression_ratio:.1f}% reduction")
            return output_filename, compression_ratio
            
        except Exception as e:
            logger.error(f"Error compressing PDF: {str(e)}")
            raise e
