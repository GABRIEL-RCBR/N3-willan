"""Testes unitários do módulo cadastro.py usando pytest.

Executar com:  python -m pytest -v
"""
import json

import pytest

from cadastro import Cadastro, normalizar


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def arquivo(tmp_path):
    """Caminho de um JSON temporário (o pytest apaga a pasta sozinho)."""
    return tmp_path / "dados.json"


@pytest.fixture
def cad(arquivo):
    """Cadastro já populado com 3 clientes."""
    c = Cadastro(str(arquivo))
    c.incluir({"nome": "Carlos", "email": "carlos@x.com", "cidade": "Joinville", "idade": 40})
    c.incluir({"nome": "ana", "email": "ana@y.com", "cidade": "São Paulo", "idade": 25})
    c.incluir({"nome": "Bruno", "email": "bruno@x.com", "cidade": "Blumenau", "idade": 33})
    return c


def novo(nome="D"):
    return {"nome": nome, "email": "d@d.com", "cidade": "c", "idade": 1}


# ---------------------------------------------------------------- normalizar

@pytest.mark.parametrize("entrada, esperado", [
    ("São Paulo", "sao paulo"),
    ("  JOINVILLE ", "joinville"),
    ("Açaí", "acai"),
    ("", ""),
])
def test_normalizar(entrada, esperado):
    assert normalizar(entrada) == esperado


# ---------------------------------------------------------------- carregar

def test_arquivo_inexistente_comeca_vazio(arquivo):
    c = Cadastro(str(arquivo))
    assert c.registros == []
    assert c.proximo_id == 1


def test_arquivo_vazio(arquivo):
    arquivo.write_text("", encoding="utf-8")
    c = Cadastro(str(arquivo))
    assert c.registros == []
    assert c.proximo_id == 1


def test_arquivo_com_lista_simples(arquivo):
    arquivo.write_text(json.dumps([{"id": 7, **novo()}]), encoding="utf-8")
    c = Cadastro(str(arquivo))
    assert len(c.registros) == 1
    assert c.proximo_id == 8


# ---------------------------------------------------------------- incluir

def test_incluir_persiste_em_json(cad, arquivo):
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert len(dados["registros"]) == 3
    assert dados["proximo_id"] == 4


def test_incluir_converte_e_limpa_campos(cad):
    r = cad.incluir({"nome": "  Eva  ", "email": "e@e", "cidade": "X", "idade": "30"})
    assert r["nome"] == "Eva"
    assert r["idade"] == 30


def test_recarregar_do_arquivo(cad, arquivo):
    outro = Cadastro(str(arquivo))
    assert len(outro.registros) == 3
    assert outro.incluir(novo())["id"] == 4


# ---------------------------------------------------------------- validar

@pytest.mark.parametrize("dados, mensagem", [
    ({"nome": "", "email": "a", "cidade": "b", "idade": 1}, "não pode ser vazio"),
    ({"nome": "a", "email": "a", "cidade": "b", "idade": "abc"}, "número inteiro"),
    ({"nome": "a", "email": "a", "cidade": "b", "idade": -1}, "negativo"),
    ({"nome": "a", "email": "a", "cidade": "b"}, "ausente"),
])
def test_validacao_invalida(cad, dados, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        cad.incluir(dados)
    assert len(cad.registros) == 3  # nada foi incluído


def test_validacao_parcial_ignora_campos_ausentes():
    assert Cadastro.validar({"idade": "5"}, parcial=True) == {"idade": 5}


# ---------------------------------------------------------------- alterar

def test_alterar(cad, arquivo):
    cad.alterar(2, {"cidade": "Curitiba", "idade": "26"})
    r = Cadastro(str(arquivo)).buscar_por_id(2)
    assert r["cidade"] == "Curitiba"
    assert r["idade"] == 26
    assert r["nome"] == "ana"  # campo não informado continua igual


def test_alterar_inexistente(cad):
    with pytest.raises(KeyError):
        cad.alterar(99, {"nome": "X"})


# ---------------------------------------------------------------- excluir

def test_excluir(cad, arquivo):
    cad.excluir(1)
    assert Cadastro(str(arquivo)).buscar_por_id(1) is None


def test_excluir_inexistente(cad):
    with pytest.raises(KeyError):
        cad.excluir(99)


def test_ids_nao_sao_reutilizados(cad):
    cad.excluir(3)
    assert cad.incluir(novo())["id"] == 4


# ---------------------------------------------------------------- pesquisar

@pytest.mark.parametrize("termo, campo, ids", [
    ("x.com", "email", [1, 3]),
    ("SAO", None, [2]),        # ignora acento e maiúsculas
    ("bru", "nome", [3]),
    ("zzz", None, []),
])
def test_pesquisar(cad, termo, campo, ids):
    assert [r["id"] for r in cad.pesquisar(termo, campo)] == ids


def test_pesquisar_campo_invalido(cad):
    with pytest.raises(ValueError):
        cad.pesquisar("1", "idade")


# ---------------------------------------------------------------- ordenar

def test_ordenar_por_nome(cad):
    assert [r["nome"] for r in cad.listar_ordenado("nome")] == ["ana", "Bruno", "Carlos"]


def test_ordenar_por_idade(cad):
    assert [r["idade"] for r in cad.listar_ordenado("idade")] == [25, 33, 40]


def test_ordenar_decrescente(cad):
    assert [r["idade"] for r in cad.listar_ordenado("idade", decrescente=True)] == [40, 33, 25]


def test_ordenar_campo_invalido(cad):
    with pytest.raises(ValueError):
        cad.listar_ordenado("telefone")
