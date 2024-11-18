import tkinter as tk
from tkinter import messagebox
import grpc
import generated.orders_pb2 as orders_pb2
import generated.orders_pb2_grpc as orders_pb2_grpc
import generated.common_pb2 as common_pb2
import generated.inventory_pb2 as inventory_pb2
import generated.inventory_pb2_grpc as inventory_pb2_grpc

# Função para enviar pedido
def make_order():
    customer_name = entry_customer_name.get()
    item_name = entry_item_name.get()
    quantity = entry_quantity.get()

    if not customer_name or not item_name or not quantity:
        messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
        return

    try:
        quantity = int(quantity)
    except ValueError:
        messagebox.showerror("Erro", "A quantidade deve ser um número inteiro.")
        return

    # Conecta ao serviço gRPC
    channel = grpc.insecure_channel("localhost:50051")
    order_stub = orders_pb2_grpc.OrderServiceStub(channel)

    try:
        response = order_stub.CreateOrder(
            orders_pb2.OrderRequest(
                customer_name=customer_name,
                items=[common_pb2.Item(item_name=item_name, quantity=quantity)]
            )
        )
        if response.status == "Confirmed":
            messagebox.showinfo("Pedido Confirmado", f"Pedido confirmado!\nID do pedido: {response.order_id}")
        else:
            messagebox.showwarning("Pedido Não Confirmado", f"Pedido não confirmado: {response.status}")
    except grpc.RpcError as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao servidor: {e}")

# Função para consultar o estoque disponível
def check_stock():
    channel = grpc.insecure_channel("localhost:50052")
    inventory_stub = inventory_pb2_grpc.InventoryServiceStub(channel)

    try:
        response = inventory_stub.GetStock(common_pb2.Empty())
        stock_info = "\n".join([f"{item.item_name}: {item.quantity}" for item in response.items])
        messagebox.showinfo("Estoque Disponível", f"Estoque atual:\n{stock_info}")
    except grpc.RpcError as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao servidor: {e}")

# Função para consultar todos os pedidos
def check_orders():
    channel = grpc.insecure_channel("localhost:50051")
    order_stub = orders_pb2_grpc.OrderServiceStub(channel)

    try:
        response = order_stub.GetAllOrders(common_pb2.Empty())
        if response.orders:
            orders_info = "\n\n".join([
                f"ID do Pedido: {order.order_id}\nCliente: {order.customer_name}\nItens: {', '.join([f'{item.item_name} ({item.quantity})' for item in order.items])}\nStatus: {order.status}"
                for order in response.orders
            ])
            messagebox.showinfo("Pedidos Realizados", f"Pedidos:\n{orders_info}")
        else:
            messagebox.showinfo("Pedidos Realizados", "Nenhum pedido realizado.")
    except grpc.RpcError as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao servidor: {e}")

# Função para cancelar um pedido
def cancel_order():
    order_id = entry_order_id.get()

    if not order_id:
        messagebox.showerror("Erro", "O ID do pedido é obrigatório.")
        return

    # Conecta ao serviço gRPC
    channel = grpc.insecure_channel("localhost:50051")
    order_stub = orders_pb2_grpc.OrderServiceStub(channel)

    try:
        response = order_stub.CancelOrder(orders_pb2.OrderID(order_id=order_id))
        if response.status == "Cancelled":
            messagebox.showinfo("Cancelamento de Pedido", f"Pedido cancelado com sucesso! Status: {response.status}")
        else:
            messagebox.showwarning("Cancelamento de Pedido", f"Falha ao cancelar o pedido: {response.status}")
    except grpc.RpcError as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao servidor: {e}")

# Função para finalizar um pedido
def finish_order():
    order_id = entry_order_id.get()

    if not order_id:
        messagebox.showerror("Erro", "O ID do pedido é obrigatório.")
        return

    # Conecta ao serviço gRPC
    channel = grpc.insecure_channel("localhost:50051")
    order_stub = orders_pb2_grpc.OrderServiceStub(channel)

    try:
        response = order_stub.FinishOrder(orders_pb2.OrderID(order_id=order_id))
        if response.status == "Finished":
            messagebox.showinfo("Pedido Finalizado", f"Pedido finalizado com sucesso! Status: {response.status}")
        else:
            messagebox.showwarning("Finalização de Pedido", f"Falha ao finalizar o pedido: {response.status}")
    except grpc.RpcError as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao servidor: {e}")

# Criando a interface gráfica
root = tk.Tk()
root.title("Lanchonete - Pedido de Itens")

# Labels e entradas para nome do cliente, item e quantidade
tk.Label(root, text="Nome do Cliente:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_customer_name = tk.Entry(root)
entry_customer_name.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Nome do Item:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_item_name = tk.Entry(root)
entry_item_name.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Quantidade:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_quantity = tk.Entry(root)
entry_quantity.grid(row=2, column=1, padx=10, pady=5)

# Botão para fazer pedido
btn_order = tk.Button(root, text="Fazer Pedido", command=make_order)
btn_order.grid(row=3, column=0, columnspan=2, pady=5)

# Botão para consultar estoque
btn_check_stock = tk.Button(root, text="Consultar Estoque", command=check_stock)
btn_check_stock.grid(row=4, column=0, columnspan=2, pady=5)

# Botão para consultar pedidos
btn_check_orders = tk.Button(root, text="Consultar Pedidos", command=check_orders)
btn_check_orders.grid(row=5, column=0, columnspan=2, pady=5)

# Campo de entrada para o ID do pedido
tk.Label(root, text="ID do Pedido:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
entry_order_id = tk.Entry(root)
entry_order_id.grid(row=6, column=1, padx=10, pady=5)

# Botão para cancelar pedido
btn_cancel_order = tk.Button(root, text="Cancelar Pedido", command=cancel_order)
btn_cancel_order.grid(row=7, column=0, columnspan=2, pady=5)

# Botão para finalizar pedido
btn_finish_order = tk.Button(root, text="Finalizar Pedido", command=finish_order)
btn_finish_order.grid(row=8, column=0, columnspan=2, pady=5)

# Inicia o loop da interface
root.mainloop()
