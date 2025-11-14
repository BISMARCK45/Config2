import csv


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


if __name__ == "__main__":
    main()