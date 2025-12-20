import os

INPUT_PATH = '../assets/rockyou.txt'
OUTPUT_PATH = '../assets/rockyou_top_50k.txt'
LINE_LIMIT = 50000

def create_short_dictionary():
    if not os.path.exists(INPUT_PATH):
        print(f"Error: The file '{INPUT_PATH}' was not found.")
        return

    print(f"Reading from {INPUT_PATH}...")

    try:
        
        with open(INPUT_PATH, 'r', encoding='latin-1') as original_dict:
            with open(OUTPUT_PATH, 'w', encoding='utf-8') as new_dict :
                
                count = 0
                for line in original_dict:
                    new_dict.write(line)
                    count += 1
                    
                    if count >= LINE_LIMIT:
                        break
        
        print(f"Created '{OUTPUT_PATH}' with {count} lines.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_short_dictionary()