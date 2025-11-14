import csv
import json
import urllib.request

def csv_reader(filename):
    config = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    key = row[0].strip()
                    value = row[1].strip()
                    config[key] = value
        return config
    except FileNotFoundError:
        print(f"Ошибка: Файл {filename} не найден!")
        return {}
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return {}


def error_handler(config):
    errors = []

    if 'package_name' not in config:
        errors.append("Отсутствует package_name")

    if 'repository_url' not in config:
        errors.append("Отсутствует repository_url")

    if 'repository_mode' not in config:
        errors.append("Отсутствует repository_mode")
    elif config['repository_mode'] not in ['local', 'remote']:
        errors.append("repository_mode должен быть 'local' или 'remote'")

    if 'tree_output' in config and config['tree_output'] not in ['true', 'false']:
        errors.append("tree_output должен быть 'true' или 'false'")

    if 'max_depth' in config:
        try:
            depth = int(config['max_depth'])
            if depth < 1:
                errors.append("max_depth должен быть больше 0")
        except:
            errors.append("max_depth должен быть числом")

    return errors


def print_config(config):
    print("\nВсе параметры конфигурации:")
    for key, value in config.items():
        print(f"{key}: {value}")


def get_npm_dependencies(package_name, version):
    try:
        # Формируем URL для запроса к npm registry
        url = f"https://registry.npmjs.org/{package_name}/{version}"
        print(f"Запрашиваем данные по URL: {url}")

        # Делаем HTTP запрос
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            package_info = json.loads(data)

            # Извлекаем зависимости
            dependencies = package_info.get('dependencies', {})

            return dependencies

    except urllib.error.HTTPError as e:
        print(f"Ошибка HTTP: {e.code} - {e.reason}")
        return {}
    except urllib.error.URLError as e:
        print(f"Ошибка URL: {e.reason}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e}")
        return {}
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return {}


def print_dependencies(dependencies):
    if not dependencies:
        print("Зависимости не найдены")
        return

    print("\nПрямые зависимости пакета:")
    for package, version in dependencies.items():
        print(f"  - {package}: {version}")
def main():
    filename = "config.csv"

    print(f"Читаем конфигурационный файл: {filename}")

    config = csv_reader(filename)

    if not config:
        return

    errors = error_handler(config)

    if errors:
        print("\nОшибки в конфигурации:")
        for error in errors:
            print(f" - {error}")
        return

    print_config(config)

    print("\n" + "=" * 50)
    package_name = config['package_name']
    version = config.get('package_version', 'latest')  # Если версия не указана, используем 'latest'

    print(f"Получаем зависимости для пакета: {package_name} версия: {version}")

    dependencies = get_npm_dependencies(package_name, version)

    # Выводим зависимости
    print_dependencies(dependencies)

if __name__ == "__main__":
    main()