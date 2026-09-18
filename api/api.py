from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from controllers.estoque import EstoqueController

app = FastAPI(title="API de Estoque", version="1.0")
ctrl = EstoqueController()


class ProdutoCreate(BaseModel):
    nome:       str
    categoria:  str
    quantidade: int
    preco:      float
    qtd_minima: int = 5

class ProdutoUpdate(BaseModel):
    nome:       Optional[str]   = None
    categoria:  Optional[str]   = None
    preco:      Optional[float] = None
    qtd_minima: Optional[int]   = None

class Movimentar(BaseModel):
    quantidade: int
    observacao: str = ""


@app.get("/")
def root():
    return {"status": "online", "msg": "API de Estoque funcionando!"}


@app.get("/resumo")
def resumo():
    return ctrl.resumo()

@app.get("/produtos")
def listar():
    return ctrl.listar_produtos()

@app.get("/produtos/{produto_id}")
def buscar(produto_id: int):
    p = ctrl.buscar_produto(produto_id)
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return p

@app.post("/produtos", status_code=201)
def criar(produto: ProdutoCreate):
    return ctrl.adicionar_produto(**produto.dict())

@app.put("/produtos/{produto_id}")
def editar(produto_id: int, dados: ProdutoUpdate):
    try:
        campos = {k: v for k, v in dados.dict().items() if v is not None}
        return ctrl.editar_produto(produto_id, **campos)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/produtos/{produto_id}")
def excluir(produto_id: int):
    try:
        ctrl.excluir_produto(produto_id)
        return {"msg": "Produto excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/produtos/{produto_id}/entrada")
def entrada(produto_id: int, dados: Movimentar):
    try:
        return ctrl.entrada(produto_id, dados.quantidade, dados.observacao)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/produtos/{produto_id}/saida")
def saida(produto_id: int, dados: Movimentar):
    try:
        return ctrl.saida(produto_id, dados.quantidade, dados.observacao)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/historico")
def historico(produto_id: Optional[int] = None):
    return ctrl.historico(produto_id)


@app.get("/alertas")
def alertas():
    return ctrl.alertas_estoque_baixo()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)