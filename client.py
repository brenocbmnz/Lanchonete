import grpc
import generated.orders_pb2 as orders_pb2
import generated.orders_pb2_grpc as orders_pb2_grpc
import generated.common_pb2 as common_pb2  # Importar common_pb2 para usar Item e Empty

channel = grpc.insecure_channel("localhost:50051")
order_stub = orders_pb2_grpc.OrderServiceStub(channel)

# Criar pedido usando o Item do common_pb2
response = order_stub.CreateOrder(
    orders_pb2.OrderRequest(
        customer_name="Alice",
        items=[common_pb2.Item(item_name="burger", quantity=2)]  # Usando Item de common_pb2
    )
)
print(f"Order Status: {response.status}")

# Consultar todos os pedidos usando Empty do common_pb2
all_orders_response = order_stub.GetAllOrders(common_pb2.Empty())
for order in all_orders_response.orders:
    print(f"Cliente: {order.customer_name}, Status: {order.status}")
