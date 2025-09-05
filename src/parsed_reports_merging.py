import re
from typing import List, Tuple
from pathlib import Path
import json

class PageTextPreparation:
    """
    Cleans and formats page blocks according to rules, handling consecutive 
    groups for tables, lists, and footnotes.
    """

    def __init__(self, use_serialized_tables: bool = False, serialized_tables_instead_of_markdown: bool = False):
        """Initialize with option to add serialized tables to markdown ones."""
        self.use_serialized_tables = use_serialized_tables
        self.serialized_tables_instead_of_markdown = serialized_tables_instead_of_markdown

    def process_reports(
        self, 
        reports_dir: Path = None, 
        reports_paths: List[Path] = None, 
        output_dir: Path = None
    ):
        """
        Process reports from a directory or list of paths, returning a list of processed reports 
        and saving them to an output directory if specified.
        """
        all_reports = []
        
        if reports_dir:
            reports_paths = list(reports_dir.glob('*.json'))
        
        for report_path in reports_paths:
            with open(report_path, 'r', encoding='utf-8') as file:
                report_data = json.load(file)
            
            full_report_text = self.process_report(report_data)
            report = {"metainfo": report_data['metainfo'], "content": full_report_text}
            all_reports.append(report)
            
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                with open(output_dir / report_path.name, 'w', encoding='utf-8') as file:
                    json.dump(report, file, indent=2, ensure_ascii=False)
        
        return all_reports
        
    def process_report(self, report_data):
        """
        Process a single report, returning a list of processed pages and printing a message if corrections were made.
        """
        self.report_data = report_data
        processed_pages = []
        total_corrections = 0
        corrections_list = []

        for page_content in self.report_data["content"]:
            page_number = page_content["page"]
            page_text = self.prepare_page_text(page_number)
            cleaned_text, corrections_count, corrections = self._clean_text(page_text)
            total_corrections += corrections_count
            corrections_list.extend(corrections)
            page_data = {
                "page": page_number,
                "text": cleaned_text
            }
            processed_pages.append(page_data)
        
        if total_corrections > 0:
            print(
                f"Fixed {total_corrections} occurrences in the file "
                f"{self.report_data['metainfo']['sha1_name']}"
            )
            print(corrections_list[:30])
        
        processed_report = {
            "chunks": None,
            "pages": processed_pages
        }
        
        return processed_report

    def prepare_page_text(self, page_number):
        """Main method to process page blocks and return assembled string."""
        page_data = self._get_page_data(page_number)
        if not page_data or "content" not in page_data:
            return ""

        blocks = page_data["content"]

        filtered_blocks = self._filter_blocks(blocks)
        final_blocks = self._apply_formatting_rules(filtered_blocks)

        if final_blocks:
            final_blocks[0] = final_blocks[0].lstrip()
            final_blocks[-1] = final_blocks[-1].rstrip()

        return "\n".join(final_blocks)

    def _get_page_data(self, page_number):
        """Returns page dict for given page number, or None if not found."""
        all_pages = self.report_data.get("content", [])
        for page in all_pages:
            if page.get("page") == page_number:
                return page
        return None

    def _filter_blocks(self, blocks):
        """Remove blocks of ignored types."""
        ignored_types = {"page_footer", "picture"}
        filtered_blocks = []
        for block in blocks:
            block_type = block.get("type")
            if block_type in ignored_types:
                continue
            filtered_blocks.append(block)
        return filtered_blocks
    
    def _clean_text(self, text):
        """Clean text using regex substitutions and count corrections."""
        command_mapping = {
            'zero': '0',
            'one': '1', 
            'two': '2',
            'three': '3',
            'four': '4',
            'five': '5',
            'six': '6',
            'seven': '7',
            'eight': '8',
            'nine': '9',
            'period': '.',
            'comma': ',',
            'colon': ":",
            'hyphen': "-",
            'percent': '%',
            'dollar': '$',
            'space': ' ',
            'plus': '+',
            'minus': '-',
            'slash': '/',
            'asterisk': '*',
            'lparen': '(',
            'rparen': ')',
            'parenright': ')',
            'parenleft': '(',
            'wedge.1_E': '',
        }

        recognized_commands = "|".join(command_mapping.keys())
        slash_command_pattern = rf"/({recognized_commands})(\.pl\.tnum|\.tnum\.pl|\.pl|\.tnum|\.case|\.sups)"

        occurrences_amount = len(re.findall(slash_command_pattern, text))
        occurrences_amount += len(re.findall(r'glyph<[^>]*>', text))
        occurrences_amount += len(re.findall(r'/([A-Z])\.cap', text))

        corrections = []

        def replace_command(match):
            base_command = match.group(1)
            replacement = command_mapping.get(base_command)
            if replacement is not None:
                corrections.append((match.group(0), replacement))
            return replacement if replacement is not None else match.group(0)

        def replace_glyph(match):
            corrections.append((match.group(0), ''))
            return ''

        def replace_cap(match):
            original = match.group(0)
            replacement = match.group(1)
            corrections.append((original, replacement))
            return replacement

        text = re.sub(slash_command_pattern, replace_command, text)
        text = re.sub(r'glyph<[^>]*>', replace_glyph, text)
        text = re.sub(r'/([A-Z])\.cap', replace_cap, text)

        return text, occurrences_amount, corrections
    
    def _block_ends_with_colon(self, block):
        """Check if block text ends with colon for relevant block types."""
        block_type = block.get("type")
        text = block.get("text", "").rstrip()
        if block_type in {"text", "caption", "section_header", "paragraph"}:
            return text.endswith(":")
        return False

    def _apply_formatting_rules(self, blocks):
        """Transform blocks according to formatting rules."""
        page_header_in_first_3 = False
        section_header_in_first_3 = False
        for blk in blocks[:3]:
            if blk["type"] == "page_header":
                page_header_in_first_3 = True
            if blk["type"] == "section_header":
                section_header_in_first_3 = True

        final_blocks = []
        first_section_header_index = 0

        i = 0
        n = len(blocks)

        while i < n:
            block = blocks[i]
            block_type = block.get("type")
            text = block.get("text", "").strip()

            # Handle headers
            if block_type == "page_header":
                prefix = "\n# " if i < 3 else "\n## "
                final_blocks.append(f"{prefix}{text}\n")
                i += 1
                continue

            if block_type == "section_header":
                first_section_header_index += 1
                if (
                    first_section_header_index == 1
                    and i < 3
                    and not page_header_in_first_3
                ):
                    prefix = "\n# "
                else:
                    prefix = "\n## "
                final_blocks.append(f"{prefix}{text}\n")
                i += 1
                continue

            if block_type == "paragraph":
                if self._block_ends_with_colon(block) and i + 1 < n:
                    next_block_type = blocks[i + 1].get("type")
                    if next_block_type not in ("table", "list_item"):
                        final_blocks.append(f"\n### {text}\n")
                        i += 1
                        continue
                else:
                    final_blocks.append(f"\n### {text}\n")
                    i += 1
                    continue

            # Handle table groups
            if block_type == "table" or (
                self._block_ends_with_colon(block)
                and i + 1 < n
                and blocks[i + 1].get("type") == "table"
            ):
                group_blocks = []
                header_for_table = None
                if self._block_ends_with_colon(block) and i + 1 < n:
                    header_for_table = block
                    table_block = blocks[i + 1]
                    i += 2
                else:
                    table_block = block
                    i += 1

                if header_for_table:
                    group_blocks.append(header_for_table)
                group_blocks.append(table_block)

                footnote_candidates_start = i
                if i < n:
                    maybe_text_block = blocks[i]
                    if maybe_text_block.get("type") == "text":
                        if (i + 1 < n) and (blocks[i + 1].get("type") == "footnote"):
                            group_blocks.append(maybe_text_block)
                            i += 1

                while i < n and blocks[i].get("type") == "footnote":
                    group_blocks.append(blocks[i])
                    i += 1

                group_text = self._render_table_group(group_blocks)
                final_blocks.append(group_text)
                continue

            # Handle list groups
            if block_type == "list_item" or (
                self._block_ends_with_colon(block)
                and i + 1 < n
                and blocks[i + 1].get("type") == "list_item"
            ):
                group_blocks = []
                if self._block_ends_with_colon(block) and i + 1 < n:
                    header_for_list = block
                    i += 1
                    group_blocks.append(header_for_list)

                while i < n and blocks[i].get("type") == "list_item":
                    group_blocks.append(blocks[i])
                    i += 1

                if i < n and blocks[i].get("type") == "text":
                    if (i + 1 < n) and (blocks[i + 1].get("type") == "footnote"):
                        group_blocks.append(blocks[i])
                        i += 1

                while i < n and blocks[i].get("type") == "footnote":
                    group_blocks.append(blocks[i])
                    i += 1

                group_text = self._render_list_group(group_blocks)
                final_blocks.append(group_text)
                continue

            # Handle normal blocks
            if block_type in (
                "text",
                "caption",
                "footnote",
                "checkbox_selected",
                "checkbox_unselected",
                "formula",
            ):
                if not text.strip():
                    i += 1
                    continue
                else:
                    final_blocks.append(f"{text}\n")
                    i += 1
                continue

            raise ValueError(f"Unknown block type: {block_type}")

        return final_blocks

    def _render_table_group(self, group_blocks):
        """Render table group with optional header, text and footnotes."""
        chunk = []
        for blk in group_blocks:
            blk_type = blk.get("type")
            blk_text = blk.get("text", "").strip()
            if blk_type in {"text", "caption", "section_header", "paragraph"}:
                chunk.append(f"{blk_text}\n")

            elif blk_type == "table":
                table_id = blk.get("table_id")
                if table_id is None:
                    continue
                table_markdown = self._get_table_by_id(table_id)
                chunk.append(f"{table_markdown}\n")

            elif blk_type == "footnote":
                chunk.append(f"{blk_text}\n")

            elif blk_type == "text":
                chunk.append(f"{blk_text}\n")

            else:
                raise ValueError(f"Unexpected block type in table group: {blk_type}")

        return "\n" + "".join(chunk) + "\n"

    def _render_list_group(self, group_blocks):
        """Render list group with optional header, text and footnotes."""
        chunk = []
        for blk in group_blocks:
            blk_type = blk.get("type")
            blk_text = blk.get("text", "").strip()
            if blk_type in {"text", "caption", "section_header", "paragraph"}:
                chunk.append(f"{blk_text}\n")

            elif blk_type == "list_item":
                chunk.append(f"- {blk_text}\n")

            elif blk_type == "footnote":
                chunk.append(f"{blk_text}\n")

            elif blk_type == "checkbox_selected":
                chunk.append(f"[x] {blk_text}\n")

            elif blk_type == "checkbox_unselected":
                chunk.append(f"[ ] {blk_text}\n")

            else:
                chunk.append(f"{blk_text}\n")

        return "\n" + "".join(chunk) + "\n"

    def _get_table_by_id(self, table_id):
        """Get table representation by ID from report data.
        Returns markdown or serialized text based on configuration."""
        for t in self.report_data.get("tables", []):
            if t.get("table_id") == table_id:
                if self.use_serialized_tables:
                    return self._get_serialized_table_text(t, self.serialized_tables_instead_of_markdown)
                return t.get("markdown", "")
        raise ValueError(f"Table with ID={table_id} not found in report_data!")
    
    def _get_serialized_table_text(self, table, serialized_tables_instead_of_markdown):
        """Convert serialized table format to text string.
        
        Args:
            table: Table object containing serialized data
            
        Returns:
            String containing concatenated information blocks or markdown as fallback
        """
        if not table.get("serialized"):
            return table.get("markdown", "")
            
        info_blocks = table["serialized"].get("information_blocks", [])
        text_blocks = [block["information_block"] for block in info_blocks]
        serialized_text = "\n".join(text_blocks)
        if serialized_tables_instead_of_markdown:
            return serialized_text
        else:
            markdown = table.get("markdown", "")
            combined_text = f"{markdown}\nDescription of the table entities:\n{serialized_text}"
            return combined_text

    def export_to_markdown(self, reports_dir: Path, output_dir: Path):
        """Export processed reports to markdown files.
        
        Args:
            reports_dir: Directory containing JSON report files
            output_dir: Directory where markdown files will be saved
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for report_path in reports_dir.glob("*.json"):
            # Skip the processing summary file
            if report_path.name == "processing_summary.json":
                continue
                
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Check if this is already a processed report (has content.pages structure)
            if 'content' in report_data and 'pages' in report_data['content']:
                # This is already processed, just extract the text
                document_text = ""
                for page in report_data['content']['pages']:
                    document_text += f"\n\n---\n\n# Page {page['page']}\n\n"
                    document_text += page['text']
                
                report_name = report_data['metainfo']['sha1_name']
                with open(output_dir / f"{report_name}.md", "w", encoding="utf-8") as f:
                    f.write(document_text)
            else:
                # This is raw report data, need to process it first
                processed_report = self.process_report(report_data)
                
                document_text = ""
                for page in processed_report['pages']:
                    document_text += f"\n\n---\n\n# Page {page['page']}\n\n"
                    document_text += page['text']
                
                report_name = report_data['metainfo']['sha1_name']
                with open(output_dir / f"{report_name}.md", "w", encoding="utf-8") as f:
                    f.write(document_text)
