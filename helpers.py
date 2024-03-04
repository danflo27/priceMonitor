from datetime import datetime
from dotenv import load_dotenv
import pytz 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def plot_differences(data_points, symbol):
    timestamps = [datetime.fromtimestamp(item['reported timestamp']) for item in data_points]
    differences = [item['difference'] for item in data_points]

    plt.figure(figsize=(10, 6))

    # Plotting the data
    plt.plot(timestamps, differences, marker='o', linestyle='-', color='blue')

    # Formatting the x-axis to show dates properly
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()  # Rotation for better readability

    # Adding labels and title
    plt.xlabel('Time')
    plt.ylabel('Difference')
    title = symbol + " report vs. actual price differences"
    plt.title(title)

    # Drawing a horizontal line at y=0 for reference
    plt.axhline(y=0, color='r', linestyle='--')

    plt.tight_layout()
    plt.savefig(str(symbol) + '_plot.png')

def find_max_difference(data_points):
    max_value = (max(item['absolute difference'] for item in data_points)).__round__(2)
    item_with_max_difference = max(data_points, key=lambda item: item['absolute difference'])
    timestamp = item_with_max_difference['dune timestamp']
    date_time = datetime.fromtimestamp(timestamp)
    date_time_eastern = date_time.astimezone(pytz.timezone('US/Eastern'))
    date_time_string = date_time_eastern.strftime('%Y-%m-%d %H:%M %Z')
    max_data_point = [(max_value, date_time_string, timestamp)]
    return max_data_point

def get_avg_time_between_reports(timestamps):
    if len(timestamps) > 1:
        timestamps.sort()
        time_differences = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        average_time_difference = sum(time_differences) / len(time_differences)
    else:
        average_time_difference = None  # No average if there's less than 2 timestamps
    return average_time_difference


def to_unix_time(datetime_str):
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f UTC')
    dt = dt.replace(tzinfo=pytz.UTC)
    return int(dt.timestamp())
