import pytesseract
import cv2
import pyautogui
from openai import OpenAI
import json
import time 

# some set up 
with open('tokens.json', 'r') as file:
    tokens = json.load(file)


pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

"""
Captures question from screen and uses OCR to extract text.
"""
def capture_question():
    # takes a screenshot
    screenshot = pyautogui.screenshot()
    screenshot.save("question.png")

    # read image & preprocess
    img = cv2.imread("question.png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    # extract text
    text = pytesseract.image_to_string(processed_img)
    return text

"""
Runs the extracted question through the OpenAI API to get an answer.
"""
def get_answer(question):
    # queries API based on question that was extracted
    client = OpenAI(api_key=tokens['openai_key'])
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Answer the multiple-choice question accurately. Answer with a single letter (A, B, C, D, E, or F."},
                  {"role": "user", "content": question}]
    )
    return response["choices"][0]["message"]["content"] # choices[0] is the first response

"""
Autofills answer in the application.
"""
def select_answer(answer):
    options = ["A", "B", "C", "D", "E", "F"]  # Update based on UI options
    if answer in options:
        index = options.index(answer)
        # Move to the corresponding answer location (adjust x, y based on screen)
        x, y = 500, 300 + (index * 50)
        pyautogui.click(x, y)
        time.sleep(1)
        pyautogui.press('enter')  # Submit answer

def main():
    question = capture_question()
    print("Extracted Question:", question)
    answer = get_answer(question)
    print("Generated Answer:", answer)
    select_answer(answer)

if __name__ == "__main__":
    main()

"""
What is the color of the sky?
A. Blue
B. Red
C. Green"
"""