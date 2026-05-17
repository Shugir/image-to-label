import requests
import json
import base64
from typing import Dict, Any

def encode_image_to_base64(image_path: str) -> str:
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_product_data(image_path: str) -> Dict[str, Any]:
    """
    Extracts product data from an image using Ollama's gemma4:31b-cloud,
    translates fields to Dutch, and performs smart mapping.
    """
    try:
        base64_image = encode_image_to_base64(image_path)
    except Exception as e:
        return {"error": f"Failed to encode image: {str(e)}"}
    
    # Prompt with full nutrition table extraction and 1-shot example
    prompt = (
        "Extract all product label data from this image and return ONLY a JSON object. Translate all values to Dutch.\n"
        "Rules:\n"
        "- Extract the FULL nutrition table: every row (Energy kJ, Energy kcal, Fat, Saturates, Carbohydrates, Sugars, Fibre, Protein, Salt, etc.)\n"
        "- Each nutrition property maps to a list of {\"100g\": \"value\", \"serving\": \"value\"} objects\n"
        "- serving_note = the footnote text about serving size (e.g. '*Per portie van 25g')\n"
        "- If a column (100g or serving) is missing for a row, use an empty string\n"
        "- If a field is not present on the label, omit the key entirely\n"
        "Example:\n"
        "{\n"
        "  \"product_title\": \"Haverkoeken 500g\",\n"
        "  \"nutrition\": {\n"
        "    \"Energie kJ\": [{\"100g\": \"1680 kJ\", \"serving\": \"420 kJ\"}],\n"
        "    \"Energie kcal\": [{\"100g\": \"400 kcal\", \"serving\": \"100 kcal\"}],\n"
        "    \"Vetten\": [{\"100g\": \"12.0 g\", \"serving\": \"3.0 g\"}],\n"
        "    \"waarvan verzadigd\": [{\"100g\": \"2.4 g\", \"serving\": \"0.6 g\"}],\n"
        "    \"Koolhydraten\": [{\"100g\": \"64.0 g\", \"serving\": \"16.0 g\"}],\n"
        "    \"waarvan suikers\": [{\"100g\": \"28.0 g\", \"serving\": \"7.0 g\"}],\n"
        "    \"Vezels\": [{\"100g\": \"4.0 g\", \"serving\": \"1.0 g\"}],\n"
        "    \"Eiwitten\": [{\"100g\": \"7.0 g\", \"serving\": \"1.8 g\"}],\n"
        "    \"Zout\": [{\"100g\": \"0.40 g\", \"serving\": \"0.10 g\"}],\n"
        "    \"serving_note\": \"*Dit pak bevat 4 porties van 25g\"\n"
        "  },\n"
        "  \"ingredients\": \"Haver (40%), Suiker, Plantaardige olie...\",\n"
        "  \"allergy_advice\": \"Bevat GLUTEN en SOJA\",\n"
        "  \"storage\": \"Bewaar op een koele, droge plaats\",\n"
        "  \"footer\": \"Geproduceerd voor: Food Co Ltd\",\n"
        "  \"icons\": [\"Recyclebaar\", \"Vegan\"]\n"
        "}\n"
        "Return ONLY the JSON object, no markdown, no explanation."
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma4:31b-cloud",
                "prompt": prompt,
                "images": [base64_image],
                "stream": False,
                "format": "json"
            },
            timeout=60
        )
        response.raise_for_status()
        
        # Safely extract JSON from the response
        raw_content = response.text
        try:
            # Case 1: Entire response is valid JSON
            resp_json = response.json()
            result_text = resp_json.get("response", "{}")
        except Exception:
            # Case 2: Response is raw text (happens with some Ollama versions)
            result_text = raw_content

        # Final sanitization: Extract first { and last } in case AI added markdown or text
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start == -1 or end == 0:
            return {"error": "AI returned no valid JSON object", "raw": result_text}
        
        return json.loads(result_text[start:end])
    except Exception as e:
        return {"error": str(e)}
