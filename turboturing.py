from typing import Optional, Any
import os
from io import StringIO
import contextlib

import inquirer
import rich
import anthropic
from anthropic.types import Message


class PythonExecutor:
    def __init__(self, world: Any):
        self.locals = {}
        self.globals = {'world': world}

    def execute(self, code: str) -> Any:
        try:
            # Capture stdout
            stdout = StringIO()

            with contextlib.redirect_stdout(stdout):
                # Execute the code and capture the result
                result = eval(code, self.globals, self.locals)

            # Get any printed output
            output = stdout.getvalue()
            if output:
                print(output, end='')

            return result

        except Exception as e:
            return f'Failed to execute Python code: {str(e)}'


class AnthropicClient:
    def __init__(self, api_key: str, model: str = 'claude-3-opus-20240229'):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        response: Message = self.client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=4096
        )

        return response.content[0].text  # type: ignore


class World:
    def speak(self, message: str):
        rich.print(f'[bold green]Model says:[/bold green] {message}')


PROMPT = """
You will function in a sandbox world. You can communicate with the world by generating python code. This code will be executed in a sandbox. You will receive the result of the code execution. Please output the code only, no other text.

In the sandbox, you have access to the world object (global object named 'world'). This object is the only way to communicate with the world.

The world object has a few methods:
- speak(message: str): This method will send the message to the human user.

Please say hello to the user using these rules.
"""  # noqa: E501


def main():
    # Example of using AnthropicClient
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set")

    world = World()
    executor = PythonExecutor(world)

    llm = AnthropicClient(api_key=api_key)
    code = llm.chat(prompt=PROMPT)
    rich.print('[red]Code:[/red]')
    rich.print(code)

    if inquirer.confirm('Do you want to execute the code?'):
        result = executor.execute(code)
        rich.print('[green]Result:[/green]')
        rich.print(result)


if __name__ == "__main__":
    main()
