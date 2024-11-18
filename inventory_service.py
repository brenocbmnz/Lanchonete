import grpc
from concurrent import futures
import generated.inventory_pb2 as inventory_pb2
import generated.inventory_pb2_grpc as inventory_pb2_grpc
import generated.common_pb2 as common_pb2
import threading

class InventoryService(inventory_pb2_grpc.InventoryServiceServicer):
    def __init__(self):
        self.stock = {"burger": 10, "fries": 20, "soda": 30}
        self.lock = threading.Lock()  # Lock para garantir exclusão mútua

    def CheckAvailability(self, request, context):
        item = request.item_name
        quantity = request.quantity

        with self.lock:
            if item in self.stock and self.stock[item] >= quantity:
                print(f"[INVENTORY SERVICE] Verificando disponibilidade de {item}: disponível ({self.stock[item]} em estoque, pedido = {quantity})")
                return inventory_pb2.AvailabilityResponse(available=True, message="Available")
            print(f"[INVENTORY SERVICE] Verificando disponibilidade de {item}: indisponível ({self.stock[item]} em estoque, pedido = {quantity})")
            return inventory_pb2.AvailabilityResponse(available=False, message="Out of stock")

    def UpdateStock(self, request, context):
        item = request.item_name
        quantity = request.quantity

        with self.lock:
            if item not in self.stock:
                print(f"[INVENTORY SERVICE] Atualizando estoque - Item {item} não encontrado")
                return inventory_pb2.StockUpdateResponse(status="Item not found")

            new_quantity = self.stock[item] + quantity
            if new_quantity < 0:
                print(f"[INVENTORY SERVICE] Atualizando estoque - Estoque insuficiente para {item} (tentativa de reduzir {quantity}, atual = {self.stock[item]})")
                return inventory_pb2.StockUpdateResponse(status="Insufficient stock")

            # Atualiza o estoque
            self.stock[item] = new_quantity
            print(f"[INVENTORY SERVICE] Atualizando estoque de {item}: nova quantidade = {self.stock[item]} (quantidade alterada = {quantity})")
            return inventory_pb2.StockUpdateResponse(status="Updated")

    def GetStock(self, request, context):
        with self.lock:
            stock_items = []
            for item_name, quantity in self.stock.items():
                stock_items.append(inventory_pb2.StockItem(item_name=item_name, quantity=quantity))
            print(f"[INVENTORY SERVICE] Consultando estoque: {self.stock}")
            return inventory_pb2.StockResponse(items=stock_items)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Inventory Service is running on port 50052...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
