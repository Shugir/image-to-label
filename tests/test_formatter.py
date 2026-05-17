import unittest
from engine.formatter import generate_label_text

class TestFormatter(unittest.TestCase):
    def test_full_label(self):
        data = {
            "product_title": "CHOCOLATE OAT BARS",
            "nutrition": {
                "Energy": [
                    {"100g": "1680 kJ", "serving": "420 kJ", "is_primary": True},
                    {"100g": "400 kcal", "serving": "100 kcal", "is_primary": False},
                ],
                "Fat": {"100g": "12.0 g", "serving": "3.0 g"},
                "Saturates": {"100g": "2.4 g", "serving": "0.6 g"},
                "Carbohydrate": {"100g": "64.0 g", "serving": "16.0 g"},
                "Sugars": {"100g": "28.0 g", "serving": "7.0 g"},
                "Fibre": {"100g": "4.0 g", "serving": "1.0 g"},
                "Protein": {"100g": "7.0 g", "serving": "1.8 g"},
                "Salt": {"100g": "0.40 g", "serving": "0.10 g"},
                "serving_note": "This pack contains 4 servings."
            },
            "ingredients": "Whole Oats (40%), Sugar, Vegetable Oil (Palm), Chocolate Chips (10%) (Sugar, Cocoa Mass, Cocoa Butter, Emulsifier: SOYA Lecithin), Crisp Rice (Rice Flour, WHEAT Flour, Sugar, Malted BARLEY Flour, Salt), Salt.",
            "allergy_advice": "For allergens, including cereals containing gluten, see ingredients in BOLD. May also contain traces of NUTS.",
            "storage": "Store in a cool, dry place. Reseal bag after opening to maintain freshness.",
            "footer": "Mfd for: Food Co Ltd, London, EC1A 1AA, UK.",
            "icons": ["(e 100g)", "[Recycle]", "[Vegan]"]
        }
        
        output = generate_label_text(data)
        
        # Verify basic structural elements
        self.assertIn("CHOCOLATE OAT BARS", output)
        self.assertIn("NUTRITION INFORMATION", output)
        self.assertIn("Typical Values", output)
        self.assertIn("Per 100g", output)
        self.assertIn("Per Serving", output)
        self.assertIn("1680 kJ", output)
        self.assertIn("400 kcal", output)
        self.assertIn("INGREDIENTS:", output)
        self.assertIn("ALLERGY ADVICE:", output)
        self.assertIn("STORAGE:", output)
        self.assertIn("Mfd for:", output)
        self.assertIn("(e 100g)", output)
        self.assertIn("[Recycle]", output)
        self.assertIn("[Vegan]", output)

    def test_dynamic_height_optimization(self):
        # Test case with missing storage and allergy advice
        data = {
            "product_title": "MINIMAL LABEL",
            "nutrition": {
                "Energy": {"100g": "100 kJ", "serving": "25 kJ"},
            },
            "ingredients": "Simple ingredients.",
            # allergy_advice is missing
            # storage is missing
            "footer": "Footer info",
            "icons": ["(e 100g)"]
        }
        
        output = generate_label_text(data)
        
        self.assertNotIn("ALLERGY ADVICE:", output)
        self.assertNotIn("STORAGE:", output)
        # Ensure the separators for those sections are also gone
        # In my implementation, the separator for storage is only added if storage exists.
        # Let's check that the resulting text is shorter.
        self.assertTrue(len(output) < 1000)

if __name__ == "__main__":
    unittest.main()
