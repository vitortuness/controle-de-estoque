from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()
engine = create_engine("sqlite:///data/estoque.db", echo=False)
Session = sessionmaker(bind=engine)


class Produto(Base):
    __tablename__ = "produtos"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    nome         = Column(String(100), nullable=False)
    categoria    = Column(String(50))
    quantidade   = Column(Integer, default=0)
    preco        = Column(Float, nullable=False)
    qtd_minima   = Column(Integer, default=5)
    criado_em    = Column(DateTime, default=datetime.now)

    movimentacoes = relationship("Movimentacao", back_populates="produto")

    def to_dict(self):
        return {
            "id":         self.id,
            "nome":       self.nome,
            "categoria":  self.categoria,
            "quantidade": self.quantidade,
            "preco":      self.preco,
            "qtd_minima": self.qtd_minima,
            "criado_em":  self.criado_em.isoformat() if self.criado_em else None,
        }


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    produto_id  = Column(Integer, ForeignKey("produtos.id"))
    tipo        = Column(String(10))  # "entrada" ou "saida"
    quantidade  = Column(Integer)
    observacao  = Column(String(200))
    criado_em   = Column(DateTime, default=datetime.now)

    produto = relationship("Produto", back_populates="movimentacoes")

    def to_dict(self):
        return {
            "id":         self.id,
            "produto_id": self.produto_id,
            "produto":    self.produto.nome if self.produto else None,
            "tipo":       self.tipo,
            "quantidade": self.quantidade,
            "observacao": self.observacao,
            "criado_em":  self.criado_em.isoformat() if self.criado_em else None,
        }


def init_db():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(engine)