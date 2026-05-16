import pytest
from unittest.mock import patch, MagicMock
from engine.ai_processor import extract_product_data

def test_extract_product_data_success():
    """Test successful data extraction and translation to Dutch."""
    mock_response = '{"product_naam": "Melk", "inhoud": "1 Liter", "categorie": "Vloeistof"}'
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": mock_response}
        
        result = extract_product_data("dummy_path.jpg")
        
        assert result["product_naam"] == "Melk"
        assert result["inhoud"] == "1 Liter"
        assert "categorie" in result

def test_extract_product_data_pruning():
    """Test that empty fields are pruned from the result."""
    # Note: The pruning is actually handled by the LLM prompt, 
    # but the function should return exactly what the LLM provides.
    mock_response = '{"product_naam": "Appels", "gewicht": "2 KG"}' # 'inhoud' is missing/pruned
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": mock_response}
        
        result = extract_product_data("dummy_path.jpg")
        
        assert "product_naam" in result
        assert "gewicht" in result
        assert "inhoud" not in result

def test_extract_product_data_error():
    """Test error handling when the AI service is unavailable."""
    with patch('requests.post', side_effect=Exception("Connection Error")):
        result = extract_product_data("dummy_path.jpg")
        assert "error" in result
        assert "Connection Error" in result["error"]
