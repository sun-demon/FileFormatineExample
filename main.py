import os.path
import shutil
import xml.etree.ElementTree
from glob import glob
import xml.etree.ElementTree as ET
from enum import Enum, auto
from operator import attrgetter


def filenames_started_with_a_recursive(start_directory: str, pattern: str):
    return [filename for filename in glob(f'{start_directory}/**/{pattern}', recursive=True) if
            os.path.isfile(filename)]


def zip_directory_with_file_patterns_info(dirname: str, pattern: str):
    filenames = filenames_started_with_a_recursive(dirname, pattern)
    print('\n'.join(filenames))
    with open('log.txt', 'w') as log_file:
        log_file.write('\n'.join(filenames))
    shutil.make_archive(f'{dirname}', 'zip', dirname)


class Color(Enum):
    RED = 31
    GREEN = auto()
    YELLOW = auto()
    BLUE = auto()
    MAGENTA = auto()
    CYAN = auto()
    LIGHT_RED = 91
    LIGHT_GREEN = auto()
    LIGHT_YELLOW = auto()
    LIGHT_BLUE = auto()
    LIGHT_MAGENTA = auto()
    LIGHT_CYAN = auto()

    def __lt__(self, other) -> bool:
        return self.value < other.value


class Car:
    class Brand(Enum):
        LINCOLN = 1
        KIA = auto()
        ACURA = auto()
        SUBARU = auto()
        AUDI = auto()
        HONDA = auto()
        BMW = auto()
        MAZDA = auto()
        LEXUS = auto()
        TOYOTA = auto()

        def __lt__(self, other) -> bool:
            return self.name < other.name

    def __init__(self, number: str, brand: Brand, color: Color, owner: str):
        self.number = number
        self.brand = brand
        self.color = color
        self.owner = owner

    def __str__(self) -> str:
        return f'number: {self.number}, brand: {self.brand}, color: {self.color}, owner: {self.owner}'


class CarDataBase:
    def __init__(self, filename: str):
        self.filename = filename
        self.root = ET.Element('cars')
        if os.path.exists(filename) and os.path.isfile(filename):
            try:
                tree = ET.parse(filename)
                self.root = tree.getroot()
            except xml.etree.ElementTree.ParseError as e:
                print(e)
                self.root = ET.Element('cars')

    def __del__(self):
        with open(self.filename, 'w') as file:
            ET.indent(self.root, space='    ')
            file.write(ET.tostring(self.root).decode('utf-8'))

    def remove_car_by_number(self, number: str) -> None:
        for elem in self.root.iter('car'):
            if elem.get('number') == number:
                self.root.remove(elem)

    def insert_car(self, car: Car) -> None:
        new_elem = ET.Element('car')
        new_elem.set('number', car.number)
        new_elem.set('brand', car.brand.name)
        new_elem.set('color', car.color.name)
        new_elem.set('owner', car.owner)
        self.root.append(new_elem)

    def cars(self) -> list:
        result: list = []
        for elem in self.root.iter('car'):
            number = elem.get('number')
            brand = [brand for brand in Car.Brand if brand.name == elem.get('brand')][0]
            color = [color for color in Color if color.name == elem.get('color')][0]
            owner = elem.get('owner')
            result.append(Car(number, brand, color, owner))
        return result

    def get_car_by_number(self, number: str) -> Car | None:
        filter_result = [car for car in self.cars() if car.number == number]
        if len(filter_result) == 0:
            return None
        return filter_result[0]

    def sort_by_attribute(self, attribute_name):
        cars = self.cars()
        cars.sort(key=attrgetter(attribute_name))
        self.root.clear()
        for car in cars:
            self.insert_car(car)


def press_enter_for_continue() -> None:
    input('Press ENTER for continue...')


def select_item() -> int:
    return int(input('Select item > '))


def remove_entry_by_number_wrapper(database: CarDataBase) -> None:
    number = input('Enter car number: ')
    database.remove_car_by_number(number)


def insert_entry_wrapper(database: CarDataBase) -> None:
    print('Enter car info:')
    number = input('number: ')
    print('Car brands:')
    brands = [brand for brand in Car.Brand]
    for i, brand in enumerate(brands, start=1):
        print(f'{i}) {brand.name}')
    brand = brands[select_item() - 1]
    print('Colors:')
    colors = [color for color in Color]
    for i, color in enumerate(colors, start=1):
        print(f'{i}) {color.name}')
    color = colors[select_item() - 1]
    owner = input('owner: ')
    database.insert_car(Car(number, brand, color, owner))


def change_entry_by_number_wrapper(database: CarDataBase) -> None:
    number = input('Enter car number: ')
    car = database.get_car_by_number(number)
    if not car:
        print('Car does not founded')
        press_enter_for_continue()
        return
    print(f'Car info: {car}')
    database.remove_car_by_number(number)
    try:
        insert_entry_wrapper(database)
    except RuntimeError as e:
        print(e)
        database.insert_car(car)


def get_info_by_number_wrapper(database: CarDataBase) -> None:
    number = input('Enter car number: ')
    car = database.get_car_by_number(number)
    if not car:
        print('Car does not found')
        press_enter_for_continue()
        return
    print(f'Car info: {car}')
    press_enter_for_continue()


def sort_cars_wrapper(database: CarDataBase) -> None:
    print('Sorts by:')
    attributes = ['brand', 'color', 'owner']
    for i, attribute in enumerate(attributes, start=1):
        print(f'{i}) {attribute}')
    database.sort_by_attribute(attributes[select_item() - 1])


def save_into_file_and_print_all_owner_cars_wrapper(database: CarDataBase) -> None:
    owners = sorted({car.owner for car in database.cars()})
    if len(owners) == 0:
        print('Any owner does not found')
        press_enter_for_continue()
        return
    for i, owner in enumerate(owners, start=1):
        print(f'{i}) {owner}')
    owner = owners[select_item() - 1]
    owner_cars = [car for car in database.cars() if car.owner == owner]
    print(f'The owner: {owner} cars: ')
    for owner_car in owner_cars:
        print(owner_car)
    filename = input('Enter filename for saving: ')
    new_database = CarDataBase(filename)
    new_database.root.clear()
    for owner_car in owner_cars:
        new_database.insert_car(owner_car)


class Item:
    def __init__(self, name: str, function):
        self.name = name
        self.function = function


def manage_car_data(filename: str) -> None:
    database = CarDataBase(filename)

    while True:
        os.system('cls')
        items = [Item(*name_and_function) for name_and_function in [
            ('remove entry (by number)', remove_entry_by_number_wrapper),
            ('insert entry', insert_entry_wrapper),
            ('change entry (by number)', change_entry_by_number_wrapper),
            ('get info (by number)', get_info_by_number_wrapper),
            ('sort automobiles', sort_cars_wrapper),
            ('save into file and print all owner cars', save_into_file_and_print_all_owner_cars_wrapper)
        ]]
        for i, item in enumerate(items, start=1):
            print(f'{i}) {item.name}')
        print(f'0) exit')
        item_number = select_item()
        if item_number == 0:
            return
        os.system('cls')
        items[item_number - 1].function(database)


def main():
    zip_directory_with_file_patterns_info('some_directory', 'a*')
    manage_car_data('cars_data.xml')


if __name__ == '__main__':
    main()
