from models.database import Session, Movimentacao, Produto


def registrar_entrada(produto_id: int, quantidade: int, observacao: str = ""):
    with Session() as s:
        produto = s.get(Produto, produto_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        produto.quantidade += quantidade

        mov = Movimentacao(
            produto_id=produto_id,
            tipo="entrada",
            quantidade=quantidade,
            observacao=observacao,
        )
        s.add(mov)
        s.commit()
        return mov.to_dict()


def registrar_saida(produto_id: int, quantidade: int, observacao: str = ""):
    with Session() as s:
        produto = s.get(Produto, produto_id)
        if not produto:
            raise ValueError("Produto não encontrado")
        if produto.quantidade < quantidade:
            raise ValueError(f"Estoque insuficiente. Disponível: {produto.quantidade}")

        produto.quantidade -= quantidade

        mov = Movimentacao(
            produto_id=produto_id,
            tipo="saida",
            quantidade=quantidade,
            observacao=observacao,
        )
        s.add(mov)
        s.commit()
        return mov.to_dict()


def buscar_historico(produto_id: int = None):
    with Session() as s:
        q = s.query(Movimentacao)
        if produto_id:
            q = q.filter(Movimentacao.produto_id == produto_id)
        return [m.to_dict() for m in q.order_by(Movimentacao.criado_em.desc()).all()]