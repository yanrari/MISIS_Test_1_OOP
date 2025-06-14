from abc import ABC, abstractmethod
from typing import List, Optional
import copy
import re
from io import StringIO

class Printable(ABC):
    """Base abstract class for printable objects."""
    
    def print_me(self, os, prefix="", is_last=False, no_slash=False, is_root=False):
        """Base printing method for the tree structure display.
        Implement properly to display hierarchical structure."""
        buffer = StringIO()

        has_prefix = len(prefix) > 0

        if has_prefix:
            buffer.write(" " if no_slash else "|")

        if is_root and not has_prefix or has_prefix:
            buffer.write(prefix)
            buffer.write("\\-" if is_last else "+-")

        buffer.write(os)
        buffer.write("\n")
        
        val = buffer.getvalue()
        buffer.flush()
        buffer.close()

        return val

        
    @abstractmethod
    def clone(self):
        """Create a deep copy of this object."""
        pass

class BasicCollection(Printable):
    """Base class for collections of items."""
    def __init__(self):
        self._items = []
    
    def add(self, elem):
        self._items.append(elem)
    
    def find(self, elem):
        index = self._items.index(elem)
        return self._items[index]
    
    def clone(self):
        return copy.deepcopy(self)

class Component(Printable):
    """Base class for computer components."""

    def clone(self):
        return copy.deepcopy(self)

class Address(Printable):
    """Class representing a network address."""
    def __init__(self, addr):
        self.validate(addr)
        self.__address = addr
    
    def validate(self, addr):
        pattern = r"[0-9]{1,3}\.{0,1}"

        if not re.match(pattern, addr):
            raise ValueError("Malformed network address")
        
    def print_me(self, no_slash):
        return super().print_me(os=self.__address, prefix=" ", no_slash=no_slash)

    def clone(self):
        return copy.deepcopy(self)

class Computer(BasicCollection, Component):
    """Class representing a computer with addresses and components."""
    def __init__(self, name):
        BasicCollection.__init__(self)
        Component.__init__(self)
        self.name = name
        self.__addresses = []
    
    def add_address(self, addr):
        self.__addresses.append(Address(addr))
        return self
    
    def add_component(self, comp):
        self.add(comp)
        return self

    @property
    def components(self):
        return self._items

    def print_me(self, is_last, no_slash):
        buffer = StringIO()

        buffer.write(super(Component, self).print_me(os=f"Host: {self.name}", is_last=is_last, is_root=True))
        
        for addr in self.__addresses:
            buffer.write(addr.print_me(no_slash=no_slash))

        components_count = len(self._items)
        for idx in range(components_count):
            if idx == components_count - 1:
                buffer.write(self._items[idx].print_me(is_last=True, no_slash=is_last))
            else:
                buffer.write(self._items[idx].print_me(is_last=False, no_slash=is_last))

        val = buffer.getvalue()
        buffer.flush()
        buffer.close()

        return val

    def clone(self):
        return copy.deepcopy(self)

class Network(Printable):
    """Class representing a network of computers."""
    def __init__(self, name):
        self.__name = name
        self.__computers: list[Computer] = []
    
    def add_computer(self, comp: Computer):
        self.__computers.append(comp)
        return self
    
    def find_computer(self, name):
        found = list(filter(lambda c: c.name == name, self.__computers))
        return found[0] if len(found) > 0 else None
    
    def __str__(self):
        buffer = StringIO()

        buffer.write(super().print_me(os=f"Network: {self.__name}", is_root=False))

        computers_count = len(self.__computers)
        for idx in range(computers_count):
            if idx == computers_count - 1:
                buffer.write(self.__computers[idx].print_me(is_last=True, no_slash=True))
            else:
                buffer.write(self.__computers[idx].print_me(is_last=False, no_slash=False))

        val = buffer.getvalue()

        buffer.flush()
        buffer.close()

        return val.rstrip()

    def clone(self):
        return copy.deepcopy(self)

class Disk(Component):
    """Disk component class with partitions."""
    # Определение типов дисков
    SSD = 0
    MAGNETIC = 1
    
    def __init__(self, storage_type: int, size: int):
        # Initialize properly
        self.partitions: list[tuple] = []
        if (storage_type not in [self.SSD, self.MAGNETIC]):
            raise ValueError("Invalid storage type. Shoud be 0 for SSD or 1 for MAGNETIC")
        
        self.__storage_type = storage_type
        self.__size = size
    
    def __str__(self):
        return "HDD" if self.__storage_type == 1 else "SSD"

    def add_partition(self, size: int, name: str):
        reminder = self.__size - sum(t[0] for t in self.partitions)

        if size > reminder:
            raise ValueError("Cannot add partition! Not enogh space remained on the disk!")

        self.partitions.append((size, name))
        return self
    
    def print_me(self, is_last, no_slash):
        buffer = StringIO()

        buffer.write(super().print_me(os=f"{str(self)}, {self.__size} GiB", prefix=" ", is_last=is_last, no_slash=no_slash))

        partitions_count = len(self.partitions)
        for idx in range(partitions_count):
            p_size, p_type = self.partitions[idx]
            if idx == partitions_count - 1:
                buffer.write(super().print_me(os=f"[{idx}]: {p_size} GiB, {p_type}", prefix=f"   ", is_last=True, no_slash=no_slash))
            else:
                buffer.write(super().print_me(os=f"[{idx}]: {p_size} GiB, {p_type}", prefix=f"   ", is_last=False, no_slash=no_slash))

        val = buffer.getvalue()
        buffer.flush()
        buffer.close()

        return val

    def clone(self):
        return copy.deepcopy(self)

