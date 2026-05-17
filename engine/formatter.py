import json
import re

def generate_label_text(data):
    """
    Transforms AI processor JSON output into a plain-text label layout.
    Width constraint: 55 characters (matching SampleLabelFormat.txt)
    """
    if not data:
        return "No data provided"
        
    WIDTH = 55
    lines = []

    # Product Title
    title = data.get("product_title")
    if title:
        lines.append("=" * WIDTH)
        lines.append(title.center(WIDTH))
        lines.append("-" * WIDTH)
        lines.append("")
    else:
        # Fallback if title is missing to keep structure
        lines.append("=" * WIDTH)
        lines.append("PRODUCT NAME".center(WIDTH))
        lines.append("-" * WIDTH)
        lines.append("")

    # Nutrition Information
    nutrition = data.get("nutrition", {})
    if nutrition and isinstance(nutrition, dict) and any(k != "serving_note" for k in nutrition):
        lines.append("NUTRITION INFORMATION")
        serving_note = nutrition.get("serving_note", "")
        # Extract serving label from serving_note (e.g. "Per portie van 25g" → "Per 25g")
        serving_col = "Per Serving"
        if serving_note:
            m = re.search(r'(\d+\s*(?:g|ml|mg|kcal|kJ))', serving_note, re.IGNORECASE)
            if m:
                serving_col = f"Per {m.group(1)}"
        header = f"{'Typical Values':<22}{'Per 100g':<18}{serving_col:<15}"
        lines.append(header)
        lines.append("-" * WIDTH)
        
        # Values
        for prop, values in nutrition.items():
            if prop == "serving_note":
                continue
            # If values is a list (for multi-line entries like Energy kJ/kcal)
            if isinstance(values, list):
                for entry in values:
                    if not isinstance(entry, dict): continue
                    val_100g = str(entry.get("100g", ""))
                    val_serving = str(entry.get("serving", ""))
                    is_primary = entry.get("is_primary", True)
                    row = f"{prop:<22}{val_100g:<18}{val_serving:<15}" if is_primary else f"{' ':<22}{val_100g:<18}{val_serving:<15}"
                    lines.append(row)
            elif isinstance(values, dict):
                val_100g = str(values.get("100g", ""))
                val_serving = str(values.get("serving", ""))
                lines.append(f"{prop:<22}{val_100g:<18}{val_serving:<15}")
            else:
                # Fallback for malformed nutrition data
                lines.append(f"{prop:<22}{str(values):<18}")
        
        lines.append("-" * WIDTH)
        serving_note = nutrition.get("serving_note", "")
        if serving_note:
            lines.append(f"* {serving_note}")
        lines.append("")

    # Ingredients
    ingredients = data.get("ingredients", "")
    if ingredients and str(ingredients).strip():
        lines.append("-" * WIDTH)
        lines.append("")
        # Simple wrap for ingredients
        words = str(ingredients).split()
        current_line = "INGREDIENTS: "
        for word in words:
            if len(current_line) + len(word) + 1 <= WIDTH:
                current_line += ( " " if current_line != "INGREDIENTS: " else "" ) + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        lines.append("")

    # Allergy Advice
    allergy = data.get("allergy_advice", "")
    if allergy and str(allergy).strip():
        words = str(allergy).split()
        current_line = "ALLERGY ADVICE: "
        for word in words:
            if len(current_line) + len(word) <= WIDTH:
                current_line += word if current_line == "ALLERGY ADVICE: " else " " + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        lines.append("")

    # Storage
    storage = data.get("storage", "")
    if storage and str(storage).strip():
        lines.append("-" * WIDTH)
        lines.append("")
        words = str(storage).split()
        current_line = "STORAGE: "
        for word in words:
            if len(current_line) + len(word) + 1 <= WIDTH:
                current_line += ( " " if current_line != "STORAGE: " else "" ) + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        lines.append("")

    # Footer
    footer = data.get("footer", "")
    if footer and str(footer).strip():
        lines.append("-" * WIDTH)
        lines.append("")
        words = str(footer).split()
        current_line = ""
        for word in words:
            if not current_line:
                current_line = word
            elif len(current_line) + 1 + len(word) <= WIDTH:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        lines.append("")

    # Simple horizontal footer icons
    icons = data.get("icons", [])
    if icons and isinstance(icons, list):
        icon_str = "  ".join([str(i) for i in icons])
        lines.append(icon_str.center(WIDTH))

    return "\n".join(lines)
