import pyautogui
from openai import OpenAI
import json
import time 
import base64
import mss 
from PIL import Image
import imagehash
from playsound import playsound

# some set up 
with open('tokens.json', 'r') as file:
    tokens = json.load(file)


#############################
# 1. SCREENSHOT & HASHING   #
#############################
def capture_question(filename="question.png"):
    """
    Captures question from screen. Right now hard coded to capture left half of screen.
    """
    # takes a screenshot, aligning middle center
    screen_width, screen_height = pyautogui.size()
    region = {
        "left": 0,
        "top": 0,
        "width": screen_width // 2,  # left half. HARDCODED
        "height": screen_height
    }
    with mss.mss() as sct:
        sct_img = sct.grab(region)
    mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

def compute_hash(img_path):
    """Returns a perceptual hash (pHash) for the given image."""
    with Image.open(img_path) as img:
        return imagehash.phash(img)

def read_image_as_base64(img_path):
    """Reads an image file and returns base64-encoded string."""
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


#############################
# 2. OPENAI (CHATGPT) CALL  #
#############################
def get_answer(question):
    """
    Runs the extracted question through the OpenAI API to get an answer.
    """
    # queries API based on question that was extracted
    client = OpenAI(api_key=tokens['openai_key'])
    system_prompt = (
        "You are an image analysis assistant. You are provided with a screenshot (in base64 format) of a multiple-choice question screen. "
        "The answer options are displayed on the screen with labels such as A, B, C, etc. "
        "Analyze the screenshot to determine which answer is correct."
        "Return your answer as a singular letter. "
    )

    user_prompt = [
        { "type": "text", "text": "Answer this question accurately with a single letter (A, B, C, D, E, or F.)" },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{question}",
            },
        },
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt, 
        }],
    )
    result_text = response.choices[0].message.content.strip().upper()
    return result_text

#############################
# 3. CLICK THE ANSWER       #
#############################
def select_answer(answer):
    """
    Dynamically finds bounding boxes for letters A-F in the bottom portion
    of the left half, then clicks the center of the matching letter.
    """
    # HARDCODED 
    answer_positions = {
        "A": (236, 949),
        "B": (350, 949),
        "C": (466, 949)
    }
    # if the letter was found by OCR, click it
    if answer in answer_positions:
        x, y = answer_positions[answer]
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
        time.sleep(1)
        print(f"Clicked on answer {answer} at position ({x}, {y})")
    else:
        print(f"Answer '{answer}' not recognized by OCR or not present on screen. Defaulting to answer C.")
        x, y = answer_positions["C"]
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
        time.sleep(1)
        print(f"Clicked on answer C at position ({x}, {y})")

#############################
# 4. PLAY SOUND             #
#############################
def play_sound():
    """
    Plays a short beep or sound file when the screen changes.
    """
    playsound("chime.mp3")

def main():
    # looping to check for new questions and wajts 20 seconds between checks
    previous_hash = None
    try:
        while True:
            # Capture the left half of the screen
            capture_question("question.png")

            # Compute current hash
            current_hash = compute_hash("question.png")

            # Compare with previous hash to detect a new question or change
            if previous_hash is None or current_hash != previous_hash:
                print("Screen changed. Processing new question...")

                # Play a sound to indicate a new question
                play_sound()

                # Read the image as base64
                encoded_img = read_image_as_base64("question.png")

                # Get answer from ChatGPT
                answer = get_answer(encoded_img)
                if answer:
                    print("ChatGPT returned:", answer)
                    # Use the provided coordinates to click the answer
                    select_answer(answer)
                else:
                    print("No valid response from ChatGPT.")

                # Update the previous hash
                previous_hash = current_hash
            else:
                print("No change detected. Skipping ChatGPT call.")

            # Wait 20 seconds before repeating
            time.sleep(20)
    except KeyboardInterrupt:
        # gracefully exit on keyboard interrupt
        print("Program interrupted by user. Exiting...")

if __name__ == "__main__":
    main()

# sample question, should answer "C"

"""
In Multi-Version Concurrency Control (MVCC), what happens when a transaction reads a value while another transaction is updating it?

A. The transaction waits until the update is complete.
B. The transaction sees an error and is aborted.
C. The transaction reads an older, consistent version of the data.
D. The transaction locks the row until it finishes reading.
E. The transaction updates the value immediately.
F. The transaction overwrites the value without checking.
"""