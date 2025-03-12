import pytesseract
import cv2
import pyautogui
from openai import OpenAI
import json
import time 
import base64

# some set up 
with open('tokens.json', 'r') as file:
    tokens = json.load(file)


"""
Captures question from screen and uses OCR to extract text.
"""
def capture_question():
    # takes a screenshot, aligning middle center
    screen_width, screen_height = pyautogui.size()
    region_width, region_height = 800, 600
    region_x = (screen_width - region_width) // 2
    region_y = 0
    screenshot = pyautogui.screenshot(region=(region_x, region_y, region_width, region_height))
    screenshot.save("question.png")
    # encode the iamge 
    with open("question.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string   

"""
Runs the extracted question through the OpenAI API to get an answer.
"""
def get_answer(question):
    # queries API based on question that was extracted
    client = OpenAI(api_key=tokens['openai_key'])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Answer the multiple-choice question accurately. Answer with a single letter (A, B, C, D, E, or F.))"},
                  {"role": "user", "content": [
                    { "type": "text", "text": "Answer this question accurately with a single letter (A, B, C, D, E, or F.)" },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{question}",
                        },
                },
            ], 
        }],
    )
    return response.choices[0].message.content

"""
Autofills answer in the application.
"""
def select_answer(answer):
    options = ["A", "B", "C", "D", "E", "F"]  # Update based on UI options
    if answer in options:
        index = options.index(answer)
        # Move to the corresponding answer location (adjust x, y based on screen)
        # x, y = 500, 300 + (index * 50)
        x, y = 50, 50
        # move cursor to the location
        pyautogui.moveTo(x, y)
        pyautogui.click(x, y)
        time.sleep(1)
        pyautogui.press('enter')  # Submit answer

def main():
    question = capture_question()
    answer = get_answer(question)
    print("Generated Answer:", answer)
    select_answer(answer)

if __name__ == "__main__":
    main()

"""
In Multi-Version Concurrency Control (MVCC), what happens when a transaction reads a value while another transaction is updating it?

A. The transaction waits until the update is complete.
B. The transaction sees an error and is aborted.
C. The transaction reads an older, consistent version of the data.
D. The transaction locks the row until it finishes reading.
E. The transaction updates the value immediately.
F. The transaction overwrites the value without checking.
"""