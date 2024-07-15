import os, sys
# laod environment variables from .env file
import dotenv
dotenv.load_dotenv()

def test_use_api_key(pdf_path, output_dir):
    from gptpdf import parse_pdf
    api_key = ''
    base_url = "https://api.openai.com/v1"
    # Manually provide OPENAI_API_KEY and OPEN_API_BASE
    content, image_paths = parse_pdf(pdf_path, output_dir=output_dir, api_key=api_key, base_url=base_url, model='gpt-4o', gpt_worker=1)
    print(content)
    print(image_paths)
    # also output_dir/output.md is generated

if __name__ == '__main__':
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)
    test_use_api_key(pdf_path, output_dir)