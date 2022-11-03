from __future__ import annotations
from pydantic import BaseModel
from typing import Union, TypeVar, Hashable, Generic, Dict, Tuple

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")
T = TypeVar("T")


class Node(BaseModel, Generic[T]):
    elem: T
    prev: Union[Node, None] = None
    next: Union[Node, None] = None


class LinkedList(BaseModel):
    head: Union[Node, None] = None
    tail: Union[Node, None] = None
    len: int = 0

    def push_front_node(self, node: Node):
        node.next = self.head
        if self.head:
            self.head.prev = node
        else:
            self.tail = node
        self.len += 1
        self.head = node

    def pop_back_node(self) -> Union[Node, None]:
        if self.tail:
            node = self.tail
            self.tail = node.prev
            self.len -= 1
            if self.tail:
                self.tail.next = None
            else:
                self.head = None
            return node
        else:
            return None

    def unlink_node(self, node: Node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail.prev = node.prev
        self.len -= 1


class LRUKCache(BaseModel, Generic[K, V]):
    k: int
    cap: int
    cache: Dict[K, Node[Tuple[K, V]]] = dict()
    cache_linked_list: LinkedList = LinkedList()
    history_cap: int
    history_cache: Dict[K, Tuple[Node[Tuple[K, V]], int]] = dict()
    history_linked_list: LinkedList = LinkedList()

    def put(self, key: K, value: V):
        result = self.history_cache.get(key)
        if result:
            (node, hit_count) = result
            if hit_count + 1 == self.k:
                self.history_cache.pop(key)
                self.history_linked_list.unlink_node(node)
                self.put_cache(node)
            else:

                self.history_cache[key] = (node, hit_count + 1)
        else:
            node = Node(elem=(key, value))
            self.history_cache[key] = (node, 0)
            self.history_linked_list.push_front_node(node)
            if self.history_linked_list.len > self.history_cap:
                node = self.history_linked_list.pop_back_node()
                try:
                    self.history_cache.pop(node.elem[0])
                except Exception as _:
                    pass

    def get(self, key: K) -> Union[V, None]:
        self.hit_history(key)
        return self.get_cache(key)

    def hit_history(self, key: K):
        result = self.history_cache.get(key)
        if result:
            (node, hit_count) = result
            if hit_count + 1 == self.k:
                try:
                    self.history_cache.pop(key)
                    self.history_linked_list.unlink_node(node)
                    self.put_cache(node)
                except Exception as _:
                    pass
            else:
                self.history_cache[key] = (node, hit_count + 1)
                self.history_linked_list.unlink_node(node)
                self.history_linked_list.push_front_node(node)

    def put_cache(self, node: Node):
        key = node.elem[0]
        try:
            n = self.cache.pop(key)
            self.cache_linked_list.unlink_node(n)
        except Exception as _:
            pass
        self.cache[key] = node
        self.cache_linked_list.push_front_node(node)
        if self.cache_linked_list.len > self.cap:
            delete_node = self.cache_linked_list.pop_back_node()
            self.cache.pop(delete_node.elem[0])

    def get_cache(self, key: K) -> Union[V, None]:
        node = self.cache.get(key)
        if node:
            self.cache_linked_list.unlink_node(node)
            self.cache_linked_list.push_front_node(node)
            return node.elem[1]
        else:
            return None
