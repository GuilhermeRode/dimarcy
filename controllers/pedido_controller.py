from __future__ import annotations
from tkinter import messagebox, filedialog
from models import pedido_model, config_model
from models.pedido_model import Pedido
from controllers import pdf_controller


class PedidoController:
    def __init__(self, app):
        self.app = app

    def listar(self, busca="", status=""):
        return pedido_model.listar(busca, status)

    def dashboard(self):
        return pedido_model.dashboard_stats()

    def ranking_referencias(self, limit=10):
        return pedido_model.referencias_mais_vendidas(limit)

    def novo(self) -> Pedido:
        from datetime import date
        p = Pedido()
        p.dt_pedido = date.today().strftime("%d/%m/%Y")
        return p

    def carregar(self, pedido_id: int):
        return pedido_model.buscar(pedido_id)

    def salvar(self, pedido: Pedido) -> bool:
        if not pedido.cliente_nome.strip():
            messagebox.showerror("Campo obrigatório","Informe o nome do cliente.")
            return False
        if not pedido.itens:
            messagebox.showerror("Sem itens","Adicione pelo menos uma referência.")
            return False
        pedido_model.salvar(pedido)
        return True

    def excluir(self, pedido_id: int) -> bool:
        if messagebox.askyesno("Confirmar exclusão",
                               "Excluir este pedido permanentemente?"):
            pedido_model.excluir(pedido_id)
            return True
        return False

    def exportar_pdf(self, pedido: Pedido):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF","*.pdf")],
            initialfile=f"Pedido_{pedido.numero or 'novo'}.pdf")
        if not path: return
        try:
            pdf_controller.gerar(pedido, path)
            if messagebox.askyesno("PDF gerado!",
                                   f"Salvo em:\n{path}\n\nAbrir agora?"):
                import os, subprocess, sys
                if sys.platform=="win32": os.startfile(path)
                elif sys.platform=="darwin": subprocess.call(["open",path])
                else: subprocess.call(["xdg-open",path])
        except Exception as e:
            messagebox.showerror("Erro ao gerar PDF", str(e))

    def clientes(self):
        return pedido_model.clientes_unicos()

    def vendedores(self):
        return pedido_model.listar_vendedores()

    def buscar_produto(self, ref: str):
        return pedido_model.buscar_produto(ref)


class ConfigController:
    def get(self, chave, default=""): return config_model.get(chave, default)
    def get_all(self): return config_model.get_all()
    def salvar(self, dados: dict):
        for k, v in dados.items(): config_model.set_value(k, v)
        messagebox.showinfo("Salvo","Configurações salvas com sucesso.")