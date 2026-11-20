# MCP na prática: um modelo local cadastrando clientes

Um modelo de IA rodando no seu computador (Ollama) cadastra, lista e remove clientes de uma API Flask, usando MCP.

```
Você ⇄ cliente.py (host) ⇄ Ollama (modelo local)
            ⇅  MCP (stdio)
       server.py (servidor MCP) ⇄ HTTP ⇄ api.py (API Flask)
```

| Arquivo | O que é |
|---|---|
| `api.py` | API de cadastro de clientes. Um sistema comum, sem IA. |
| `server.py` | Servidor MCP: transforma a API em 3 ferramentas (listar, cadastrar, remover). |
| `cliente.py` | Host: conecta no servidor MCP, entrega as ferramentas ao modelo e executa o que ele pedir. |

## 1. Instalação (faça antes da aula)

Você precisa de **Python 3.10 ou mais novo** e uns 2 GB livres. Roda bem com 8 GB de RAM.

**Ollama**
- Mac: `brew install ollama` (ou baixe o app em https://ollama.com)
- Windows e Linux: baixe em https://ollama.com

Se instalou pelo Homebrew, deixe o Ollama rodando num terminal:

```bash
ollama serve
```

Baixe o modelo (cerca de 2 GB):

```bash
ollama pull qwen2.5:3b
```

**Bibliotecas Python**, dentro desta pasta. Primeiro, confira a versão:

```bash
python3 --version
```

Se aparecer 3.9 ou menos (é o caso do Python que vem no Mac), instale um mais novo pelo site https://www.python.org ou com `brew install python@3.13`, e use `python3.13` no lugar de `python3` no comando abaixo.

```bash
python3 -m venv .venv
```
```bash
source .venv/bin/activate
```
(No Windows: `.venv\Scripts\activate`)
```bash
pip install -r requirements.txt
```

**Importante:** ative o ambiente (`source .venv/bin/activate`) em **cada terminal** que você abrir. É ele que faz o comando `python` existir e encontrar as bibliotecas.

## 2. Rodando

**Terminal 1: a API**

```bash
python api.py
```

**Terminal 2: teste a API sem IA**

```bash
curl -X POST http://localhost:5001/clientes -H "Content-Type: application/json" -d '{"nome": "Ana", "email": "ana@email.com"}'
```
```bash
curl http://localhost:5001/clientes
```

**Terminal 2: o modelo usando o MCP**

```bash
python cliente.py
```

O `cliente.py` já sobe o `server.py` sozinho. Peça, por exemplo:

- `cadastra o João, joao@email.com`
- `quais clientes existem?`
- `remove o cliente 1`
- `sair` para encerrar

As linhas `->` mostram a ferramenta que o modelo escolheu e os argumentos; as linhas `<-` mostram o que o servidor devolveu:

```
Você: cadastra o João, joao@email.com
  -> cadastrar_cliente({'nome': 'João', 'email': 'joao@email.com'})
  <- {"email": "joao@email.com", "id": 2, "nome": "João"}
IA: O cliente João foi cadastrado com sucesso. Seu ID é 2.
```

Depois, confira com `curl http://localhost:5001/clientes` que o cadastro está mesmo na API.

## 3. O que observar

- **A parte MCP do cliente é pequena:** `Client(...)`, `list_tools()` (`tools/list`) e `call_tool()` (`tools/call`). O resto do `cliente.py` é o loop com o modelo.
- **Quem escolhe a ferramenta é o modelo**, lendo a docstring de cada função do `server.py`. Descrição ruim gera escolha ruim.
- **Quem executa é o servidor**, não o modelo. O modelo só pede.
- **O mesmo `server.py` funciona em outros apps** compatíveis com MCP (LM Studio, Claude Desktop, Cursor…), sem mudar nada.
- **Cuidado:** aqui o modelo remove clientes sem pedir confirmação. Num sistema real, ações que alteram dados devem passar por aprovação humana.
- Os dados ficam só na memória: reiniciou o `api.py`, a lista zera.

Para usar outro modelo (precisa suportar *tool calling*), por exemplo um maior e mais preciso (Mac e Linux; no Windows, defina a variável `MODELO` antes):

```bash
MODELO=qwen2.5:7b python cliente.py
```

## 4. Problemas comuns

| Erro | Solução |
|---|---|
| `No module named 'mcp.server.fastmcp'` | Você está seguindo um tutorial do SDK 1.x. Aqui usamos o `mcp` 2.x, em que `FastMCP` virou `MCPServer`. Use o `requirements.txt`. |
| `'Tool' object has no attribute 'inputSchema'` | Mesma causa: no SDK 2.x o campo é `input_schema`. |
| Erro ao instalar o `mcp` | Python antigo. Precisa ser 3.10+ (`python3 --version`). |
| `command not found: python` | O ambiente virtual não está ativado neste terminal: `source .venv/bin/activate`. |
| `No module named 'ollama'` (ou `flask`, `mcp`) | Mesma causa: ative o `.venv` antes de rodar. |
| O modelo inventa clientes que não existem | Modelos pequenos às vezes “completam” a resposta. O prompt do `cliente.py` já pede para não inventar; se continuar, use `qwen2.5:7b`. |
| `Connection refused` na porta 11434 | O Ollama não está rodando. Rode `ollama serve` ou abra o app. |
| `Connection refused` na porta 5001 | O `api.py` não está rodando no terminal 1. |
| `Address already in use` | Algum outro programa usa a porta 5001. Troque a porta no `api.py` e no `server.py`. |
| O modelo responde sem usar ferramenta | Reformule o pedido de forma direta ou use um modelo maior (`qwen2.5:7b`). |
| `curl` com aspas no Windows | No PowerShell, use `curl.exe` e escape as aspas: `-d "{\"nome\": \"Ana\", \"email\": \"ana@email.com\"}"` |

**Plano B**, se o modelo se enrolar na hora da aula: mostre o servidor funcionando sem IA no MCP Inspector (exige Node.js; este comando não foi testado na máquina de referência):

```bash
npx @modelcontextprotocol/inspector python server.py
```

---
Testado em 19/11/2026: macOS 26 (M2, 8 GB), Python 3.13, Ollama 0.40.16, `qwen2.5:3b`, `mcp` 2.3.0. Três pedidos seguidos (cadastrar, listar, remover) levaram cerca de 18 segundos.
