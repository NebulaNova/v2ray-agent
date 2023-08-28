import openai
import regex
from tqdm import tqdm

import diskcache
from diskcache import Cache

cache = Cache("./translation_cache")

with open("openai_api_key.txt", "r") as f:
    openai.api_key = f.readline()


@cache.memoize(expire=30 * 86400, tag="translation")
def translate_string(string: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that translates text. This is a string from a Bash script that needs to be translated to English: ",
            },
            {"role": "user", "content": string},
        ],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    translation = response.choices[0].message.content.strip()
    return translation


def main():
    with open("../install.sh", "r") as f, open("install_en.sh", "w") as f_en:
        lines = f.readlines()
        for line in tqdm(lines):
            line = line.rstrip()
            if line.strip().startswith("echoContent"):
                # Match only Chinese characters
                if regex.search(r"\p{Han}", line):
                    content = regex.match(r"( *echoContent [^ ]*) (.*)", line)
                    initial_part, string = content.groups()
                    line = f"{initial_part} {translate_string(string)}"
            if line.strip().startswith("read"):
                if regex.search(r"\p{Han}", line):
                    content = regex.match(r"( *read) (.*)", line)
                    initial_part, string = content.groups()
                    line = f"{initial_part} {translate_string(string)}"
            f_en.write(line + "\n")


if __name__ == "__main__":
    main()
