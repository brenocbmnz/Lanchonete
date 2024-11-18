import grpc
from concurrent import futures
import generated.orders_pb2 as orders_pb2
import generated.orders_pb2_grpc as orders_pb2_grpc
import generated.inventory_pb2 as inventory_pb2
import generated.inventory_pb2_grpc as inventory_pb2_grpc
import generated.common_pb2 as common_pb2

# Classe que implementa o serviço OrderService
class OrderService(orders_pb2_grpc.OrderServiceServicer):
    def __init__(self):
        # Dicionário para armazenar os pedidos criados
        self.orders = {}
        # Canal de comunicação com o serviço de estoque (Inventory Service)
        self.inventory_channel = grpc.insecure_channel("localhost:50052")
        self.inventory_stub = inventory_pb2_grpc.InventoryServiceStub(self.inventory_channel)

    # Método para criar um pedido
    def CreateOrder(self, request, context):
        order_id = f"order_{len(self.orders) + 1}"  # Gera um ID único para o pedido
        items = request.items  # Itens do pedido

        # Verifica a disponibilidade de cada item no estoque
        for item in items:
            response = self.inventory_stub.CheckAvailability(item)
            if not response.available:
                print(f"[ORDER SERVICE] Falha ao criar pedido {order_id}: {item.item_name} não disponível")
                return orders_pb2.OrderResponse(order_id=order_id, status=response.message)

        # Atualiza o estoque subtraindo a quantidade dos itens solicitados
        for item in items:
            stock_response = self.inventory_stub.UpdateStock(common_pb2.Item(item_name=item.item_name, quantity=-item.quantity))
            if stock_response.status != "Updated":
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(f"Failed to update stock for item: {item.item_name}")
                print(f"[ORDER SERVICE] Falha ao atualizar estoque para {item.item_name} ao criar pedido {order_id}")
                return orders_pb2.OrderResponse(order_id=order_id, status="Stock update failed")

        # Armazena o pedido criado no dicionário de pedidos
        self.orders[order_id] = {"order_id": order_id, "customer_name": request.customer_name, "items": items, "status": "Confirmed"}
        print(f"[ORDER SERVICE] Pedido criado: {order_id} para cliente {request.customer_name}")
        return orders_pb2.OrderResponse(order_id=order_id, status="Confirmed")

    # Método para obter os detalhes de um pedido específico
    def GetOrder(self, request, context):
        order = self.orders.get(request.order_id, None)  # Procura o pedido pelo ID
        if not order:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            print(f"[ORDER SERVICE] Pedido {request.order_id} não encontrado")
            return orders_pb2.OrderDetails()

        # Retorna os detalhes do pedido encontrado
        return orders_pb2.OrderDetails(
            order_id=order["order_id"],
            customer_name=order["customer_name"],
            items=order["items"],
            status=order["status"]
        )

    # Método para obter todos os pedidos
    def GetAllOrders(self, request, context):
        all_orders = []
        # Itera sobre todos os pedidos e adiciona à lista de respostas
        for order in self.orders.values():
            all_orders.append(
                orders_pb2.OrderDetails(
                    order_id=order["order_id"],
                    customer_name=order["customer_name"],
                    items=order["items"],
                    status=order["status"]
                )
            )
        print(f"[ORDER SERVICE] Consultando todos os pedidos: {len(all_orders)} pedidos encontrados")
        return orders_pb2.AllOrdersResponse(orders=all_orders)

    # Método para cancelar um pedido
    def CancelOrder(self, request, context):
        order_id = request.order_id
        order = self.orders.get(order_id, None)

        if not order:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            print(f"[ORDER SERVICE] Tentativa de cancelar pedido {order_id}: Pedido não encontrado")
            return orders_pb2.OrderResponse(order_id=order_id, status="Order not found")

        if order["status"] == "Cancelled":
            print(f"[ORDER SERVICE] Tentativa de cancelar novamente o pedido: {order_id} - Ignorado")
            return orders_pb2.OrderResponse(order_id=order_id, status="Already cancelled")

        # Atualiza o status do pedido para Cancelled
        order["status"] = "Cancelled"
        print(f"[ORDER SERVICE] Pedido {order_id} cancelado - Atualizando estoque")

        # Devolve os itens do pedido ao estoque (adiciona a quantidade de volta)
        try:
            for item in order["items"]:
                print(f"[ORDER SERVICE] Devolvendo {item.quantity} unidades de {item.item_name} ao estoque")
                stock_response = self.inventory_stub.UpdateStock(common_pb2.Item(item_name=item.item_name, quantity=item.quantity))
                if stock_response.status != "Updated":
                    raise Exception(f"Failed to return stock for item: {item.item_name}")
            print(f"[ORDER SERVICE] Pedido cancelado: {order_id} - Estoque atualizado com sucesso")
        except Exception as e:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(str(e))
            print(f"[ORDER SERVICE] Falha ao atualizar estoque ao cancelar pedido {order_id}: {str(e)}")
            return orders_pb2.OrderResponse(order_id=order_id, status="Failed to return stock")

        return orders_pb2.OrderResponse(order_id=order_id, status="Cancelled")

    # Método para finalizar um pedido
    def FinishOrder(self, request, context):
        order_id = request.order_id
        order = self.orders.get(order_id, None)

        if not order:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            print(f"[ORDER SERVICE] Tentativa de finalizar pedido {order_id}: Pedido não encontrado")
            return orders_pb2.OrderResponse(order_id=order_id, status="Order not found")

        if order["status"] == "Finished":
            print(f"[ORDER SERVICE] Tentativa de finalizar novamente o pedido: {order_id} - Ignorado")
            return orders_pb2.OrderResponse(order_id=order_id, status="Already finished")

        if order["status"] != "Confirmed":
            print(f"[ORDER SERVICE] Pedido {order_id} não está em estado válido para finalizar")
            return orders_pb2.OrderResponse(order_id=order_id, status="Cannot finish order not confirmed")

        # Atualiza o status do pedido para Finished
        order["status"] = "Finished"
        print(f"[ORDER SERVICE] Pedido {order_id} finalizado com sucesso")
        return orders_pb2.OrderResponse(order_id=order_id, status="Finished")

# Função para iniciar o serviço de pedidos
def serve():
    # Cria um servidor gRPC com um pool de threads para lidar com várias requisições simultâneas
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Adiciona o OrderService ao servidor gRPC
    orders_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    # Define a porta onde o servidor irá escutar
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Order Service is running on port 50051...")
    # Mantém o servidor em execução
    server.wait_for_termination()

# Ponto de entrada principal do script
if __name__ == "__main__":
    serve()
