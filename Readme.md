🚀 Project Name: CultureCraft
Tagline: "Democratizing Education through Hyper-Local Contextualization."
### 3. System Architecture & Workflows

#### A. The "Cultural Dictionary" Prompt (System Prompt)
*Use this logic in the Backend LLM call:*
"You are an expert educator specializing in cultural localization.
Input: A paragraph from a textbook.
User Context: {Target_Culture} (e.g., 'Farming Community in Punjab, India').
Task:
1. Identify examples/metaphors that are foreign to this culture.
2. Rewrite the paragraph keeping the *scientific concept* identical, but swapping the metaphors for local ones.
3. If the paragraph describes an image, generate a new image prompt for a 'Scientific Line Art Diagram' of the local object."

#### B. The Image Generation Strategy (Free & Fast)
We use **Pollinations.ai** via simple URL construction in the Frontend.
* **Pattern:** `https://image.pollinations.ai/prompt/{ENCODED_PROMPT}?width=800&height=600&nologo=true`
* **Prompt Engineering:** Always append *"educational textbook diagram, black and white, minimalist line art, clear background"* to the user's prompt to ensure it looks academic, not artistic.

### 4. Step-by-Step Implementation Guide for the Agent

* **Scenario:** Physics (Newton's Laws).
* **Original:** "A ice hockey puck sliding on ice."
* **Target:** "Rural India."
* **Result Text:** "A carrom coin sliding on a smooth board."
* **Result Image:** A generated line-drawing of a Carrom Board.

### 5. Technical Constraints & Rules
* **No API Keys for Images:** Strictly use Pollinations.ai URL method.
* **Latency:** If the PDF is too big, only process the *first page* for the hackathon demo to keep it fast.
* **Accessibility:** The web app itself must be screen-reader friendly (ARIA labels).

How to Present This to Win
The Hook: Start with a picture of a kid looking confused at a textbook. Say, "Talent is equally distributed, but opportunity—and context—is not."

The Magic: Don't just show code. Show the "Before and After".

The Future: End by saying, "This isn't just for schools. This is for medical manuals, legal documents, and farming guides. We are rewriting the world's knowledge for the 90%."