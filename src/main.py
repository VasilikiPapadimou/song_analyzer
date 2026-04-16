from dotenv import load_dotenv
import os
from openai import OpenAI
from datetime import datetime
import json

load_dotenv()

client = OpenAI()

# read file
try:
    file_path = "data/songs/Warrior-Aurora.txt"
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    lyrics_text = "".join(lines)
except FileNotFoundError:
    print(f"❌ File not found: {file_path}")
    exit()
except Exception as e:
    print(f"❌ Error reading file: {e}")
    exit()


# send to LLM
try:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"""
                Analyze the following song lyrics:

                {lyrics_text}

                Return ONLY a valid JSON object with this structure:

                {{
                "song_title": "",
                "artist": "",
                "interpretation_summary": "",
                "dominant_emotions": [],
                "emotional_arc": "",
                "narrator_perspective": "",
                "key_evidence_lines": [],
                "uncertainty_notes": ""
                }}

                Rules:
                - Return ONLY JSON (no explanations, no text before or after)
                - dominant_emotions must be a list of single words
                - key_evidence_lines must be exact quotes from the lyrics
                """
    )
except Exception as e:
    print(f"❌ API call failed: {e}")
    exit()


# print result
'''try:
    output_text = response.output[0].content[0].text
    print(output_text)
except Exception as e:
    print(f"❌ Error reading response: {e}")
    exit()
'''
try:
    output_text = response.output[0].content[0].text

    # convert string to JSON
    parsed_output = json.loads(output_text)

    print("\n--- PARSED JSON ---\n")
    print(json.dumps(parsed_output, indent=2))

except json.JSONDecodeError as err:
    print("❌ Failed to parse JSON")
    print("Raw output was:")
    print(output_text)
    print(f"Error: {err}")
    exit()

except Exception as e:
    print(f"❌ Error processing response: {e}")

# create output path for raw data
input_filename = os.path.basename(file_path)
name_without_ext = os.path.splitext(input_filename)[0]
current_date = datetime.now().strftime("%Y-%m-%d")

output_file_path = f"output/raw/{name_without_ext}_{current_date}_raw.txt"

# save raw output
try:
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    print(f"\n✅ Raw output saved to: {output_file_path}")
except Exception as e:
    print(f"❌ Failed to save raw output: {e}")


# tokens consumed
usage = response.usage

print("\n--- USAGE ---")
print(f"Input tokens: {usage.input_tokens}")
print(f"Output tokens: {usage.output_tokens}")
print(f"Total tokens: {usage.total_tokens}")

input_price = 0.0003 / 1000
output_price = 0.0006 / 1000

cost = (
    usage.input_tokens * input_price +
    usage.output_tokens * output_price
)

print(f"\nEstimated cost: ${cost:.6f}")
