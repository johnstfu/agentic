"""
Tests for input validators
"""

import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.validators import sanitize_claim, validate_user_id, sanitize_feedback_comment


class TestSanitizeClaim:
    """Tests for sanitize_claim function"""
    
    def test_valid_claim(self):
        """Test with valid claim"""
        result = sanitize_claim("La Tour Eiffel mesure 330 mètres")
        assert result == "La Tour Eiffel mesure 330 mètres"
    
    def test_claim_with_extra_spaces(self):
        """Test claim with multiple spaces"""
        result = sanitize_claim("  La Tour Eiffel   mesure  330m  ")
        assert result == "La Tour Eiffel mesure 330m"
    
    def test_claim_too_short(self):
        """Test claim shorter than 10 chars"""
        result = sanitize_claim("Trop")  # 4 chars
        assert result is None
    
    def test_claim_too_long(self):
        """Test claim longer than 500 chars"""
        long_claim = "A" * 501
        result = sanitize_claim(long_claim)
        assert result is None
    
    def test_claim_with_dangerous_chars(self):
        """Test claim with potentially dangerous characters"""
        result = sanitize_claim("La Tour Eiffel <script>alert('xss')</script>")
        assert result is not None
        assert '<script>' not in result
        assert '</script>' not in result
    
    def test_claim_with_brackets(self):
        """Test claim with brackets"""
        result = sanitize_claim("Test {bracket} and <tag>")
        assert result is not None
        assert '{' not in result
        assert '<' not in result
    
    def test_empty_claim(self):
        """Test with empty claim"""
        assert sanitize_claim("") is None
        assert sanitize_claim("   ") is None
    
    def test_none_claim(self):
        """Test with None input"""
        assert sanitize_claim(None) is None
    
    def test_non_string_input(self):
        """Test with non-string input"""
        assert sanitize_claim(123) is None
        assert sanitize_claim(['list']) is None
    
    def test_claim_at_min_length(self):
        """Test claim at exactly 10 characters"""
        result = sanitize_claim("1234567890")
        assert result == "1234567890"
    
    def test_claim_at_max_length(self):
        """Test claim at exactly 500 characters"""
        claim = "A" * 500
        result = sanitize_claim(claim)
        assert result == claim


class TestValidateUserId:
    """Tests for validate_user_id function"""
    
    def test_valid_user_id(self):
        """Test with valid user ID"""
        assert validate_user_id("user_123") is True
        assert validate_user_id("admin") is True
        assert validate_user_id("test_user_456") is True
    
    def test_user_id_too_short(self):
        """Test user ID shorter than 3 chars"""
        assert validate_user_id("ab") is False
    
    def test_user_id_too_long(self):
        """Test user ID longer than 50 chars"""
        long_id = "a" * 51
        assert validate_user_id(long_id) is False
    
    def test_user_id_with_special_chars(self):
        """Test user ID with special characters"""
        assert validate_user_id("user@123") is False
        assert validate_user_id("user-123") is False
        assert validate_user_id("user.123") is False
    
    def test_empty_user_id(self):
        """Test with empty user ID"""
        assert validate_user_id("") is False
    
    def test_none_user_id(self):
        """Test with None input"""
        assert validate_user_id(None) is False


class TestSanitizeFeedbackComment:
    """Tests for sanitize_feedback_comment function"""
    
    def test_valid_comment(self):
        """Test with valid comment"""
        result = sanitize_feedback_comment("Great analysis!")
        assert result == "Great analysis!"
    
    def test_comment_with_html(self):
        """Test comment with HTML tags"""
        result = sanitize_feedback_comment("Good <b>analysis</b>!")
        assert result is not None
        assert '<b>' not in result
        assert '</b>' not in result
    
    def test_comment_too_long(self):
        """Test comment longer than 1000 chars"""
        long_comment = "A" * 1001
        result = sanitize_feedback_comment(long_comment)
        assert result is not None
        assert len(result) == 1000
    
    def test_empty_comment(self):
        """Test with empty comment"""
        assert sanitize_feedback_comment("") is None
        assert sanitize_feedback_comment("   ") is None
    
    def test_none_comment(self):
        """Test with None input"""
        assert sanitize_feedback_comment(None) is None

