from models.database import Session, Produto, init_db
from models.movimentacao import registrar_entrada, registrar_saida, buscar_historico


class EstoqueController:
    def __init__(self):
        init_db()  # garante que o banco e as tabelas existem

    def listar_produtos(self):
        with Session() as s:
            return [p.to_dict() for p in s.query(Produto).all()]

    def buscar_produto(self, produto_id: int):
        with Session() as s:
            p = s.get(Produto, produto_id)
            return p.to_dict() if p else None

    def adicionar_produto(self, nome, categoria, quantidade, preco, qtd_minima=5):
        with Session() as s:
            p = Produto(
                nome=nome,
                categoria=categoria,
                quantidade=quantidade,
                preco=preco,
                qtd_minima=qtd_minima,
            )
            s.add(p)
            s.commit()
            return p.to_dict()

    def editar_produto(self, produto_id: int, **kwargs):
        with Session() as s:
            p = s.get(Produto, produto_id)
            if not p:
                raise ValueError("Produto não encontrado")
            for campo, valor in kwargs.items():
                if hasattr(p, campo):
                    setattr(p, campo, valor)
            s.commit()
            return p.to_dict()

    def excluir_produto(self, produto_id: int):
        with Session() as s:
            p = s.get(Produto, produto_id)
            if not p:
                raise ValueError("Produto não encontrado")
            s.delete(p)
            s.commit()

    def entrada(self, produto_id: int, quantidade: int, observacao: str = ""):
        return registrar_entrada(produto_id, quantidade, observacao)

    def saida(self, produto_id: int, quantidade: int, observacao: str = ""):
        return registrar_saida(produto_id, quantidade, observacao)

    def historico(self, produto_id: int = None):
        return buscar_historico(produto_id)

    def alertas_estoque_baixo(self):
        with Session() as s:
            produtos = s.query(Produto).filter(
                Produto.quantidade <= Produto.qtd_minima
            ).all()
            return [p.to_dict() for p in produtos]

    def resumo(self):
        produtos     = self.listar_produtos()
        total_itens  = sum(p["quantidade"] for p in produtos)
        valor_total  = sum(p["quantidade"] * p["preco"] for p in produtos)
        alertas      = len(self.alertas_estoque_baixo())
        return {
            "total_produtos": len(produtos),
            "total_itens":    total_itens,
            "valor_total":    round(valor_total, 2),
            "alertas":        alertas,
        }