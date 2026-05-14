# 🧶 Tricot Pedidos — v2.0 MVC

Sistema desktop de gerenciamento de pedidos para empresa de tricot.
Banco de dados SQLite local + PDF profissional + arquitetura MVC.

---

## 🚀 Instalação e execução

```bash
pip install -r requirements.txt
python app.py
```

No Windows, clique duplo em `iniciar.bat`.

---

## 🗂️ Estrutura do projeto (MVC)

```
tricot_pedidos/
│
├── app.py                        ← Entry point, janela principal, roteamento
│
├── models/                       ← DADOS (Model)
│   ├── database.py               ← Conexão SQLite, init_db()
│   ├── config_model.py           ← CRUD de configurações
│   └── pedido_model.py           ← Pedido, ItemPedido, CRUD completo
│
├── views/                        ← INTERFACE (View)
│   ├── theme.py                  ← Tokens de design centralizados
│   ├── widgets.py                ← Componentes reutilizáveis (Card, Btn, etc.)
│   ├── dashboard_view.py         ← Página inicial com estatísticas
│   ├── lista_view.py             ← Lista de pedidos com busca e filtros
│   ├── form_pedido_view.py       ← Formulário de criação/edição de pedidos
│   ├── clientes_view.py          ← Histórico de clientes
│   └── config_view.py            ← Configurações da empresa
│
├── controllers/                  ← LÓGICA (Controller)
│   ├── pedido_controller.py      ← Regras de negócio de pedidos
│   └── pdf_controller.py         ← Geração de PDF com ReportLab
│
├── pedidos.db                    ← Banco de dados SQLite (gerado automaticamente)
├── requirements.txt
└── iniciar.bat                   ← Atalho Windows
```

---

## 🖥️ Funcionalidades

| Módulo        | Funcionalidade                                              |
|---------------|-------------------------------------------------------------|
| Dashboard     | Estatísticas gerais, faturamento, pedidos por status        |
| Pedidos       | Lista com busca, filtro por status, alteração rápida        |
| Novo pedido   | Cliente, datas, entrega, pagamento, grade PP→Único          |
| Itens         | N referências por pedido, cor, material, preço e tamanhos   |
| Totais        | Cálculo automático com desconto                             |
| PDF           | Documento A4 profissional com tabela de tamanhos            |
| Clientes      | Histórico com total de pedidos e valor gasto                |
| Configurações | Nome e dados da empresa (usados no PDF)                     |

---

## 💾 Backup

O arquivo `pedidos.db` contém todos os dados. Copie-o para fazer backup.

---

## 🔧 Personalização

Para mudar cores e fontes de toda a aplicação, edite apenas `views/theme.py`.
