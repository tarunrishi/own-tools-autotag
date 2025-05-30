from PIL import Image, ImageDraw, ImageFont
import PyPDF2
import os
import re

# Function to read text from .txt files
def read_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to read text from .pdf files
def read_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to gather all text from .txt and .pdf files in the source_text directory
def gather_text_from_files(source_dir):
    all_text = ""
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if filename.endswith('.txt'):
            all_text += read_text_from_txt(file_path) + " "
        elif filename.endswith('.pdf'):
            all_text += read_text_from_pdf(file_path) + " "
    return all_text.strip()

# Function to extract words from the paragraphh
def extract_words(paragraph):
    # Split based on spaces, punctuation, and special characters like "/", "://"
    # Use regex to split on whitespace, punctuation, and the key characters
    split_pattern = r'([\s.,;:!?/])+|"+|://'
    words = re.split(split_pattern, paragraph)
    
    # Remove any empty strings that may have resulted from the splitting
    words = [word for word in words if word]
    
    return words

# Function to generate images for words
def generate_image(word, output_dir, font_path=None):
    # Set image size to 400x400
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color=(255, 255, 255))

    # Initialize ImageDraw
    draw = ImageDraw.Draw(image)

  # Try to load the specified font, fallback to default if unavailable
    try:
        font = ImageFont.truetype(font_path, 100) if font_path else ImageFont.truetype("arial.ttf", 100)
    except IOError:
        print(f"Warning: Could not load font '{font_path}'. Falling back to default font.")
        font = ImageFont.load_default()

    # Calculate text size and position using textbbox
    text_bbox = draw.textbbox((0, 0), word, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((width - text_width) / 2, (height - text_height) / 2)

    try:
        # Draw the text onto the image
        draw.text(position, word, fill="black", font=font)
         # Save image to file
        image_path = os.path.join(output_dir, f"{word}.png")
        image.save(image_path)
    except:
        # do nothing
         print(f"Warning: Could not draw word '{word}'")
         image_path = os.path.join(output_dir, f"{word}.png")
        

    return image_path

# Function to save the associated tags
def save_tags(word_image_map, output_file):
    with open(output_file, 'a') as f:  # Append mode to add new tags
        for word, image_path in word_image_map.items():
            f.write(f"{image_path},{word}\n")

# Function to load existing tags from the tag file
def load_existing_tags(tag_file):
    if not os.path.exists(tag_file):
        return set()
    
    existing_words = set()
    with open(tag_file, 'r') as f:
        for line in f:
            _, word = line.strip().split(',')
            existing_words.add(word)
    return existing_words 

# Main function to automate the process
def automate_process(paragraph, output_dir, tag_file, font_path=None, existing_words=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    words = extract_words(paragraph)
    word_image_map = {}

    for word in words:
        if word not in existing_words:
            image_path = generate_image(word, output_dir, font_path)
            word_image_map[word] = image_path

    save_tags(word_image_map, tag_file)

# function to process files from the source_text directory
def process_source_text_files(source_dir, output_dir, tag_file, font_path=None):
    # Load existing tags to exclude those words
    existing_words = load_existing_tags(tag_file)
    
    # Gather text from the source files
    paragraph = gather_text_from_files(source_dir)
    
    # Process the paragraph and generate images, excluding existing words
    automate_process(paragraph, output_dir, tag_file, font_path, existing_words)

# Example usage
source_dir = "./source_text"
output_dir = "./word_images"
tag_file = "word_tags.csv"
font_path = "Times_New_Roman.ttf"  # Optional: specify the path to your .ttf font

process_source_text_files(source_dir, output_dir, tag_file, font_path)