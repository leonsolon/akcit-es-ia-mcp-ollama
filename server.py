"""Servidor MCP: transforma a API de clientes em ferramentas que uma IA pode usar."""
import logging

import httpx
from mcp.server.mcpserver import MCPServer

logging.getLogger("httpx").setLevel(logging.WARNING)  # deixa o terminal limpo

API = "http://localhost:5001"
mcp = MCPServer("clientes")


# A docstring de cada ferramenta é o que o modelo lê para decidir qual usar.
@mcp.tool()
def listar_clientes() -> dict:
    """Lista todos os clientes cadastrados e informa quantos são."""
    clientes = httpx.get(f"{API}/clientes").json()
    return {"total": len(clientes), "clientes": clientes}


@mcp.tool()
def cadastrar_cliente(nome: str, email: str) -> dict:
    """Cadastra um novo cliente com nome e e-mail."""
    return httpx.post(f"{API}/clientes", json={"nome": nome, "email": email}).json()


@mcp.tool()
def remover_cliente(id: int) -> dict:
    """Remove o cliente com o id informado."""
    return httpx.delete(f"{API}/clientes/{id}").json()


if __name__ == "__main__":
    mcp.run()  # conversa com o cliente pela entrada e saída padrão (stdio)
