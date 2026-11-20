"""Host: liga um modelo local (Ollama) ao servidor MCP de clientes."""
import asyncio
import os
import sys

import ollama
from mcp import Client, StdioServerParameters

MODELO = os.getenv("MODELO", "qwen2.5:3b")
SISTEMA = ("Você gerencia o cadastro de clientes de uma empresa. "
           "Use as ferramentas disponíveis sempre que precisar. "
           "Responda só com base no que as ferramentas devolverem: nunca invente clientes ou dados. "
           "Responda em português.")


async def main():
    servidor = StdioServerParameters(command=sys.executable, args=["server.py"])

    # ---- A parte MCP: conectar, listar e (mais abaixo) chamar ferramentas ----
    async with Client(servidor) as mcp:
        tools = (await mcp.list_tools()).tools                       # tools/list
        print("Ferramentas do servidor:", [t.name for t in tools])

        # Traduz as ferramentas MCP para o formato que o Ollama entende
        ferramentas = [{"type": "function", "function": {
            "name": t.name, "description": t.description, "parameters": t.input_schema}}
            for t in tools]

        msgs = [{"role": "system", "content": SISTEMA}]
        while True:
            try:
                pergunta = input("\nVocê: ")
            except EOFError:
                break
            if pergunta.strip().lower() in ("sair", "exit"):
                break
            msgs.append({"role": "user", "content": pergunta})

            # ---- O modelo decide se chama alguma ferramenta ----
            while True:
                resp = ollama.chat(model=MODELO, messages=msgs, tools=ferramentas)
                msgs.append(resp.message)
                if not resp.message.tool_calls:
                    print("IA:", resp.message.content)
                    break
                for call in resp.message.tool_calls:
                    nome, args = call.function.name, call.function.arguments
                    print(f"  -> {nome}({args})")
                    resultado = await mcp.call_tool(nome, args)       # tools/call
                    texto = "".join(c.text for c in resultado.content if hasattr(c, "text"))
                    print(f"  <- {texto}")
                    msgs.append({"role": "tool", "content": texto, "tool_name": nome})


asyncio.run(main())
