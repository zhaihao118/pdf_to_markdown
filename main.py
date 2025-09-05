#!/usr/bin/env python3
"""
Knowledge Utils - PDF Processing and Report Merging Tool

This tool provides functionality to:
1. Parse PDF files and extract structured content
2. Process and merge parsed reports with text cleaning
3. Export results to various formats (JSON, Markdown)

Usage:
    python main.py --help
    python main.py parse --input pdfs/ --output parsed_reports/
    python main.py merge --input parsed_reports/ --output merged_reports/
    python main.py export --input merged_reports/ --output markdown/ --format markdown
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List
import json
import logging

from src.pdf_parsing import PDFParser
from src.parsed_reports_merging import PageTextPreparation

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_utils.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def setup_directories(*dirs: Path) -> None:
    """Create directories if they don't exist."""
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ready: {directory}")


def parse_pdfs(input_dir: Path, output_dir: Path, **kwargs) -> None:
    """Parse PDF files from input directory and save results to output directory."""
    logger.info(f"Starting PDF parsing from {input_dir} to {output_dir}")
    
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return
    
    setup_directories(output_dir)
    
    # Get all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Initialize parser with output directory
    parser = PDFParser(output_dir=output_dir)
    
    # Process all PDFs at once using the correct method
    try:
        parser.parse_and_export(input_doc_paths=pdf_files)
        logger.info("PDF parsing completed successfully")
    except Exception as e:
        logger.error(f"Error during PDF parsing: {str(e)}")
        raise


def merge_reports(input_dir: Path, output_dir: Path, **kwargs) -> None:
    """Process and merge parsed reports with text cleaning."""
    logger.info(f"Starting report merging from {input_dir} to {output_dir}")
    
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return
    
    setup_directories(output_dir)
    
    # Get configuration options
    use_serialized_tables = kwargs.get('use_serialized_tables', False)
    serialized_instead_of_markdown = kwargs.get('serialized_instead_of_markdown', False)
    
    # Initialize processor
    processor = PageTextPreparation(
        use_serialized_tables=use_serialized_tables,
        serialized_tables_instead_of_markdown=serialized_instead_of_markdown
    )
    
    # Process reports
    try:
        processed_reports = processor.process_reports(
            reports_dir=input_dir,
            output_dir=output_dir
        )
        
        logger.info(f"Successfully processed {len(processed_reports)} reports")
        
        # Save summary
        summary = {
            "total_reports": len(processed_reports),
            "reports": [
                {
                    "name": report["metainfo"].get("sha1_name", "unknown"),
                    "pages": len(report["content"]["pages"])
                }
                for report in processed_reports
            ]
        }
        
        summary_file = output_dir / "processing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processing summary saved to: {summary_file}")
        
    except Exception as e:
        logger.error(f"Error during report merging: {str(e)}")
        raise


def export_reports(input_dir: Path, output_dir: Path, format_type: str = "markdown", **kwargs) -> None:
    """Export processed reports to specified format."""
    logger.info(f"Starting export from {input_dir} to {output_dir} in {format_type} format")
    
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return
    
    setup_directories(output_dir)
    
    if format_type.lower() == "markdown":
        # Initialize processor for markdown export
        processor = PageTextPreparation()
        
        try:
            processor.export_to_markdown(input_dir, output_dir)
            logger.info("Markdown export completed successfully")
        except Exception as e:
            logger.error(f"Error during markdown export: {str(e)}")
            raise
    else:
        logger.error(f"Unsupported export format: {format_type}")
        return


def list_files_info(directory: Path) -> None:
    """List files in directory with basic information."""
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        return
    
    files = list(directory.glob("*"))
    if not files:
        logger.info(f"No files found in {directory}")
        return
    
    logger.info(f"Files in {directory}:")
    for file_path in sorted(files):
        if file_path.is_file():
            size = file_path.stat().st_size
            logger.info(f"  FILE {file_path.name} ({size:,} bytes)")
        elif file_path.is_dir():
            count = len(list(file_path.glob("*")))
            logger.info(f"  DIR {file_path.name}/ ({count} items)")


