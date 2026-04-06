import os
import json
from app import ChapterParser, UniversalMapper

def test_extraction():
    # Target a real Class 5 Math PDF
    # C:\Users\AVROJIT\OneDrive\Desktop\EDUGALAXY\Syllabus\class5\Maths\chapter  (2).pdf
    subject = 'math'
    chapter_name = 'Operations on Large numbers'
    chapter_idx = 1
    class_num = '5'
    board = 'CBSE'
    
    print(f"--- Searching for {subject} Ch {chapter_idx+1} ({class_num}) ---")
    path = UniversalMapper.get_asset_path(subject, chapter_name, chapter_idx, board, class_num)
    
    if not path:
        print("❌ Path not found!")
        return

    print(f"✅ Found asset: {path}")
    
    print("--- Parsing Content ---")
    data = ChapterParser.parse_txt(path)
    
    if not data:
        print("❌ Parsing failed or returned no text!")
        return
        
    print(f"✅ Extracted {len(data['terms'])} terms")
    print(f"✅ Extracted {len(data['facts'])} facts")
    print(f"✅ Extracted {len(data['tf'])} TF questions")
    print(f"✅ Extracted {len(data['fill'])} Fill questions")
    
    print("\n--- Sample Facts ---")
    for f in data['facts'][:5]:
        print(f"  - {f}")
        
    print("\n--- Sample Terms ---")
    print(f"  {', '.join(data['terms'][:10])}")

if __name__ == "__main__":
    test_extraction()
