# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: orders.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'orders.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import common_pb2 as common__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0corders.proto\x1a\x0c\x63ommon.proto\"B\n\x0cOrderRequest\x12\x15\n\rcustomer_name\x18\x01 \x01(\t\x12\x1b\n\x05items\x18\x02 \x03(\x0b\x32\x0c.common.Item\"1\n\rOrderResponse\x12\x10\n\x08order_id\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\t\"d\n\x0cOrderDetails\x12\x10\n\x08order_id\x18\x01 \x01(\t\x12\x15\n\rcustomer_name\x18\x02 \x01(\t\x12\x1b\n\x05items\x18\x03 \x03(\x0b\x32\x0c.common.Item\x12\x0e\n\x06status\x18\x04 \x01(\t\"\x1b\n\x07OrderID\x12\x10\n\x08order_id\x18\x01 \x01(\t\"2\n\x11\x41llOrdersResponse\x12\x1d\n\x06orders\x18\x01 \x03(\x0b\x32\r.OrderDetails2\xbd\x01\n\x0cOrderService\x12,\n\x0b\x43reateOrder\x12\r.OrderRequest\x1a\x0e.OrderResponse\x12#\n\x08GetOrder\x12\x08.OrderID\x1a\r.OrderDetails\x12\x31\n\x0cGetAllOrders\x12\r.common.Empty\x1a\x12.AllOrdersResponse\x12\'\n\x0b\x43\x61ncelOrder\x12\x08.OrderID\x1a\x0e.OrderResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'orders_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ORDERREQUEST']._serialized_start=30
  _globals['_ORDERREQUEST']._serialized_end=96
  _globals['_ORDERRESPONSE']._serialized_start=98
  _globals['_ORDERRESPONSE']._serialized_end=147
  _globals['_ORDERDETAILS']._serialized_start=149
  _globals['_ORDERDETAILS']._serialized_end=249
  _globals['_ORDERID']._serialized_start=251
  _globals['_ORDERID']._serialized_end=278
  _globals['_ALLORDERSRESPONSE']._serialized_start=280
  _globals['_ALLORDERSRESPONSE']._serialized_end=330
  _globals['_ORDERSERVICE']._serialized_start=333
  _globals['_ORDERSERVICE']._serialized_end=522
# @@protoc_insertion_point(module_scope)
