import os
import json
from typing import Dict, Any, List
from groq import Groq

# Configure Groq
# Ideally, this should be loaded from environment variables
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

async def rewrite_text_with_culture(text: str, culture: str) -> Dict[str, Any]:
    """
    Rewrites the given text to match the target culture using Groq (Llama 3).
    Returns a dictionary with rewritten text and image prompt.
    """
    if not client:
        return {
            "rewritten_text": "Error: GROQ_API_KEY not found. Please set it in your environment.",
            "image_prompt": "Error: No API Key"
        }

    try:
        prompt = f"""
        You are an expert educator known for making complex topics incredibly easy to understand (like Richard Feynman).
        
        Input Text: "{text}"
        Target Audience Context: "{culture}"
        
        Task:
        1.  **Analyze**: Deeply understand the core educational concept in the Input Text.
        2.  **Simplify & Explain**: Rewrite the text to be crystal clear and easy to grasp.
            -   Focus on **Conceptual Clarity** above all else.
            -   Use simple, direct language.
            -   Use analogies or examples if they help understanding, but only if they are natural.
            -   *Subtly* adapt the tone and examples to be relatable to someone from {culture}, but DO NOT force it. If a "rural" example makes it confusing, don't use it.
            -   The goal is for the student to say "Oh, I get it now!", not "Why is this about farming?".
        3.  **Visualize**: Create a prompt for an image generation model that depicts the *core concept* clearly.
        
        Output JSON format:
        {{
            "rewritten_text": "The clear, simplified explanation...",
            "image_prompt": "A clear, educational line art diagram of [concept]..."
        }}
        
        IMPORTANT: Output ONLY the JSON.
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that outputs strictly JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
            response_format={"type": "json_object"}
        )

        response_content = chat_completion.choices[0].message.content
        
        # Parse JSON response
        try:
            result = json.loads(response_content)
            return result
        except json.JSONDecodeError:
            return {
                "rewritten_text": response_content,
                "image_prompt": "Error parsing JSON response"
            }

    except Exception as e:
        print(f"Error calling Groq: {e}")
        return {
            "rewritten_text": f"Error processing with AI: {str(e)}",
            "image_prompt": "Error"
        }

async def describe_image(image_bytes: bytes) -> str:
    """
    Describes the content of an image using Groq Llama 3.2 Vision.
    """
    if not client:
        return "Error: No API Key"
    
    try:
        # Encode image to base64
        import base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe the educational content of this image in detail. Focus on the scientific or academic concepts shown."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
            temperature=0.5,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error describing image: {e}")
        return ""

async def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribes audio using Groq Whisper.
    """
    if not client:
        return "Error: No API Key"
    
    try:
        # Groq python client expects a file-like object with a name
        from io import BytesIO
        audio_file = BytesIO(audio_bytes)
        audio_file.name = "audio.m4a" # Default to m4a/mp3
        
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="whisper-large-v3-turbo",
            response_format="text"
        )
        return transcription
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

async def generate_audio(text: str, voice: str) -> bytes:
    """
    Generates audio using edge-tts.
    """
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return audio_bytes
    except Exception as e:
        print(f"Error generating audio: {e}")
        return b""

async def generate_quiz(text: str) -> Dict[str, Any]:
    """
    Generates a 3-question quiz based on the text.
    """
    if not client:
        return {"questions": []}

    try:
        prompt = f"""
        Create a 3-question multiple-choice quiz to test understanding of the following concept.
        
        Concept: "{text}"
        
        Task:
        1. Create 3 questions that test *conceptual understanding* (not just memory).
        2. Relate the questions back to the simplified explanation.
        
        Output JSON format:
        {{
            "questions": [
                {{
                    "question": "...",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "..."
                }},
                ...
            ]
        }}
        
        IMPORTANT: Output ONLY the JSON.
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that outputs strictly JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )

        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return {"questions": []}

async def chat_with_persona(message: str, history: List[Dict[str, str]], context: str, culture: str) -> str:
    """
    Chat with a Socratic Persona based on the culture.
    """
    if not client:
        return "Error: No API Key"

    try:
        system_prompt = f"""
        You are a wise and patient mentor from {culture}.
        
        Context of the lesson: "{context}"
        
        Your Persona:
        - You use local idioms and metaphors from {culture} naturally.
        - You are Socratic: You ask guiding questions rather than just giving answers.
        - You are kind and encouraging, like a favorite teacher or elder.
        - If the user asks about the lesson, explain it using examples from {culture}.
        
        Goal: Help the student understand the concept deeply.
        """

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=512,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error in chat: {e}")
        return "I'm having trouble thinking right now. Ask me again?"
