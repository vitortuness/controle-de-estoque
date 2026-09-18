import PySimpleGUI as sg
import requests
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

API = "http://localhost:8000"

sg.theme("DarkBlue14")
FONT_TITULO = ("Helvetica", 16, "bold")
FONT_NORMAL = ("Helvetica", 11)
VERDE       = "#2ECC71"
VERMELHO    = "#E74C3C"
AMARELO     = "#F1C40F"
AZUL        = "#3498DB"

def get(endpoint):
    try:
        r = requests.get(f"{API}{endpoint}", timeout=5)
        return r.json()
    except Exception as e:
        sg.popup_error(f"Erro ao conectar na API:\n{e}\n\nRode: python -m uvicorn api.api:app --reload")
        return None

def post(endpoint, dados):
    try:
        r = requests.post(f"{API}{endpoint}", json=dados, timeout=5)
        if r.status_code in (200, 201):
            return r.json()
        sg.popup_error(f"Erro: {r.json().get('detail', r.text)}")
    except Exception as e:
        sg.popup_error(f"Erro: {e}")
    return None

def put(endpoint, dados):
    try:
        r = requests.put(f"{API}{endpoint}", json=dados, timeout=5)
        if r.status_code == 200:
            return r.json()
        sg.popup_error(f"Erro: {r.json().get('detail', r.text)}")
    except Exception as e:
        sg.popup_error(f"Erro: {e}")
    return None

def delete(endpoint):
    try:
        r = requests.delete(f"{API}{endpoint}", timeout=5)
        return r.status_code == 200
    except Exception as e:
        sg.popup_error(f"Erro: {e}")
    return False

def janela_adicionar_produto():
    layout = [
        [sg.Text("Novo Produto", font=FONT_TITULO)],
        [sg.HSeparator()],
        [sg.Text("Nome:",        size=14), sg.Input(key="-NOME-",   size=30)],
        [sg.Text("Categoria:",   size=14), sg.Input(key="-CAT-",    size=30)],
        [sg.Text("Quantidade:",  size=14), sg.Input(key="-QTD-",    size=10)],
        [sg.Text("Preço R$:",    size=14), sg.Input(key="-PRECO-",  size=10)],
        [sg.Text("Qtd. Mínima:", size=14), sg.Input(key="-MIN-",    size=10, default_text="5")],
        [sg.HSeparator()],
        [sg.Button("💾 Salvar",    button_color=(VERDE, "white")),
         sg.Button("❌ Cancelar")],
    ]
    win = sg.Window("Adicionar Produto", layout, modal=True, font=FONT_NORMAL)
    while True:
        e, v = win.read()
        if e in (sg.WIN_CLOSED, "❌ Cancelar"):
            break
        if e == "💾 Salvar":
            try:
                dados = {
                    "nome":       v["-NOME-"],
                    "categoria":  v["-CAT-"],
                    "quantidade": int(v["-QTD-"]),
                    "preco":      float(v["-PRECO-"]),
                    "qtd_minima": int(v["-MIN-"]),
                }
                if not dados["nome"]:
                    raise ValueError("Nome obrigatório")
                if post("/produtos", dados):
                    sg.popup("✅ Produto cadastrado!", title="Sucesso")
                    break
            except ValueError as e:
                sg.popup_error(f"Preencha os campos corretamente.\n{e}")
    win.close()

def janela_movimentar(produto_id, nome, tipo):
    cor    = VERDE if tipo == "entrada" else VERMELHO
    titulo = "📦 Entrada de Estoque" if tipo == "entrada" else "📤 Saída de Estoque"
    layout = [
        [sg.Text(titulo, font=FONT_TITULO)],
        [sg.Text(f"Produto: {nome}", font=FONT_NORMAL)],
        [sg.HSeparator()],
        [sg.Text("Quantidade:", size=12), sg.Input(key="-QTD-", size=10)],
        [sg.Text("Observação:", size=12), sg.Input(key="-OBS-", size=30)],
        [sg.HSeparator()],
        [sg.Button("✅ Confirmar", button_color=(cor, "white")),
         sg.Button("❌ Cancelar")],
    ]
    win = sg.Window(titulo, layout, modal=True, font=FONT_NORMAL)
    while True:
        e, v = win.read()
        if e in (sg.WIN_CLOSED, "❌ Cancelar"):
            break
        if e == "✅ Confirmar":
            try:
                dados = {"quantidade": int(v["-QTD-"]), "observacao": v["-OBS-"]}
                if post(f"/produtos/{produto_id}/{tipo}", dados):
                    sg.popup(f"✅ {tipo.capitalize()} registrada!", title="Sucesso")
                    break
            except ValueError:
                sg.popup_error("Informe uma quantidade válida.")
    win.close()

