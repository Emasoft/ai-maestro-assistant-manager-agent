#!/usr/bin/env python3
"""
EAMA Design Search Script

Search design documents in the project for:
- UUID matches
- Keyword/text matches
- Status filtering (draft, approved, deprecated)

Usage:
    python eama_design_search.py --uuid abc123
    python eama_design_search.py --keyword "authentication"
    python eama_design_search.py --status approved
    python eama_design_search.py --list
    python eama_design_search.py --keyword "auth" --status draft

Output: JSON for programmatic use, human-readable summary to stderr
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, cast


@dataclass
class DesignDocument:
    """Represents a design document with metadata."""

    path: str
    uuid: Optional[str]
    title: str
    status: str
    created: Optional[str]
    modified: Optional[str]
    keywords: list[str]
    summary: str


def get_project_dir() -> Path:
    """Get the project directory from environment or current directory."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    return Path(project_dir)


def find_design_directories(project_dir: Path) -> list[Path]:
    """Find all design-related directories in the project."""
    design_dirs = []

    # Common design directory names
    design_patterns = [
        "design",
        "designs",
        "specs",
        "specifications",
        "architecture",
        "docs/design",
        "docs/specs",
        "docs/architecture",
    ]

    for pattern in design_patterns:
        design_path = project_dir / pattern
        if design_path.is_dir():
            design_dirs.append(design_path)

    return design_dirs


def extract_uuid_from_content(content: str) -> Optional[str]:
    """Extract UUID from document content (frontmatter or body)."""
    # Check YAML frontmatter for uuid field
    frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        uuid_match = re.search(r"uuid:\s*([a-f0-9-]+)", frontmatter, re.IGNORECASE)
        if uuid_match:
            return uuid_match.group(1)

    # Check for UUID in document body (EAMA-UUID: format)
    body_uuid_match = re.search(r"EAMA-UUID:\s*([a-f0-9-]+)", content, re.IGNORECASE)
    if body_uuid_match:
        return body_uuid_match.group(1)

    # Check for standalone UUID format in first 500 chars
    early_uuid_match = re.search(
        r"\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b",
        content[:500],
        re.IGNORECASE,
    )
    if early_uuid_match:
        return early_uuid_match.group(1)

    return None


def extract_status_from_content(content: str) -> str:
    """Extract status from document content."""
    # Check frontmatter for status
    frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        status_match = re.search(
            r"status:\s*(draft|approved|review|deprecated|archived)",
            frontmatter,
            re.IGNORECASE,
        )
        if status_match:
            return status_match.group(1).lower()

    # Check body for status markers
    status_patterns = [
        (r"\*\*Status\*\*:\s*(draft|approved|review|deprecated|archived)", 1),
        (r"Status:\s*(draft|approved|review|deprecated|archived)", 1),
        (r"\[DRAFT\]", "draft"),
        (r"\[APPROVED\]", "approved"),
        (r"\[DEPRECATED\]", "deprecated"),
    ]

    for pattern, group_or_value in status_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            if isinstance(group_or_value, int):
                return match.group(group_or_value).lower()
            return cast(str, group_or_value)

    return "unknown"


def extract_title_from_content(content: str, filename: str) -> str:
    """Extract title from document content."""
    # Check frontmatter for title
    frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        title_match = re.search(
            r'title:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE
        )
        if title_match:
            return title_match.group(1).strip()

    # Check for first H1 heading
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()

    # Fall back to filename
    return filename.replace(".md", "").replace("-", " ").replace("_", " ").title()


def extract_keywords_from_content(content: str) -> list[str]:
    """Extract keywords from document content."""
    keywords: set[str] = set()

    # Check frontmatter for keywords/tags
    frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # keywords: [a, b, c] or keywords: - a format
        keywords_match = re.search(r"keywords:\s*\[([^\]]+)\]", frontmatter)
        if keywords_match:
            keywords.update(
                k.strip().strip("'\"") for k in keywords_match.group(1).split(",")
            )

        tags_match = re.search(r"tags:\s*\[([^\]]+)\]", frontmatter)
        if tags_match:
            keywords.update(
                k.strip().strip("'\"") for k in tags_match.group(1).split(",")
            )

    return list(keywords)


def extract_summary_from_content(content: str) -> str:
    """Extract summary/description from document content."""
    # Check frontmatter for description
    frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        desc_match = re.search(
            r'description:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE
        )
        if desc_match:
            return desc_match.group(1).strip()[:200]

    # Get first non-heading, non-empty paragraph after frontmatter
    content_after_frontmatter = re.sub(
        r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL
    )
    paragraphs = re.split(r"\n\n+", content_after_frontmatter)

    for para in paragraphs:
        para = para.strip()
        # Skip headings, lists, code blocks
        if (
            para
            and not para.startswith("#")
            and not para.startswith("-")
            and not para.startswith("```")
        ):
            return para[:200] + ("..." if len(para) > 200 else "")

    return ""