class CPU(Component):
    """CPU component class."""
    def __init__(self, cores: int, mhz: int):
        self.__cores = cores
        self.__mhz = mhz

    def print_me(self, is_last, no_slash):
        return super().print_me(os=f"CPU, {self.__cores} cores @ {self.__mhz}MHz", prefix=" ", is_last=is_last, no_slash=no_slash)

    def clone(self):
        return copy.deepcopy(self)

class Memory(Component):
    """Memory component class."""
    def __init__(self, size: int):
        self.__size = size
        
    def print_me(self, is_last, no_slash):
        return super().print_me(os=f"Memory, {self.__size} MiB", prefix=" ", is_last=is_last, no_slash=no_slash)

    def clone(self):
        return copy.deepcopy(self)

# Пример использования (может быть неполным или содержать ошибки)
def main():
    # Создание тестовой сети
    n = Network("MISIS network")
    
    # Добавляем первый сервер с одним CPU и памятью
    n.add_computer(
        Computer("server1.misis.ru")
        .add_address("192.168.1.1")
        .add_component(CPU(4, 2500))
        .add_component(Memory(16000))
    )
    
    # Добавляем второй сервер с CPU и HDD с разделами
    n.add_computer(
        Computer("server2.misis.ru")
        .add_address("10.0.0.1")
        .add_component(CPU(8, 3200))
        .add_component(
            Disk(Disk.MAGNETIC, 2000)
            .add_partition(500, "system")
            .add_partition(1500, "data")
        )
    )
    
    # Выводим сеть для проверки форматирования
    print("=== Созданная сеть ===")
    print(n)
    
    # Тест ожидаемого вывода
    expected_output = """Network: MISIS network
+-Host: server1.misis.ru
| +-192.168.1.1
| +-CPU, 4 cores @ 2500MHz
| \-Memory, 16000 MiB
\-Host: server2.misis.ru
  +-10.0.0.1
  +-CPU, 8 cores @ 3200MHz
  \-HDD, 2000 GiB
    +-[0]: 500 GiB, system
    \-[1]: 1500 GiB, data"""

    print("=== Ожидаемый формат вывода ===")
    print(expected_output)
    
    assert str(n) == expected_output, "Формат вывода не соответствует ожидаемому"
    print("✓ Тест формата вывода пройден")
    
    # Тестируем глубокое копирование
    print("\n=== Тестирование глубокого копирования ===")
    x = n.clone()
    
    # Тестируем поиск компьютера
    print("Поиск компьютера server2.misis.ru:")
    c = x.find_computer("server2.misis.ru")
    
    # Модифицируем найденный компьютер в копии
    print("\nДобавляем SSD к найденному компьютеру в копии:")
    c.add_component(
        Disk(Disk.SSD, 500)
        .add_partition(500, "fast_storage")
    )

    # Проверяем, что оригинал не изменился
    print("\n=== Модифицированная копия ===")
    print(x)
    print("\n=== Исходная сеть (должна остаться неизменной) ===")
    print(n)
    
    # Проверяем ассерты для тестирования системы
    print("\n=== Выполнение тестов ===")
    
    # Тест поиска
    assert x.find_computer("server1.misis.ru") is not None, "Компьютер не найден"
    print("✓ Тест поиска пройден")
    
    # Тест независимости копий
    original_server2 = n.find_computer("server2.misis.ru")
    modified_server2 = x.find_computer("server2.misis.ru")
    
    original_components = sum(1 for _ in original_server2.components)
    modified_components = sum(1 for _ in modified_server2.components)
    
    assert original_components == 2, f"Неверное количество компонентов в оригинале: {original_components}"
    assert modified_components == 3, f"Неверное количество компонентов в копии: {modified_components}"
    print("✓ Тест независимости копий пройден")
    
    # Проверка типов дисков
    disk_tests = [
        (Disk(Disk.SSD, 256), "SSD"),
        (Disk(Disk.MAGNETIC, 1000), "HDD")
    ]
    
    for disk, expected_type in disk_tests:
        assert expected_type in str(disk), f"Неверный тип диска в выводе: {str(disk)}"
    print("✓ Тест типов дисков пройден")
    
    print("\nВсе тесты пройдены!")

if __name__ == "__main__":
    main()
