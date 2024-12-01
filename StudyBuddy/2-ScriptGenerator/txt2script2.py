import openai
import sys
import os
import tiktoken
import re
from dotenv import load_dotenv

# Load the OpenAI API key from environment variables
load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
print(f"OpenAI API Key: {'Loaded' if openai_api_key else 'Not Loaded'}")


# Function to estimate tokens accurately using tiktoken
def estimate_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Function to read bullet points from a file
def read_bullet_points(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file '{file_path}': {e}")
        sys.exit(1)

# Function to split text into chunks based on <page number="n"> tags
def split_text_by_page_tags(text, max_chunk_tokens, model="gpt-4"):
    # Regular expression to match content between <page number="n"> and </page>
    page_pattern = re.compile(r'<page\s+number="(\d+)">(.*?)</page>', re.DOTALL)

    # Find all matches
    pages = page_pattern.findall(text)

    chunks = []
    encoding = tiktoken.encoding_for_model(model)

    for i, (page_number, page_content) in enumerate(pages):
        page_content = page_content.strip()
        token_count = len(encoding.encode(page_content))
        if token_count <= max_chunk_tokens:
            chunks.append((page_number, page_content))
        else:
            # If page content is too long, split it into smaller parts
            print(f"Warning: Content in page {page_number} exceeds max token limit. Splitting into smaller parts.")
            subchunks = split_large_text(page_content, max_chunk_tokens, encoding)
            # Label subchunks with page number and subchunk index
            for idx, subchunk in enumerate(subchunks):
                chunks.append((f"{page_number}.{idx+1}", subchunk))

    return chunks

# Function to split large text into smaller chunks based on paragraphs
def split_large_text(text, max_chunk_tokens, encoding):
    paragraphs = text.split('\n\n')
    subchunks = []
    current_chunk = ""
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para_tokens = len(encoding.encode(para))
        if current_tokens + para_tokens <= max_chunk_tokens:
            current_chunk += para + '\n\n'
            current_tokens += para_tokens
        else:
            if current_chunk:
                subchunks.append(current_chunk.strip())
            # Start new chunk
            current_chunk = para + '\n\n'
            current_tokens = para_tokens

    if current_chunk:
        subchunks.append(current_chunk.strip())

    return subchunks

# Function to generate the podcast script for each chunk
def generate_script(bullet_points_chunk, model_name):
    system_prompt = "You are a professional podcast scriptwriter."
    user_prompt = f"""Convert the following bullet points into a cohesive, engaging podcast script suitable for a general audience. Write in a conversational tone, as if speaking directly to the listener. Include an intriguing introduction, smooth transitions between topics, and a strong conclusion. Use relatable examples or anecdotes to illustrate key points, and simplify complex medical terminology. Avoid using section labels like '[Topic 1]' or '[Conclusion]'; instead, ensure the script flows naturally.

Bullet Points:
{bullet_points_chunk}
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Calculate total tokens for messages
    total_message_tokens = sum([estimate_tokens(m['content'], model=model_name) for m in messages])

    # Define the maximum context length for the model
    if "gpt-3.5-turbo" in model_name:
        max_context_length = 4096
    else:
        max_context_length = 8192  # For GPT-4

    # Set desired response tokens and a buffer
    desired_response_tokens = 1500  # Adjust based on desired output length
    buffer_tokens = 100  # Safety buffer

    # Calculate available tokens for the assistant's response
    max_response_tokens = max_context_length - total_message_tokens - buffer_tokens

    # Ensure max_response_tokens is positive
    if max_response_tokens <= 0:
        print("Error: The input chunk is too large to process. Consider reducing the chunk size.")
        sys.exit(1)

    try:
        response = openai.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=min(desired_response_tokens, max_response_tokens),
            temperature=0.7,
            n=1,
            stop=None
        )
        # Return the generated content
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        print(f"An error occurred during the OpenAI API call: {e}")
        sys.exit(1)

# Main execution
if __name__ == "__main__":
    # Check if the input file was provided as a command-line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Prompt the user to enter the input file name
        input_file = input("Enter the path to the input text file containing bullet points: ")

    # Read bullet points from the specified file
    bullet_points = read_bullet_points(input_file)

    # Set the model name
    model_name = "gpt-4"  # Change to "gpt-3.5-turbo" if GPT-4 is not available

    # Define the maximum context length for the model
    if "gpt-3.5-turbo" in model_name:
        max_context_length = 4096
    else:
        max_context_length = 8192  # For GPT-4

    # Prepare the prompts
    system_prompt = "You are a professional podcast scriptwriter."
    system_prompt_tokens = estimate_tokens(system_prompt, model=model_name)

    # Calculate maximum tokens for each chunk
    buffer_tokens = 100  # Safety buffer
    desired_response_tokens = 1500  # Adjust based on desired output length
    per_message_tokens = 50  # Approximate tokens for prompts

    max_chunk_tokens = max_context_length - system_prompt_tokens - desired_response_tokens - buffer_tokens - per_message_tokens

    # Split the bullet points into chunks based on <page number="n"> tags
    print('Splitting bullet points into sections based on <page number="n"> tags...')
    bullet_point_chunks = split_text_by_page_tags(bullet_points, max_chunk_tokens, model=model_name)

    # Generate the podcast script for each chunk and combine
    full_script = ""
    for i, (page_number, chunk) in enumerate(bullet_point_chunks):
        print(f"Processing page {page_number} ({i + 1} of {len(bullet_point_chunks)})...")
        script = generate_script(chunk, model_name)
        full_script += f"Page {page_number}:\n{script}\n\n"

    # Define the output file name based on the input file name
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"{base_name}_script.txt"

    # Save the generated script to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(full_script)
        print(f"Podcast script has been generated and saved to '{output_file}'.")
    except Exception as e:
        print(f"An error occurred while writing to the file '{output_file}': {e}")
        sys.exit(1)