def parse_design_document(file_path: Path) -> Optional[DesignDocument]:
    """Parse a design document and extract metadata."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    stat = file_path.stat()

    return DesignDocument(
        path=str(file_path),
        uuid=extract_uuid_from_content(content),
        title=extract_title_from_content(content, file_path.name),
        status=extract_status_from_content(content),
        created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
        modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
        keywords=extract_keywords_from_content(content),
        summary=extract_summary_from_content(content),
    )


def scan_design_documents(project_dir: Path) -> list[DesignDocument]:
    """Scan all design directories and parse documents."""
    documents = []
    design_dirs = find_design_directories(project_dir)

    for design_dir in design_dirs:
        for md_file in design_dir.rglob("*.md"):
            doc = parse_design_document(md_file)
            if doc:
                documents.append(doc)

    return documents


def search_by_uuid(
    documents: list[DesignDocument], uuid_query: str
) -> list[DesignDocument]:
    """Search documents by UUID (partial match supported)."""
    uuid_query = uuid_query.lower()
    return [doc for doc in documents if doc.uuid and uuid_query in doc.uuid.lower()]


def search_by_keyword(
    documents: list[DesignDocument], keyword: str
) -> list[DesignDocument]:
    """Search documents by keyword in title, summary, or keywords list."""
    keyword = keyword.lower()
    results = []

    for doc in documents:
        # Search in title
        if keyword in doc.title.lower():
            results.append(doc)
            continue

        # Search in summary
        if keyword in doc.summary.lower():
            results.append(doc)
            continue

        # Search in keywords
        if any(keyword in kw.lower() for kw in doc.keywords):
            results.append(doc)
            continue

        # Search in file path
        if keyword in doc.path.lower():
            results.append(doc)

    return results


def filter_by_status(
    documents: list[DesignDocument], status: str
) -> list[DesignDocument]:
    """Filter documents by status."""
    status = status.lower()
    return [doc for doc in documents if doc.status == status]


def document_to_dict(doc: DesignDocument) -> dict[str, Any]:
    """Convert DesignDocument to dictionary for JSON output."""
    return {
        "path": doc.path,
        "uuid": doc.uuid,
        "title": doc.title,
        "status": doc.status,
        "created": doc.created,
        "modified": doc.modified,
        "keywords": doc.keywords,
        "summary": doc.summary,
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Search design documents in the project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --uuid abc123              Search by UUID (partial match)
  %(prog)s --keyword authentication   Search by keyword
  %(prog)s --status approved          Filter by status
  %(prog)s --list                     List all design documents
  %(prog)s --keyword auth --status draft  Combined search
        """,
    )

    parser.add_argument("--uuid", help="Search by UUID (partial match supported)")
    parser.add_argument("--keyword", help="Search by keyword in title/summary/keywords")
    parser.add_argument(
        "--status",
        choices=["draft", "approved", "review", "deprecated", "archived", "unknown"],
        help="Filter by document status",
    )
    parser.add_argument("--list", action="store_true", help="List all design documents")
    parser.add_argument(
        "--project-dir", help="Project directory (default: $CLAUDE_PROJECT_DIR or cwd)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON (default)")
    parser.add_argument(
        "--summary", action="store_true", help="Print human-readable summary to stderr"
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.uuid, args.keyword, args.status, args.list]):
        parser.error(
            "At least one search option required: --uuid, --keyword, --status, or --list"
        )

    # Get project directory
    if args.project_dir:
        project_dir = Path(args.project_dir)
    else:
        project_dir = get_project_dir()

    if not project_dir.is_dir():
        print(json.dumps({"error": f"Project directory not found: {project_dir}"}))
        return 1

    # Scan documents
    documents = scan_design_documents(project_dir)

    if not documents:
        result = {"results": [], "count": 0, "message": "No design documents found"}
        print(json.dumps(result, indent=2))
        return 0

    # Apply filters
    results = documents

    if args.uuid:
        results = search_by_uuid(results, args.uuid)

    if args.keyword:
        results = search_by_keyword(results, args.keyword)

    if args.status:
        results = filter_by_status(results, args.status)

    # Output results
    output = {
        "results": [document_to_dict(doc) for doc in results],
        "count": len(results),
        "total_scanned": len(documents),
        "project_dir": str(project_dir),
    }

    print(json.dumps(output, indent=2))

    # Print summary to stderr if requested
    if args.summary:
        print("\n--- Design Search Results ---", file=sys.stderr)
        print(f"Found: {len(results)} of {len(documents)} documents", file=sys.stderr)
        for doc in results:
            status_icon = {"approved": "[+]", "draft": "[.]", "deprecated": "[-]"}.get(
                doc.status, "[?]"
            )
            print(f"  {status_icon} {doc.title}", file=sys.stderr)
            print(f"      Path: {doc.path}", file=sys.stderr)
            if doc.uuid:
                print(f"      UUID: {doc.uuid}", file=sys.stderr)
        print(file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
