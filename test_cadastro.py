import json
import os
import tempfile
import unittest

from cadastro import Cadastro


class TestCadastro(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.arquivo = os.path.join(self.dir.name, "dados.json")
        self.cad = Cadastro(self.arquivo)
        self.cad.incluir({"nome": "Carlos", "email": "carlos@x.com", "cidade": "Joinville", "idade": 40})
        self.cad.incluir({"nome": "ana", "email": "ana@y.com", "cidade": "São Paulo", "idade": 25})
        self.cad.incluir({"nome": "Bruno", "email": "bruno@x.com", "cidade": "Blumenau", "idade": 33})

    def tearDown(self):
        self.dir.cleanup()

    def test_incluir_persiste_em_json(self):
        with open(self.arquivo, encoding="utf-8") as f:
            dados = json.load(f)
        self.assertEqual(len(dados["registros"]), 3)
        self.assertEqual(dados["proximo_id"], 4)

    def test_recarregar_do_arquivo(self):
        outro = Cadastro(self.arquivo)
        self.assertEqual(len(outro.registros), 3)
        self.assertEqual(outro.incluir({"nome": "D", "email": "d", "cidade": "c", "idade": 1})["id"], 4)

    def test_alterar(self):
        self.cad.alterar(2, {"cidade": "Curitiba", "idade": "26"})
        r = Cadastro(self.arquivo).buscar_por_id(2)
        self.assertEqual(r["cidade"], "Curitiba")
        self.assertEqual(r["idade"], 26)
        self.assertEqual(r["nome"], "ana")

    def test_excluir(self):
        self.cad.excluir(1)
        self.assertIsNone(Cadastro(self.arquivo).buscar_por_id(1))
        with self.assertRaises(KeyError):
            self.cad.excluir(1)

    def test_ids_nao_sao_reutilizados(self):
        self.cad.excluir(3)
        self.assertEqual(self.cad.incluir({"nome": "E", "email": "e", "cidade": "c", "idade": 1})["id"], 4)

    def test_validacao(self):
        with self.assertRaises(ValueError):
            self.cad.incluir({"nome": "", "email": "a", "cidade": "b", "idade": 1})
        with self.assertRaises(ValueError):
            self.cad.incluir({"nome": "a", "email": "a", "cidade": "b", "idade": "abc"})

    def test_pesquisa_texto(self):
        self.assertEqual([r["id"] for r in self.cad.pesquisar("x.com", "email")], [1, 3])
        self.assertEqual([r["id"] for r in self.cad.pesquisar("SAO")], [2])  # sem acento/caixa
        self.assertEqual(self.cad.pesquisar("zzz"), [])
        with self.assertRaises(ValueError):
            self.cad.pesquisar("1", "idade")

    def test_ordenacao_por_dois_campos(self):
        self.assertEqual([r["nome"] for r in self.cad.listar_ordenado("nome")], ["ana", "Bruno", "Carlos"])
        self.assertEqual([r["idade"] for r in self.cad.listar_ordenado("idade")], [25, 33, 40])


if __name__ == "__main__":
    unittest.main()
