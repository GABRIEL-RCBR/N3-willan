# Cadastro de Clientes (Python + JSON)

Sistema de cadastro em linha de comando, sem dependências externas (Python 3.8+).

## Funcionalidades

| Requisito | Implementação |
|---|---|
| Incluir, alterar, excluir | Opções 1, 2 e 3 do menu (`Cadastro.incluir/alterar/excluir`) |
| Persistência em JSON | Arquivo `clientes.json`, gravado a cada alteração |
| Pesquisa por campos texto | Opção 4 — pesquisa parcial em `nome`, `email`, `cidade` (ou todos), ignorando maiúsculas e acentos |
| Listas ordenadas por 2 campos | Opção 5 — imprime a lista ordenada por **nome** e outra ordenada por **idade** |

Campos do registro: `id` (automático), `nome`, `email`, `cidade` (texto) e `idade` (inteiro).

## Como executar

```bash
python3 cadastro.py
```

## Testes

```bash
pip install -r requirements.txt
python3 -m pytest -v
```

## Formato do arquivo JSON

```json
{
  "proximo_id": 3,
  "registros": [
    {"id": 1, "nome": "Ana", "email": "ana@email.com", "cidade": "São Paulo", "idade": 25},
    {"id": 2, "nome": "Bruno", "email": "bruno@email.com", "cidade": "Blumenau", "idade": 33}
  ]
}
```
