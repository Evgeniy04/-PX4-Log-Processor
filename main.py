import os
import pandas as pd
from pyulog import ulog2csv
import matplotlib.pyplot as plt

def remove_trash(output_dir, file_path):
    battery_status = os.path.join(output_dir, f'{os.path.basename(file_path).replace(".ulg", "")}_battery_status_0.csv')
    vehicle_air_data = os.path.join(output_dir, f'{os.path.basename(file_path).replace(".ulg", "")}_vehicle_air_data_0.csv')
    merged_log = os.path.join(output_dir, 'merged_log_data.xlsx')

    if os.path.exists(merged_log) and os.path.exists(vehicle_air_data) and os.path.exists(battery_status):
        os.remove(merged_log)
        os.remove(vehicle_air_data)
        os.remove(battery_status)
    else:
        raise Exception("!!!Какой-то из файлов не создан!!!")

def colorbar_and_plot(output_dir):
    # Чтение объединенного файла для построения графика
    output_file = os.path.join(output_dir, 'flight_data_graph.png')
    file_path = os.path.join(output_dir, 'merged_log_data.xlsx')
    merged_df = pd.read_excel(file_path)

    # Cоздание цветовой шкалы
    styled_df = merged_df.style.background_gradient(subset=['voltage_v', 'current_a', 'baro_alt_meter'], cmap='coolwarm')

    # Экспорт в Excel с сохранением стиля
    styled_df.to_excel(os.path.join(output_dir, "styled_output.xlsx"), engine='openpyxl', index=False)

    # Построение графика
    plt.figure(figsize=(10, 6))

    # График для voltage_v
    plt.plot(merged_df['timestamp'], merged_df['voltage_v'], label='Voltage (V)', color='blue')

    # График для current_a
    plt.plot(merged_df['timestamp'], merged_df['current_a'], label='Current (A)', color='red')

    # График для baro_alt_meter
    plt.plot(merged_df['timestamp'], merged_df['baro_alt_meter'], label='Baro Altitude (meters)', color='green')

    # Настройки графика
    plt.title('Flight Data Overview')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Values')
    plt.legend()
    plt.grid(True)

    # Сохранение графика
    plt.savefig(output_file)
    plt.close()

def merge(output_dir, file_path):
    output_file = os.path.join(output_dir, 'merged_log_data.xlsx')
    # Чтение первого файла (battery_status)
    battery_df = pd.read_csv(os.path.join(output_dir, f'{os.path.basename(file_path).replace(".ulg", "")}_battery_status_0.csv'))

    # Преобразование timestamp в формат времени с начала полета
    battery_df['timestamp'] = (battery_df['timestamp'] - battery_df['timestamp'].min()) / 1e6  # Преобразование в секунды

    # Выбор нужных столбцов
    battery_df = battery_df[['timestamp', 'voltage_v', 'current_a']]

    # Чтение второго файла (vehicle_air_data)
    air_data_df = pd.read_csv(os.path.join(output_dir, f'{os.path.basename(file_path).replace(".ulg", "")}_vehicle_air_data_0.csv'))

    # Преобразование timestamp и выбор нужных столбцов
    air_data_df['timestamp'] = (air_data_df['timestamp'] - air_data_df['timestamp'].min()) / 1e6  # Преобразование в секунды
    air_data_df = air_data_df[['timestamp', 'baro_alt_meter']]

    # Объединение двух таблиц по времени (timestamp) с использованием метода merge_asof для приблизительного сопоставления
    merged_df = pd.merge_asof(battery_df.sort_values('timestamp'), air_data_df.sort_values('timestamp'), on='timestamp', direction='nearest')

    # Сохранение в формате Excel
    merged_df.to_excel(output_file, index=False)
    

def process_ulg_file(file_path):
    """
    Функция для обработки .ulg файла и сохранения результата
    """
    # Имя выходного файла (с тем же именем, но расширение .csv)
    output_dir = os.path.dirname(file_path)

    # Чтение .ulg файла
    ulog2csv.convert_ulog2csv(file_path,
                        messages="battery_status,vehicle_air_data",       # or None for all messages
                        output=output_dir,                                        # specify your output directory
                        delimiter=",",                                    # your desired delimiter
                        time_s=0,                                         # start time in seconds (e.g., 0)
                        time_e=None)                                      # end time in seconds (e.g., None for all)
    
    merge(output_dir, file_path)
    colorbar_and_plot(output_dir)
    remove_trash(output_dir, file_path)


def find_and_process_ulg_files(start_dir):
    """
    Функция для рекурсивного поиска .ulg файлов и их обработки
    """
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith('.ulg'):
                file_path = os.path.join(root, file)
                print(f"Найден .ulg файл: {file_path}")
                process_ulg_file(file_path)


if __name__ == "__main__":
    # Укажите начальную директорию для поиска
    start_directory = "C:\\yourdirectory"  # Замените на нужную директорию
    find_and_process_ulg_files(start_directory)
