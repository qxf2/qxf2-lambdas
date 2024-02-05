"""
Extracts data from work anniversary image
"""
import cv2
import pytesseract

def get_data_from_image(created_file):
    "Extracts data from image"
    extracted_text = get_text_from_image(created_file)
    image_data = split_text(extracted_text)
    #Handle the case of the number '1' not getting predicted properly
    special_words = {
        "1st": ["1st", "lst", "Ist"],
        "11th": [
            "Ilth",
            "IIth",
            "llth",
            "lIth",
            "11th",
            "1Ith",
            "I1th",
            "1lth",
            "l1th",
        ],
        "12th": ["12th", "I2th", "l2th"],
        "13th": ["13th", "l3th", "I3th"],
        "14th": ["14th", "l4th", "I4th"],
    }

    for word in special_words:
        if image_data["anniversary"] in special_words[word]:
            image_data["anniversary"] = word
            break
    return image_data


def get_text_from_image(file):
    "Predicts the text from the image using Tesseract"
    image = cv2.imread(file)

    template = cv2.imread("Work_anniversary_template.png")

    # Subtract the image from template to get just the text
    img = image - template

    # crop text portion in the image
    x_axis = 350
    y_axis = 500
    width = 2800
    height = 800
    img = image[y_axis : y_axis + height, x_axis : x_axis + width]

    # Apply OCR on the cropped image using the trained model
    text = pytesseract.image_to_string(img, lang="eng.workanniv")
    return text

def split_text(text_from_img):
    "Splits the extracted text from image into name, anniversary and quote"
    # For the Name and anniversary number
    first_line = ""
    # For the quote
    rest_of_the_lines = ""

    text_list = text_from_img.split("\n")
    for line in text_list:
        if line.strip() == "":
            continue
        if first_line == "":
            first_line = line.strip()
        else:
            rest_of_the_lines = rest_of_the_lines + " " + line.strip()
    rest_of_the_lines = rest_of_the_lines.strip()

    first_line_list = first_line.split(" ")

    # We need name which starts from 5th word
    if len(first_line_list) > 4:
        # The second word is the anniversary number
        nth_anniversary = first_line_list[1]
        name = ""
        # Extract the name
        i = 4
        while len(first_line_list) > i:
            name = name + " " + first_line_list[i]
            i = i + 1

    if name is None or nth_anniversary is None or rest_of_the_lines == "":
        return None
    image_data = {
        "name": name.strip(),
        "anniversary": nth_anniversary.strip(),
        "quote": rest_of_the_lines.strip(),
    }
    return image_data
