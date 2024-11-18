import grpc
from concurrent import futures
import generated.inventory_pb2 as inventory_pb2
import generated.inventory_pb2_grpc as inventory_pb2_grpc
import generated.common_pb2 as common_pb2
import threading

class InventoryService(inventory_pb2_grpc.InventoryServiceServicer):
    def __init__(self):
        # Inicializa o estoque com alguns itens e quantidades
        self.stock = {"burger": 10, "fries": 20, "soda": 30}
        # Lock para garantir exclusão mútua e evitar problemas de concorrência
        self.lock = threading.Lock()

    # Método para verificar a disponibilidade de um item no estoque
    def CheckAvailability(self, request, context):
        item = request.item_name
        quantity = request.quantity

        # Usa o lock para garantir que a leitura do estoque seja segura em um ambiente multi-thread
        with self.lock:
            if item in self.stock and self.stock[item] >= quantity:
                print(f"[INVENTORY SERVICE] Verificando disponibilidade de {item}: disponível ({self.stock[item]} em estoque, pedido = {quantity})")
                return inventory_pb2.AvailabilityResponse(available=True, message="Available")
            print(f"[INVENTORY SERVICE] Verificando disponibilidade de {item}: indisponível ({self.stock[item]} em estoque, pedido = {quantity})")
            return inventory_pb2.AvailabilityResponse(available=False, message="Out of stock")

    # Método para atualizar o estoque de um item (adicionar ou remover quantidade)
    def UpdateStock(self, request, context):
        item = request.item_name
        quantity = request.quantity

        # Usa o lock para garantir que a atualização do estoque seja segura
        with self.lock:
            if item not in self.stock:
                print(f"[INVENTORY SERVICE] Atualizando estoque - Item {item} não encontrado")
                return inventory_pb2.StockUpdateResponse(status="Item not found")

            # Calcula a nova quantidade do item no estoque
            new_quantity = self.stock[item] + quantity
            if new_quantity < 0:
                print(f"[INVENTORY SERVICE] Atualizando estoque - Estoque insuficiente para {item} (tentativa de reduzir {quantity}, atual = {self.stock[item]})")
                return inventory_pb2.StockUpdateResponse(status="Insufficient stock")

            # Atualiza o estoque com a nova quantidade
            self.stock[item] = new_quantity
            print(f"[INVENTORY SERVICE] Atualizando estoque de {item}: nova quantidade = {self.stock[item]} (quantidade alterada = {quantity})")
            return inventory_pb2.StockUpdateResponse(status="Updated")

    # Método para consultar o estoque atual de todos os itens
    def GetStock(self, request, context):
        # Usa o lock para garantir que a leitura do estoque seja segura
        with self.lock:
            stock_items = []
            # Cria uma lista de itens do estoque para enviar como resposta
            for item_name, quantity in self.stock.items():
                stock_items.append(inventory_pb2.StockItem(item_name=item_name, quantity=quantity))
            print(f"[INVENTORY SERVICE] Consultando estoque: {self.stock}")
            return inventory_pb2.StockResponse(items=stock_items)

# Função para iniciar o serviço de estoque
def serve():
    # Cria um servidor gRPC com um pool de threads para lidar com várias requisições simultâneas
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Adiciona o InventoryService ao servidor gRPC
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryService(), server)
    # Define a porta onde o servidor irá escutar
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Inventory Service is running on port 50052...")
    # Mantém o servidor em execução
    server.wait_for_termination()

# Ponto de entrada principal do script
if __name__ == "__main__":
    serve()
