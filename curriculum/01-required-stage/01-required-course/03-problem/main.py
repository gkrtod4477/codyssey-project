import os


def clear_artifacts_directory(artifacts_dir):
    # 실행할 때마다 artifacts 폴더 안의 기존 파일을 모두 삭제
    try:
        if not os.path.exists(artifacts_dir):
            os.makedirs(artifacts_dir)

        for file_name in os.listdir(artifacts_dir):
            file_path = os.path.join(artifacts_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except OSError as error:
        print(f"artifacts 폴더 정리 중 오류가 발생했습니다: {error}")


def read_csv_text(csv_path):
    # CSV 원본 내용을 문자열로 읽어서 반환
    try:
        with open(csv_path, "r", encoding="utf-8") as file:
            return file.read()
    except OSError as error:
        print(f"CSV 파일을 읽는 중 오류가 발생했습니다: {error}")
        return None


def convert_csv_text_to_list(csv_text):
    # CSV 문자열을 Python의 2차원 리스트로 변환
    rows = csv_text.splitlines()
    inventory_list = []

    for row in rows:
        inventory_list.append(row.split(","))

    return inventory_list


def sort_by_flammability(inventory_list):
    # 헤더를 제외한 적재 화물 목록을 인화성 지수가 높은 순으로 정렬해서 반환
    header = inventory_list[0]
    cargo_list = inventory_list[1:]
    valid_cargo_list = []
    invalid_cargo_list = []

    for item in cargo_list:
        try:
            flammability = float(item[4])
            valid_cargo_list.append((flammability, item))
        except (ValueError, IndexError):
            print(f"인화성 지수를 처리할 수 없어 정렬에서 예외 처리된 항목: {item}")
            invalid_cargo_list.append(item)

    valid_cargo_list.sort(key=lambda element: element[0], reverse=True)
    sorted_cargo_list = [item for _, item in valid_cargo_list]
    return [header] + sorted_cargo_list + invalid_cargo_list


def filter_dangerous_items(sorted_inventory_list, threshold):
    # 인화성 지수가 기준값 이상인 화물만 별도로 추리고 반환
    header = sorted_inventory_list[0]
    cargo_list = sorted_inventory_list[1:]
    dangerous_items = []

    for item in cargo_list:
        try:
            if float(item[4]) >= threshold:
                dangerous_items.append(item)
        except (ValueError, IndexError):
            continue

    return [header] + dangerous_items


def save_csv(csv_path, rows):
    # 위험 화물 목록을 CSV 파일 형식의 문자열로 저장
    try:
        with open(csv_path, "w", encoding="utf-8") as file:
            for row in rows:
                file.write(",".join(row) + "\n")
        return True
    except OSError as error:
        print(f"CSV 파일을 저장하는 중 오류가 발생했습니다: {error}")
        return False


def save_binary(binary_path, rows):
    # 인화성 순서로 정렬된 목록을 이진 파일로 저장
    try:
        binary_text = ""
        for row in rows:
            binary_text += ",".join(row) + "\n"

        with open(binary_path, "wb") as file:
            file.write(binary_text.encode("utf-8"))
        return True
    except OSError as error:
        print(f"이진 파일을 저장하는 중 오류가 발생했습니다: {error}")
        return False


def read_binary(binary_path):
    # 저장된 이진 파일을 다시 읽어서 문자열로 반환
    try:
        with open(binary_path, "rb") as file:
            return file.read().decode("utf-8")
    except OSError as error:
        print(f"이진 파일을 읽는 중 오류가 발생했습니다: {error}")
        return None


def print_rows(title, rows):
    print(title)
    for row in rows:
        print(row)
    print()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "provided-files", "Mars_Base_Inventory_List.csv")
    artifacts_dir = os.path.join(base_dir, "artifacts")
    danger_csv_path = os.path.join(artifacts_dir, "Mars_Base_Inventory_danger.csv")
    binary_path = os.path.join(artifacts_dir, "Mars_Base_Inventory_List.bin")

    clear_artifacts_directory(artifacts_dir)

    csv_text = read_csv_text(csv_path)
    if csv_text is None:
        return

    # 1. CSV 원본 내용을 그대로 출력
    print("CSV 원본 내용")
    print(csv_text)

    # 2. CSV 내용을 리스트 객체로 변환하고 출력
    inventory_list = convert_csv_text_to_list(csv_text)
    print_rows("리스트로 변환한 내용", inventory_list)

    # 3. 적재 화물 목록을 인화성 지수가 높은 순으로 정렬
    sorted_inventory_list = sort_by_flammability(inventory_list)
    print_rows("인화성 지수가 높은 순으로 정렬한 내용", sorted_inventory_list)

    # 4. 인화성 지수가 0.7 이상인 목록만 별도로 출력
    dangerous_inventory_list = filter_dangerous_items(sorted_inventory_list, 0.7)
    print_rows("인화성 지수 0.7 이상 목록", dangerous_inventory_list)

    # 5. 인화성 지수가 0.7 이상인 목록을 별도의 CSV 파일로 저장
    if save_csv(danger_csv_path, dangerous_inventory_list):
        print(f"위험 화물 CSV 파일이 저장되었습니다: {danger_csv_path}")

    # 6. 인화성 순서로 정렬된 목록을 이진 파일로 저장
    if save_binary(binary_path, sorted_inventory_list):
        print(f"정렬된 목록 이진 파일이 저장되었습니다: {binary_path}")

    # 7. 저장된 이진 파일을 다시 읽어 들여서 화면에 출력
    binary_text = read_binary(binary_path)
    if binary_text is not None:
        print("이진 파일에서 다시 읽은 내용")
        print(binary_text)



if __name__ == "__main__":
    main()
