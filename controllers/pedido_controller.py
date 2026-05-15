"""
controllers/pedido_controller.py
Lógica de negócio entre as views e os models de pedido.
"""
from __future__ import annotations
from tkinter import messagebox, filedialog
from models import pedido_model, config_model
from models.pedido_model import Pedido, ItemPedido
from controllers import pdf_controller


class PedidoController:
    def __init__(self, app):
        self.app = app  # referência à janela principal (App)

    # ── Lista ────────────────────────────────────────────────────────────────

    def listar(self, busca: str = "", status: str = "") -> list[dict]:
        return pedido_model.listar(busca, status)

    def dashboard(self) -> dict:
        return pedido_model.dashboard_stats()

    def ranking_referencias(self, limit: int = 10) -> list[dict]:
            return pedido_model.referencias_mais_vendidas(limit)
    # ── CRUD ─────────────────────────────────────────────────────────────────

    def novo(self) -> Pedido:
        from datetime import date
        p = Pedido()
        p.dt_pedido = date.today().strftime("%d/%m/%Y")
        return p

    def carregar(self, pedido_id: int) -> Pedido | None:
        return pedido_model.buscar(pedido_id)

    def salvar(self, pedido: Pedido) -> bool:
        if not pedido.cliente_nome.strip():
            messagebox.showerror("Campo obrigatório", "Informe o nome do cliente.")
            return False
        if not pedido.itens:
            messagebox.showerror("Sem itens", "Adicione pelo menos uma referência ao pedido.")
            return False
        pedido_model.salvar(pedido)
        return True

    def excluir(self, pedido_id: int) -> bool:
        if messagebox.askyesno("Confirmar exclusão",
                               "Deseja excluir este pedido permanentemente?\n"
                               "Esta ação não pode ser desfeita."):
            pedido_model.excluir(pedido_id)
            return True
        return False

    # ── PDF ──────────────────────────────────────────────────────────────────

    def exportar_pdf(self, pedido: Pedido):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"Pedido_{pedido.numero or 'novo'}.pdf",
            title="Salvar pedido como PDF",
        )
        if not path:
            return
        try:
            pdf_controller.gerar(pedido, path)
            if messagebox.askyesno("PDF gerado com sucesso!",
                                   f"Arquivo salvo em:\n{path}\n\nDeseja abrir agora?"):
                import os, subprocess, sys
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.call(["open", path])
                else:
                    subprocess.call(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Erro ao gerar PDF", str(e))

    # ── Clientes ─────────────────────────────────────────────────────────────

    def clientes(self) -> list[dict]:
        return pedido_model.clientes_unicos()


class ConfigController:
    def get(self, chave: str, default: str = "") -> str:
        return config_model.get(chave, default)

    def get_all(self) -> dict:
        return config_model.get_all()

    def salvar(self, dados: dict):
        for k, v in dados.items():
            config_model.set_value(k, v)
        messagebox.showinfo("Configurações salvas", "As configurações foram salvas com sucesso.")
