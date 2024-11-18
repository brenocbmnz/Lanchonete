import grpc
from concurrent import futures
import generated.orders_pb2 as orders_pb2
import generated.orders_pb2_grpc as orders_pb2_grpc
import generated.inventory_pb2 as inventory_pb2
import generated.inventory_pb2_grpc as inventory_pb2_grpc
import generated.common_pb2 as common_pb2

class OrderService(orders_pb2_grpc.OrderServiceServicer):
    def __init__(self):
        self.orders = {}
        self.inventory_channel = grpc.insecure_channel("localhost:50052")
        self.inventory_stub = inventory_pb2_grpc.InventoryServiceStub(self.inventory_channel)

    def CreateOrder(self, request, context):
        order_id = f"order_{len(self.orders) + 1}"
        items = request.items

        # Check availability
        for item in items:
            response = self.inventory_stub.CheckAvailability(item)
            if not response.available:
                print(f"[ORDER SERVICE] Falha ao criar pedido {order_id}: {item.item_name} não disponível")
                return orders_pb2.OrderResponse(order_id=order_id, status=response.message)

        # Update stock (subtrair quantidade)
        for item in items:
            stock_response = self.inventory_stub.UpdateStock(common_pb2.Item(item_name=item.item_name, quantity=-item.quantity))
            if stock_response.status != "Updated":
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(f"Failed to update stock for item: {item.item_name}")
                print(f"[ORDER SERVICE] Falha ao atualizar estoque para {item.item_name} ao criar pedido {order_id}")
                return orders_pb2.OrderResponse(order_id=order_id, status="Stock update failed")

        # Save order
        self.orders[order_id] = {"order_id": order_id, "customer_name": request.customer_name, "items": items, "status": "Confirmed"}
        print(f"[ORDER SERVICE] Pedido criado: {order_id} para cliente {request.customer_name}")
        return orders_pb2.OrderResponse(order_id=order_id, status="Confirmed")

    def GetOrder(self, request, context):
        order = self.orders.get(request.order_id, None)
        if not order:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            print(f"[ORDER SERVICE] Pedido {request.order_id} não encontrado")
            return orders_pb2.OrderDetails()

        return orders_pb2.OrderDetails(
            order_id=order["order_id"],
            customer_name=order["customer_name"],
            items=order["items"],
            status=order["status"]
        )

    def GetAllOrders(self, request, context):
        all_orders = []
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

        # Update status to Cancelled
        order["status"] = "Cancelled"
        print(f"[ORDER SERVICE] Pedido {order_id} cancelado - Atualizando estoque")

        # Return items to stock (adicionar quantidade)
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

        # Update status to Finished
        order["status"] = "Finished"
        print(f"[ORDER SERVICE] Pedido {order_id} finalizado com sucesso")
        return orders_pb2.OrderResponse(order_id=order_id, status="Finished")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Order Service is running on port 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