def janela_historico():
    historico = get("/historico") or []
    dados = [
        [
            m["criado_em"][:16],
            m["produto"],
            m["tipo"].upper(),
            m["quantidade"],
            m["observacao"] or "—",
        ]
        for m in historico
    ]
    layout = [
        [sg.Text("📋 Histórico de Movimentações", font=FONT_TITULO)],
        [sg.Table(
            values=dados,
            headings=["Data/Hora", "Produto", "Tipo", "Qtd", "Observação"],
            col_widths=[16, 20, 8, 6, 28],
            auto_size_columns=False,
            display_row_numbers=False,
            justification="left",
            num_rows=15,
            key="-HIST-",
        )],
        [sg.Button("Fechar")],
    ]
    win = sg.Window("Histórico", layout, modal=True, font=FONT_NORMAL)
    win.read()
    win.close()

def main():
    col_esquerda = [
        [sg.Text("📊 Dashboard", font=FONT_TITULO)],
        [sg.HSeparator()],
        [sg.Text("Total de Produtos:", size=20),
         sg.Text("—", key="-D-PRODS-", font=("Helvetica", 13, "bold"))],
        [sg.Text("Total de Itens:", size=20),
         sg.Text("—", key="-D-ITENS-", font=("Helvetica", 13, "bold"))],
        [sg.Text("Valor em Estoque:", size=20),
         sg.Text("—", key="-D-VALOR-", font=("Helvetica", 13, "bold"))],
        [sg.Text("⚠️ Alertas:", size=20),
         sg.Text("—", key="-D-ALERT-", font=("Helvetica", 13, "bold"), text_color=AMARELO)],
        [sg.HSeparator()],
        [sg.Button("🔄 Atualizar",    button_color=(AZUL, "white"),      size=20)],
        [sg.Button("➕ Novo Produto", button_color=(VERDE, "white"),     size=20)],
        [sg.Button("📋 Histórico",    button_color=("white", "gray"),    size=20)],
        [sg.Button("⚠️ Ver Alertas",  button_color=(AMARELO, "black"),   size=20)],
        [sg.Button("🚪 Sair",         button_color=(VERMELHO, "white"),  size=20)],
    ]

    col_direita = [
        [sg.Text("🗃️ Produtos em Estoque", font=FONT_TITULO)],
        [sg.Input(size=35, key="-BUSCA-", enable_events=True, tooltip="Buscar..."),
         sg.Text("🔍")],
        [sg.Table(
            values=[],
            headings=["ID", "Nome", "Categoria", "Qtd", "Preço R$", "Mínimo"],
            col_widths=[4, 22, 14, 6, 10, 8],
            auto_size_columns=False,
            display_row_numbers=False,
            justification="left",
            num_rows=14,
            key="-TABLE-",
            enable_events=True,
            selected_row_colors=("white", AZUL),
        )],
        [sg.Button("📦 Entrada",  button_color=(VERDE, "white")),
         sg.Button("📤 Saída",    button_color=(VERMELHO, "white")),
         sg.Button("✏️ Editar",   button_color=(AZUL, "white")),
         sg.Button("🗑️ Excluir",  button_color=("white", VERMELHO))],
    ]

    layout = [
        [sg.Text("🏭  Controle de Estoque", font=("Helvetica", 20, "bold"), pad=(10, 10))],
        [sg.HSeparator()],
        [sg.Column(col_esquerda, vertical_alignment="top", pad=(10, 10)),
         sg.VSeparator(),
         sg.Column(col_direita,  vertical_alignment="top", pad=(10, 10))],
    ]

    window = sg.Window("Controle de Estoque", layout, font=FONT_NORMAL,
                       resizable=True, finalize=True)

    todos_produtos = []

    def carregar():
        nonlocal todos_produtos
        resumo = get("/resumo")
        if resumo:
            window["-D-PRODS-"].update(resumo["total_produtos"])
            window["-D-ITENS-"].update(resumo["total_itens"])
            window["-D-VALOR-"].update(f"R$ {resumo['valor_total']:,.2f}")
            window["-D-ALERT-"].update(resumo["alertas"])
        todos_produtos = get("/produtos") or []
        filtrar(window["-BUSCA-"].get())

    def filtrar(texto):
        texto = texto.lower()
        resultado = [
            p for p in todos_produtos
            if texto in p["nome"].lower() or texto in (p["categoria"] or "").lower()
        ]
        dados = [
            [p["id"], p["nome"], p["categoria"], p["quantidade"],
             f"R$ {p['preco']:.2f}", p["qtd_minima"]]
            for p in resultado
        ]
        window["-TABLE-"].update(values=dados)

    def produto_selecionado():
        sel = window["-TABLE-"].SelectedRows
        if not sel:
            sg.popup("Selecione um produto na tabela.", title="Aviso")
            return None
        texto = window["-BUSCA-"].get().lower()
        filtrado = [
            p for p in todos_produtos
            if texto in p["nome"].lower() or texto in (p["categoria"] or "").lower()
        ]
        return filtrado[sel[0]]

    carregar()

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "🚪 Sair"):
            break

        elif event == "🔄 Atualizar":
            carregar()

        elif event == "➕ Novo Produto":
            janela_adicionar_produto()
            carregar()

        elif event == "📋 Histórico":
            janela_historico()

        elif event == "⚠️ Ver Alertas":
            alertas = get("/alertas") or []
            if not alertas:
                sg.popup("✅ Nenhum produto com estoque baixo!", title="Alertas")
            else:
                msg = "\n".join([
                    f"• {p['nome']}: {p['quantidade']} un. (mín: {p['qtd_minima']})"
                    for p in alertas
                ])
                sg.popup(f"Produtos com estoque baixo:\n\n{msg}", title="⚠️ Alertas")

        elif event == "-BUSCA-":
            filtrar(values["-BUSCA-"])

        elif event == "📦 Entrada":
            p = produto_selecionado()
            if p:
                janela_movimentar(p["id"], p["nome"], "entrada")
                carregar()

        elif event == "📤 Saída":
            p = produto_selecionado()
            if p:
                janela_movimentar(p["id"], p["nome"], "saida")
                carregar()

        elif event == "✏️ Editar":
            p = produto_selecionado()
            if p:
                layout_edit = [
                    [sg.Text(f"Editar: {p['nome']}", font=FONT_TITULO)],
                    [sg.HSeparator()],
                    [sg.Text("Preço R$:",     size=14), sg.Input(str(p["preco"]),      key="-PRECO-", size=10)],
                    [sg.Text("Qtd. Mínima:",  size=14), sg.Input(str(p["qtd_minima"]), key="-MIN-",   size=10)],
                    [sg.HSeparator()],
                    [sg.Button("💾 Salvar"), sg.Button("❌ Cancelar")],
                ]
                w2 = sg.Window("Editar Produto", layout_edit, modal=True, font=FONT_NORMAL)
                e2, v2 = w2.read()
                w2.close()
                if e2 == "💾 Salvar":
                    put(f"/produtos/{p['id']}", {
                        "preco":      float(v2["-PRECO-"]),
                        "qtd_minima": int(v2["-MIN-"]),
                    })
                    carregar()

        elif event == "🗑️ Excluir":
            p = produto_selecionado()
            if p:
                if sg.popup_yes_no(f"Excluir '{p['nome']}'?", title="Confirmar") == "Yes":
                    delete(f"/produtos/{p['id']}")
                    carregar()

    window.close()


if __name__ == "__main__":
    main()

