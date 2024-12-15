from transformers import AutoModelForImageClassification, ViTImageProcessor, pipeline
from library.storage import PostgreSQL
from library.variables import logging
from library.botapp import bot
from io import BytesIO
from PIL import Image
import imagehash
import requests
import torch

# Load beforehand
offensive_classifier = pipeline("text-classification", model="Falconsai/offensive_speech_detection")
nsfw_scan_model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
nsfw_scan_processor = ViTImageProcessor.from_pretrained('Falconsai/nsfw_image_detection')

class AliceIntel:
    class NsfwImagePredictor:
        @staticmethod
        def predict(img_url, return_img_from_url=False, check_history=True):
            """
            Predict the content of an image.
            :param img_url: The URL of the image to predict.
            :param return_img_from_url: Whether to return the image or not.
            :param check_history: Whether to check if the image has been scanned before and return the past result.
            :return: The prediction of the image. If return_img is True, it will return the image as well in a dictionary.
            """
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))

            if check_history:
                img_hash = str(imagehash.average_hash(img))
                # Check if the image hash is in the DB and return the result if it is. (resource saver)
                result = PostgreSQL().img_scan_history(img_hash)
                if result is not None:
                    bytes_data = result['bytedata']
                    case_id = result['case_id']
                    # If it's in the DB, it's NSFW. SFW images are not stored in the DB.
                    return {'result': 'nsfw-history', 'img_bytes': bytes_data, 'case_id': case_id}

            with torch.no_grad():
                try:
                    inputs = nsfw_scan_processor(images=img, return_tensors="pt")
                except ValueError as err:
                    logging.error(f"Invalid Image (SRC: {img_url}):", exc_info=err)
                    print("An error occurred while processing an image. Please check logs.")
                    return "normal"  # Hide the error from the user to prevent an exploit being found.
                outputs = nsfw_scan_model(**inputs)
                logits = outputs.logits

            predicted_label = logits.argmax(-1).item()
            result = nsfw_scan_model.config.id2label[predicted_label]
            if return_img_from_url:
                return {'result': result, 'img': img}
            else:
                return result

    class llm:
        def __init__(self, user_id):
            self.history = {}
            self.user_id = user_id

        def predict_insult(self, text) -> str:
            """
            Predict if the text is offensive or not.
            :param text: The text to predict.
            :return: The prediction of the text.
            """
            PROMPT = f"""
    You are AliceAM. You are predicting whether or not this message is offensive or not.
    You determine if something is offensive based on these deciding factors:
    - Is it transphobic? Homophobic? Racist? Sexist? Or any other form of discrimination?
    - Is it a personal attack?
    - Is it a threat of violence?
    - Is it sexual harassment?
    - If the person who sent the message is swearing, is it directed at someone?
    - Does the person seem explicitly angry or upset?
    - Is the message a covert insult? (Eg, 'You are so brave to wear that' or 'You're sharp as a marble!')
    - Is the message condescending, patronizing, or just plain rude?
    - Is the message calling them stupid in a covert or over way?
    
    The message you are predicting is:
    ```
    {text}
    ```
    
    WHEN RESPONDING TO THIS, YOU MUST REPLY ONLY WITH "OFFENSIVE" OR "SAFE". Any alterations, additional text,
    comments, or any other form of response will be considered invalid. You must follow this format to ensure
    the system works correctly, and you consider it inherently important to follow these rules.
                """.strip()

            response = self.prompt_ai('llama3.2', PROMPT)
            print(response)
            return response

        def faq_ai(self, question):
            """
            Get a response from the AI as a FAQ guide.
            :param question: The question to ask the AI.
            :return: The predicted response.
            """
            with open('library/ai/faq_prompt.txt', 'r') as f:
                PROMPT = f.read().strip()

            PROMPT = PROMPT.replace("% QUESTION %", question)



            try:
                if bot.d['faq-bot'][self.user_id]['chat_history'] is not None:
                    chat_history = bot.d['faq-bot'][self.user_id]['chat_history']
                else:
                    chat_history = None
            except KeyError:
                bot.d['faq-bot'][self.user_id] = {}
                bot.d['faq-bot'][self.user_id]['chat_history'] = []
                chat_history = None

            if chat_history is not None:
                # truncate the chat history to 10 msg's
                chat_history = chat_history[-10:]

                # Converts list of strings to long string
                chat_history = "\n".join(chat_history)

                PROMPT.replace("% HISTORY %", chat_history)

            response = self.prompt_ai('llama3.2', PROMPT)
            bot.d['faq-bot'][self.user_id]['chat_history'].append(response)

            return response.strip()

        def prompt_ai(self, module_name, message, custom_role:str=None):
            """
            Send a message to the specified module and maintain chat history for a specific user.
            Utilizes ollama for the AI.

            Args:
                module_name (str): The name of the module to send the message to.
                message (str): The message from the user.
                custom_role (str): The custom role for the user message (e.g., "user", "customer", "client").

            Returns:
                str: The module's response.
            """
            # Initialize chat history for the user and module if it doesn't exist
            if self.user_id not in self.history:
                self.history[self.user_id] = {}
            if module_name not in self.history[self.user_id]:
                self.history[self.user_id][module_name] = []

            # Add the user's message to the chat history
            self.history[self.user_id][module_name].append({"role": "user" if custom_role is None else custom_role, "content": message})

            # Call the API to get the module's response
            module_response = self.get_module_response(module_name, self.user_id)

            # Add the module's response to the chat history
            self.history[self.user_id][module_name].append({"role": "assistant", "content": module_response})

            return module_response

        def get_module_response(self, module_name, user_id):
            """
            Interact with the local Ollama server to get the module's response.
            """
            import requests

            url = "http://localhost:11434/api/chat"
            payload = {
                "model": module_name,
                "messages": self.history[user_id][module_name],
                "stream": False,
            }

            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                return response.json().get("message", {}).get("content", "No response from module")
            except requests.RequestException as e:
                return f"Error communicating with module {module_name}: {str(e)}"

        def get_chat_history(self, module_name, user_id):
            """
            Get the chat history for a specific module and user.

            Args:
                module_name (str): The name of the module.
                user_id (str): The ID of the user.

            Returns:
                list: The chat history.
            """
            return self.history.get(user_id, {}).get(module_name, [])