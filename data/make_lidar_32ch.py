import numpy as np, json
def generate_32_channel_lidar():
    lidar_data = []
    for channel in range(32):
        x = np.random.uniform(-50, 50, 1000)
        y = np.random.uniform(-50, 50, 1000)
        z = np.random.uniform(-3, 3, 1000)
        lidar_data.extend([(x[i], y[i], z[i], channel) for i in range(1000)])
    return lidar_data
with open('lidar_data_32ch.json', 'w') as f:
    json.dump(generate_32_channel_lidar(), f)
