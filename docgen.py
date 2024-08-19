import os
import re
import argparse
from openai import OpenAI
from hugchat import hugchat
from hugchat.login import Login

# api_key = os.getenv("DEEPSEEK_API_KEY")

# client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

EMAIL = os.getenv("EMAIL")
PASSWD = os.getenv("PASSWD")

def get_project_info(project_dir):
    info = {
        "project_name": os.path.basename(project_dir),
        "modules": [],
        "functions": [],
        "classes": []
    }

    extensions = {
        ".py": {
            "function": r'def (\w+)\(',
            "class": r'class (\w+)\('
        },
         ".js": {
            "function": r'function (\w+)\(',
            "class": r'class (\w+)\('
        },
        ".java": {
            "function": r'(public|protected|private)?\s*(static)?\s*(\w+)\s+(\w+)\s*\(',
            "class": r'(public|protected|private)?\s*class\s+(\w+)\s*'
        }
    }

    for root, dirs, files in os.walk(project_dir):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in extensions:
                module_name = os.path.splitext(file)[0]
                info["modules"].append(module_name)

                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    info['functions'].extend(re.findall(extensions[ext]["function"], content))
                    info['classes'].extend(re.findall(extensions[ext]["class"], content))

    return info

def generate_markdown(project_info, doc_type):
    markdown = f"# {project_info['project_name']} Technical Documentation\n\n"
    markdown = markdown + "### This documentation details the functions and classes found in the given project directory"

    if doc_type == "API":
        markdown = markdown + "## API Documentation \n\n"
        markdown = markdown + "### Modules \n"
        for module in project_info["modules"]:
            markdown = markdown + f"- {module} \n"
        markdown = markdown + "\n ### Functions \n"
        for func in project_info["functions"]:
            markdown = markdown + f"- {func} \n"
        markdown = markdown + "\n ### Classes \n"
        for clsses in project_info["classes"]:
            markdown = markdown + f"- {clsses} \n"

    return markdown

def enhance_content_with_ai(markdown_content, doc_type):
    # Log in to huggingface and grant authorization to huggingchat
    EMAIL = "haresh.jayant@gmail.com"
    PASSWD = "Nansen123!"
    cookie_path_dir = "./cookies/"
    sign = Login(EMAIL, PASSWD)
    cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

    # Create ChatBot instance
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

    # Ask the AI to enhance the documentation content
    prompt = f"Enhance the following {doc_type} documentation:\n\n{markdown_content}"
    
    # Get response
    response = chatbot.chat(prompt)
    
    # # Collect the response
    # enhanced_content = ''
    # for resp in response_generator:
    #     enhanced_content += resp

    message_str = response.wait_until_done()

    return message_str

def main():
    parser = argparse.ArgumentParser(description="Generate Markdown Documentation for a Project")
    parser.add_argument("project_dir", help="Path to the project directory")
    parser.add_argument("doc_type", choices=["API"])
    parser.add_argument("--enhance", action="store_true")
    args = parser.parse_args()

    project_info = get_project_info(args.project_dir)
    markdown = generate_markdown(project_info, args.doc_type)

    if args.enhance:
        markdown = enhance_content_with_ai(markdown, args.doc_type)

    output_file = os.path.join(args.project_dir, f"{args.doc_type.replace(' ', '_').lower()}_documentation.md")
    with open(output_file, "w") as f:
        f.write(markdown)

    print(f"Documentation generated and saved to {output_file}")

if __name__ == "__main__":
    main()

