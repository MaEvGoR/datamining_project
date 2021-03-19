from MaximOrderBookSpectrum import OrderBookSpectrum
import pandas as pd


def generate_orderbook(orderlog_path, output_path, instrument, price_step, filename):
    df = pd.read_csv(orderlog_path)
    actions = df['ACTION'].to_numpy()
    ordernos = df['ORDERNO'].to_numpy()
    volumes = df['VOLUME'].to_numpy()
    buysells = df['BUYSELL'].to_numpy()
    prices = df['PRICE'].to_numpy()
    times = df['TIME'].to_numpy()

    ob = OrderBookSpectrum(price_step, filename)

    for i in range(len(df)):
        ob.new_order(actions[i], ordernos[i], volumes[i], buysells[i], prices[i], times[i])

    #     ob_file = open(output_path, "w+")
    #     ob_file.write('time, orderno, buysell, price, volume\n')
    #     for k, v in ob.ob_df.items():
    #         to_write = str(v['time']) + ', ' + str(k) + ', ' + str(v['buysell']) + ', ' + str(v['price']) + ', ' + str(v['volume']) + '\n'
    #         ob_file.write(to_write)

    return ob
