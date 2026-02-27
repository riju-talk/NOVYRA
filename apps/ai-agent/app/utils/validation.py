"""
NOVYRA Security - Input Validation

Comprehensive input validation and sanitization.
"""
import logging
import re
from typing import Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


class ContentType(str, Enum):
    """Content types for validation."""
    DOUBT = "doubt"
    ANSWER = "answer"
    COMMENT = "comment"
    PROFILE = "profile"


# Validation rules
MAX_DOUBT_LENGTH = 10000
MAX_ANSWER_LENGTH = 20000
MAX_COMMENT_LENGTH = 2000
MAX_TITLE_LENGTH = 200
MAX_TAG_LENGTH = 50
MAX_TAGS_COUNT = 10

MIN_DOUBT_LENGTH = 10
MIN_ANSWER_LENGTH = 10
MIN_COMMENT_LENGTH = 1

# Regex patterns
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
URL_PATTERN = re.compile(r'^https?://[^\s]+$')
TAG_PATTERN = re.compile(r'^[a-zA-Z0-9-]+$')

# Dangerous patterns (SQL injection, XSS, etc.)
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE)\b)",
    r"(--|;|\/\*|\*\/)",
    r"('|\")(or|and)\s*\1\s*=\s*\1"
]

XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe",
    r"<embed",
    r"<object"
]


def sanitize_text(text: str) -> str:
    """
    Sanitize text input.
    
    Removes dangerous patterns while preserving content.
    
    Args:
        text: Raw text input
    
    Returns:
        Sanitized text
    """
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text


def validate_text_length(
    text: str,
    min_length: int,
    max_length: int,
    field_name: str = "text"
) -> None:
    """
    Validate text length.
    
    Args:
        text: Text to validate
        min_length: Minimum length
        max_length: Maximum length
        field_name: Field name for error message
    
    Raises:
        ValidationError: If length is invalid
    """
    length = len(text)
    
    if length < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters (got {length})"
        )
    
    if length > max_length:
        raise ValidationError(
            f"{field_name} must be at most {max_length} characters (got {length})"
        )


def validate_no_sql_injection(text: str) -> None:
    """
    Check for SQL injection attempts.
    
    Args:
        text: Text to check
    
    Raises:
        ValidationError: If SQL injection pattern detected
    """
    text_lower = text.lower()
    
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.warning(f"SQL injection attempt detected: {pattern}")
            raise ValidationError("Invalid input: potentially malicious content detected")


def validate_no_xss(text: str) -> None:
    """
    Check for XSS attempts.
    
    Args:
        text: Text to check
    
    Raises:
        ValidationError: If XSS pattern detected
    """
    text_lower = text.lower()
    
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.warning(f"XSS attempt detected: {pattern}")
            raise ValidationError("Invalid input: potentially malicious content detected")


def validate_username(username: str) -> None:
    """
    Validate username format.
    
    Args:
        username: Username to validate
    
    Raises:
        ValidationError: If username is invalid
    """
    if not USERNAME_PATTERN.match(username):
        raise ValidationError(
            "Username must be 3-30 characters, alphanumeric, hyphens, or underscores only"
        )


def validate_email(email: str) -> None:
    """
    Validate email format.
    
    Args:
        email: Email to validate
    
    Raises:
        ValidationError: If email is invalid
    """
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Invalid email format")


def validate_url(url: str) -> None:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
    
    Raises:
        ValidationError: If URL is invalid
    """
    if not URL_PATTERN.match(url):
        raise ValidationError("Invalid URL format (must start with http:// or https://)")


def validate_tags(tags: List[str]) -> None:
    """
    Validate tags.
    
    Args:
        tags: List of tags
    
    Raises:
        ValidationError: If tags are invalid
    """
    if len(tags) > MAX_TAGS_COUNT:
        raise ValidationError(f"Maximum {MAX_TAGS_COUNT} tags allowed")
    
    for tag in tags:
        if len(tag) > MAX_TAG_LENGTH:
            raise ValidationError(f"Tag '{tag}' exceeds {MAX_TAG_LENGTH} characters")
        
        if not TAG_PATTERN.match(tag):
            raise ValidationError(f"Tag '{tag}' contains invalid characters")


def validate_doubt(
    title: str,
    content: str,
    tags: List[str]
) -> tuple[str, str, List[str]]:
    """
    Validate doubt submission.
    
    Args:
        title: Doubt title
        content: Doubt content
        tags: Doubt tags
    
    Returns:
        Sanitized (title, content, tags)
    
    Raises:
        ValidationError: If validation fails
    """
    # Sanitize
    title = sanitize_text(title)
    content = sanitize_text(content)
    tags = [sanitize_text(tag) for tag in tags]
    
    # Validate lengths
    validate_text_length(title, 5, MAX_TITLE_LENGTH, "Title")
    validate_text_length(content, MIN_DOUBT_LENGTH, MAX_DOUBT_LENGTH, "Content")
    
    # Validate security
    validate_no_sql_injection(title)
    validate_no_sql_injection(content)
    validate_no_xss(content)
    
    # Validate tags
    validate_tags(tags)
    
    return title, content, tags


def validate_answer(content: str) -> str:
    """
    Validate answer submission.
    
    Args:
        content: Answer content
    
    Returns:
        Sanitized content
    
    Raises:
        ValidationError: If validation fails
    """
    # Sanitize
    content = sanitize_text(content)
    
    # Validate length
    validate_text_length(content, MIN_ANSWER_LENGTH, MAX_ANSWER_LENGTH, "Answer")
    
    # Validate security
    validate_no_sql_injection(content)
    validate_no_xss(content)
    
    return content


def validate_comment(content: str) -> str:
    """
    Validate comment submission.
    
    Args:
        content: Comment content
    
    Returns:
        Sanitized content
    
    Raises:
        ValidationError: If validation fails
    """
    # Sanitize
    content = sanitize_text(content)
    
    # Validate length
    validate_text_length(content, MIN_COMMENT_LENGTH, MAX_COMMENT_LENGTH, "Comment")
    
    # Validate security
    validate_no_sql_injection(content)
    validate_no_xss(content)
    
    return content


def validate_search_query(query: str) -> str:
    """
    Validate search query.
    
    Args:
        query: Search query
    
    Returns:
        Sanitized query
    
    Raises:
        ValidationError: If validation fails
    """
    # Sanitize
    query = sanitize_text(query)
    
    # Validate length
    if len(query) < 1:
        raise ValidationError("Search query cannot be empty")
    
    if len(query) > 200:
        raise ValidationError("Search query too long (max 200 characters)")
    
    # Validate security
    validate_no_sql_injection(query)
    
    return query


def validate_user_id(user_id: str) -> None:
    """
    Validate user ID format.
    
    Args:
        user_id: User ID to validate
    
    Raises:
        ValidationError: If user ID is invalid
    """
    # Assuming UUIDs or similar
    if not re.match(r'^[a-zA-Z0-9_-]{10,50}$', user_id):
        raise ValidationError("Invalid user ID format")


def validate_pagination(
    page: int,
    page_size: int,
    max_page_size: int = 100
) -> tuple[int, int]:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        max_page_size: Maximum page size
    
    Returns:
        Validated (page, page_size)
    
    Raises:
        ValidationError: If pagination is invalid
    """
    if page < 1:
        raise ValidationError("Page number must be >= 1")
    
    if page_size < 1:
        raise ValidationError("Page size must be >= 1")
    
    if page_size > max_page_size:
        raise ValidationError(f"Page size must be <= {max_page_size}")
    
    return page, page_size


logger.info("Input validation utilities initialized")
