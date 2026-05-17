import json
from database.db_manager import save_label, get_history

def test_db():
    print("Testing database operations...")
    
    image_path = "test_image.jpg"
    content = {"name": "Test Item", "price": "10.00", "description": "Test Description"}
    formatted_text = "Name: Test Item\nPrice: 10.00\nDesc: Test Description"
    
    print(f"Saving label for {image_path}...")
    label_id = save_label(image_path, content, formatted_text)
    print(f"Label saved with ID: {label_id}")
    
    print("Retrieving history...")
    history = get_history()
    print(f"Found {len(history)} labels in history.")
    
    last_label = history[-1]
    assert last_label.id == label_id
    assert last_label.original_image_path == image_path
    assert last_label.dutch_content == content
    assert last_label.formatted_text == formatted_text
    
    print("Verification successful!")

if __name__ == "__main__":
    test_db()
