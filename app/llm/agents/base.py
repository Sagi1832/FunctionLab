from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InT = TypeVar("InT")
OutT = TypeVar("OutT")

class Agent(ABC, Generic[InT, OutT]):
    @abstractmethod
    def run(self, payload: InT) -> OutT: 
        pass