def main():
    """Main entry point for the knowledge utils tool."""
    parser = argparse.ArgumentParser(
        description="Knowledge Utils - PDF Processing and Report Merging Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse all PDFs in pdfs/ directory
  python main.py parse --input pdfs/ --output parsed_reports/
  
  # Merge parsed reports with text cleaning
  python main.py merge --input parsed_reports/ --output merged_reports/
  
  # Export to markdown format
  python main.py export --input merged_reports/ --output markdown/ --format markdown
  
  # List files in a directory
  python main.py list --directory pdfs/
  
  # Full pipeline
  python main.py pipeline --input pdfs/ --output final_output/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse PDF files')
    parse_parser.add_argument('--input', '-i', type=Path, required=True,
                             help='Input directory containing PDF files')
    parse_parser.add_argument('--output', '-o', type=Path, required=True,
                             help='Output directory for parsed JSON files')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Process and merge parsed reports')
    merge_parser.add_argument('--input', '-i', type=Path, required=True,
                             help='Input directory containing parsed JSON files')
    merge_parser.add_argument('--output', '-o', type=Path, required=True,
                             help='Output directory for merged reports')
    merge_parser.add_argument('--use-serialized-tables', action='store_true',
                             help='Use serialized table format')
    merge_parser.add_argument('--serialized-instead-of-markdown', action='store_true',
                             help='Use serialized tables instead of markdown tables')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export processed reports')
    export_parser.add_argument('--input', '-i', type=Path, required=True,
                              help='Input directory containing processed reports')
    export_parser.add_argument('--output', '-o', type=Path, required=True,
                              help='Output directory for exported files')
    export_parser.add_argument('--format', '-f', choices=['markdown'], default='markdown',
                              help='Export format (default: markdown)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List files in directory')
    list_parser.add_argument('--directory', '-d', type=Path, required=True,
                            help='Directory to list')
    
    # Pipeline command (runs all steps)
    pipeline_parser = subparsers.add_parser('pipeline', help='Run complete processing pipeline')
    pipeline_parser.add_argument('--input', '-i', type=Path, required=True,
                                 help='Input directory containing PDF files')
    pipeline_parser.add_argument('--output', '-o', type=Path, required=True,
                                 help='Base output directory')
    pipeline_parser.add_argument('--use-serialized-tables', action='store_true',
                                help='Use serialized table format')
    pipeline_parser.add_argument('--serialized-instead-of-markdown', action='store_true',
                                help='Use serialized tables instead of markdown tables')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'parse':
            parse_pdfs(args.input, args.output)
            
        elif args.command == 'merge':
            merge_reports(
                args.input, 
                args.output,
                use_serialized_tables=args.use_serialized_tables,
                serialized_instead_of_markdown=args.serialized_instead_of_markdown
            )
            
        elif args.command == 'export':
            export_reports(args.input, args.output, args.format)
            
        elif args.command == 'list':
            list_files_info(args.directory)
            
        elif args.command == 'pipeline':
            logger.info("Starting complete processing pipeline")
            
            # Create intermediate directories
            parsed_dir = args.output / "parsed"
            merged_dir = args.output / "merged"
            final_dir = args.output / "markdown"
            
            # Step 1: Parse PDFs
            logger.info("Step 1/3: Parsing PDFs")
            parse_pdfs(args.input, parsed_dir)
            
            # Step 2: Merge reports
            logger.info("Step 2/3: Merging reports")
            merge_reports(
                parsed_dir, 
                merged_dir,
                use_serialized_tables=args.use_serialized_tables,
                serialized_instead_of_markdown=args.serialized_instead_of_markdown
            )
            
            # Step 3: Export to markdown
            logger.info("Step 3/3: Exporting to markdown")
            export_reports(merged_dir, final_dir, "markdown")
            
            logger.info(f"Pipeline completed! Results available in: {args.output}")
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()