import csv
import json
import urllib.request
from collections import deque


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
    elif config['repository_mode'] not in ['local', 'remote', 'test']:
        errors.append("repository_mode должен быть 'local', 'remote' или 'test'")
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
        url = f"https://registry.npmjs.org/{package_name}/{version}"
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            package_info = json.loads(data)
            return package_info.get('dependencies', {})
    except Exception as e:
        print(f"Ошибка получения зависимостей для {package_name}: {e}")
        return {}


def load_test_repository(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка загрузки тестового репозитория: {e}")
        return {}


def build_dependency_graph(start_package, get_deps_func, max_depth):
    graph = {}
    visited = set()
    queue = deque([(start_package, 0)])

    while queue:
        current_package, depth = queue.popleft()

        if current_package in visited or depth >= max_depth:
            continue

        visited.add(current_package)
        dependencies = get_deps_func(current_package)
        graph[current_package] = list(dependencies.keys())

        for dep in dependencies:
            if dep not in visited:
                queue.append((dep, depth + 1))

    return graph


def detect_cycles(graph):
    cycles = []

    def dfs(package, path):
        if package in path:
            cycle = path[path.index(package):] + [package]
            if cycle not in cycles:
                cycles.append(cycle)
            return
        path.append(package)
        for dep in graph.get(package, []):
            dfs(dep, path.copy())

    for package in graph:
        dfs(package, [])

    return cycles


def print_dependency_tree(graph, start_package):
    print(f"\nДерево зависимостей:")

    queue = deque([(start_package, 0)])

    while queue:
        current_package, level = queue.popleft()

        indent = "  " * level
        print(f"{indent} {current_package}")

        for dep in graph.get(current_package, []):
            queue.append((dep, level + 1))

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

    package_name = config['package_name']
    version = config.get('package_version', 'latest')
    max_depth = int(config.get('max_depth', 3))
    repository_mode = config['repository_mode']

    print(f"\nРежим работы: {repository_mode}")

    if repository_mode == 'test':
        test_file = config['repository_url']
        print(f"Загружаем тестовый репозиторий из: {test_file}")
        test_repo = load_test_repository(test_file)

        def get_test_dependencies(package):
            return {dep: "" for dep in test_repo.get(package, [])}

        get_deps_func = get_test_dependencies

    else:
        def get_npm_deps(package):
            if package == package_name:
                return get_npm_dependencies(package, version)
            else:
                return get_npm_dependencies(package, 'latest')

        get_deps_func = get_npm_deps

    print(f"\nСтроим граф зависимостей (BFS, макс. глубина: {max_depth})...")
    graph = build_dependency_graph(package_name, get_deps_func, max_depth)

    if config.get('tree_output') == 'true':
        print_dependency_tree(graph, package_name)
    else:
        print(f"\nГраф зависимостей:")
        for package, deps in graph.items():
            print(f"  {package} -> {deps}")

    cycles = detect_cycles(graph)
    if cycles:
        print(f"\n⚠️  Обнаружены циклические зависимости:")
        for cycle in cycles:
            print(f"  {' → '.join(cycle)}")
    else:
        print(f"\n✅ Циклические зависимости не обнаружены")


if __name__ == "__main__":
    main()