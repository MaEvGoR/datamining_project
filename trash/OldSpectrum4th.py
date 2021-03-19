import numpy as np
import pandas as pd
from glob import glob
import gzip
import shutil
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import math

class Spectrum:
    def __init__(self, price_step):
        self.price_step = price_step
        self.buy_bins = []
        self.all_buy_bins = []
        self.all_buy_volumes = []
        self.all_sell_bins = []
        self.all_sell_volumes = []
        self.sell_bins = []
        self.best_sell = -1
        self.best_buy = -1
        self.buy_volumes = [0 for i in range(50)]
        self.sell_volumes = [0 for i in range(50)]
        self.spectrum_sell_bins = []
        self.spectrum_buy_bins = []
        self.spectrum_sell = [0 for i in range(10)]
        self.spectrum_buy = [0 for i in range(10)]

    def insert_to_buy(self, price, volume):
        max_price = self.all_buy_bins[0]
        # new one is greater than the currently recorded maximum
        if price > max_price:
            dist = math.ceil((price - max_price) / self.price_step)
            self.all_buy_bins = [i for i in np.arange(price, max_price, -self.price_step)] + self.all_buy_bins
            self.all_buy_volumes = [0 for i in range(len(self.all_buy_bins) - len(self.all_buy_volumes))] + self.all_buy_volumes
            self.all_buy_volumes[0] += volume
            return 0
        else:
            idx = math.ceil((max_price - price) / self.price_step)
            if idx < len(self.all_buy_bins):
                self.all_buy_volumes[idx] += volume
                return idx
            else:
                dist = idx - len(self.all_buy_bins) + 1
                self.all_buy_bins = self.all_buy_bins + [i for i in np.arange(self.all_buy_bins[-1] - self.price_step, price - 1, -self.price_step)]
                self.all_buy_volumes = self.all_buy_volumes + [0 for i in range(len(self.all_buy_bins) - len(self.all_buy_volumes))]
                self.all_buy_volumes[idx] += volume
                return idx

    def insert_to_sell(self, price, volume):
        min_price = self.all_sell_bins[0]
        # new one is less than the currently recorded minimum
        if price < min_price:
            dist = math.ceil((min_price - price) / self.price_step)
            self.all_sell_bins = [i for i in np.arange(price, min_price, self.price_step)] + self.all_sell_bins
            self.all_sell_volumes = [0 for i in range(len(self.all_sell_bins) - len(self.all_sell_volumes))] + self.all_sell_volumes
            self.all_sell_volumes[0] += volume
            return 0
        else:
            idx = math.ceil((price - min_price) / self.price_step)
            if idx < len(self.all_sell_bins):
                self.all_sell_volumes[idx] += volume
                return idx
            else:
                dist = idx - len(self.all_sell_bins) + 1
                self.all_sell_bins = self.all_sell_bins + [i for i in np.arange(self.all_sell_bins[-1] + self.price_step, price + 1, self.price_step)]
                self.all_sell_volumes = self.all_sell_volumes + [0 for i in range(len(self.all_sell_bins) - len(self.all_sell_volumes))]
                self.all_sell_volumes[idx] += volume
                return idx

    def delete_from_buy(self, price, volume):
        max_price = self.all_buy_bins[0]
        idx = math.ceil((max_price - price) / self.price_step)
        if 0 <= idx < len(self.all_buy_bins):
            if volume < self.all_buy_volumes[idx]:
                self.all_buy_volumes[idx] -= volume
                return idx
            # find first non-zero element
            else:
                self.all_buy_volumes[idx] = 0
                while self.all_buy_volumes[idx] == 0:
                    if (idx == len(self.all_buy_volumes) - 1):
                        break
                    idx += 1
                return idx
        else:
            return -1

    def delete_from_sell(self, price, volume):
        min_price = self.all_sell_bins[0]
        idx = math.ceil((price - min_price) / self.price_step)
        if 0 <= idx < len(self.all_sell_bins):
            if volume < self.all_sell_volumes[idx]:
                self.all_sell_volumes[idx] -= volume
                return idx
            # find first non-zero element
            else:
                self.all_sell_volumes[idx] = 0
                while self.all_sell_volumes[idx] == 0:
                    if (idx == len(self.all_sell_volumes) - 1):
                        break
                    idx += 1
                return idx
        else:
            return -1

    def find_idx_sell(self, price):
        k = math.ceil((price - self.best_sell) / self.price_step)
        if k == 50:
            k = 49
        return int(k)

    def find_idx_buy(self, price):
        k = math.ceil((self.best_buy - price) / self.price_step)
        if k == 50:
            k = 49
        return int(k)

    def find_idx_spectrum_sell(self, price):
        k = math.ceil((price - self.best_sell) / self.price_step) // 5
        if k == 10:
            k = 9
        return k

    def find_idx_spectrum_buy(self, price):
        k = math.ceil((self.best_buy - price) / self.price_step) // 5
        if k == 10:
            k = 9
        return k

    def recalc_spectrum_sell(self):
        self.spectrum_sell_bins = [self.sell_bins[i] for i in range(0, 50, 5)]
        self.spectrum_sell = [sum(self.sell_volumes[i:i+5]) for i in range(0, 50, 5)]
        
    def recalc_spectrum_buy(self):
        self.spectrum_buy_bins = [self.buy_bins[i] for i in range(0, 50, 5)]
        self.spectrum_buy = [sum(self.buy_volumes[i:i+5]) for i in range(0, 50, 5)]

    def new_sell_order(self, price, volume):
        # no sell orders recorded yet
        if self.best_sell == -1:
            self.best_sell = price
            max_sell = self.best_sell + 50 * self.price_step
            self.sell_bins = [p for p in np.arange(self.best_sell, max_sell, self.price_step)]
            self.spectrum_sell_bins = [p for p in np.arange(self.best_sell, max_sell, self.price_step * 5)]
            self.sell_volumes[0] = volume
            self.spectrum_sell[0] = volume
            self.all_sell_bins = self.sell_bins.copy()
            self.all_sell_volumes = self.sell_volumes.copy()
        else:
            # sell order falls somewhere in the existing bins
            if self.best_sell <= price < self.best_sell + 50 * self.price_step:
                idx = self.find_idx_sell(price)
                if idx == 50:
                    idx = 49
                self.sell_volumes[idx] += volume
                spect_idx = self.find_idx_spectrum_sell(price)
                self.spectrum_sell[spect_idx] += volume
                _ = self.insert_to_sell(price, volume)
            else:
                # found new best, update everything
                if self.best_sell > price:
                    idx = self.insert_to_sell(price, volume)
                    self.best_sell = price
                    if idx + 50 < len(self.all_sell_bins):
                        self.sell_bins = self.all_sell_bins[idx:idx+50]
                        self.sell_volumes = self.all_sell_volumes[idx:idx+50]
                    else:
                        self.sell_bins = [p for p in np.arange(self.best_sell, self.best_sell + 50 * self.price_step, self.price_step)]
                        self.sell_volumes = self.all_sell_volumes[idx:] + [0 for i in range(50 - len(self.all_sell_volumes) + idx)]
                    self.recalc_spectrum_sell()
                # save for the later usage
                else:
                    _ = self.insert_to_sell(price, volume)
                    
    def new_buy_order(self, price, volume):
        # no buy orders recorded yet
        if self.best_buy == -1:
            self.best_buy = price
            min_buy = self.best_buy - 50 * self.price_step
            self.buy_bins = [p for p in np.arange(self.best_buy, min_buy, -self.price_step)]
            self.spectrum_buy_bins = [p for p in np.arange(self.best_buy, min_buy, -self.price_step * 5)]
            self.buy_volumes[0] = volume
            self.spectrum_buy[0] = volume
            self.all_buy_bins = self.buy_bins.copy()
            self.all_buy_volumes = self.buy_volumes.copy()
        else:
            # buy order falls somewhere in the existing bins
            if self.best_buy >= price > self.best_buy - 50 * self.price_step:
                idx = self.find_idx_buy(price)
                if idx == 50:
                    idx = 49
                self.buy_volumes[idx] += volume
                spect_idx = self.find_idx_spectrum_buy(price)
                self.spectrum_buy[spect_idx] += volume
                _ = self.insert_to_buy(price, volume)
            else:
                # found new best, update everything
                if self.best_buy < price:
                    idx = self.insert_to_buy(price, volume)
                    self.best_buy = price
                    if idx + 50 < len(self.all_buy_bins):
                        self.buy_bins = self.all_buy_bins[idx:idx+50]
                        self.buy_volumes = self.all_buy_volumes[idx:idx+50]
                    else:
                        self.buy_bins = [p for p in np.arange(self.best_buy, self.best_buy - 50 * self.price_step, -self.price_step)]
                        self.buy_volumes = self.all_buy_volumes[idx:] + [0 for i in range(50 - len(self.all_buy_volumes) + idx)]
                    self.recalc_spectrum_buy()
                # save for the later usage
                else:
                    _ = self.insert_to_buy(price, volume)
                    
    def delete_sell_order(self, price, volume):
        # does not remove current best
        if self.best_sell + 50 * self.price_step > price > self.best_sell or price == self.best_sell and volume < self.sell_volumes[0]:
            idx = self.find_idx_sell(price)
            self.sell_volumes[idx] = max(0, self.sell_volumes[idx] - volume)
            spect_idx = self.find_idx_spectrum_sell(price)
            self.spectrum_sell[spect_idx] = max(0, self.spectrum_sell[spect_idx] - volume)
        else:
            # if removes current best
            if price == self.best_sell and volume >= self.sell_volumes[0]:
                idx = self.delete_from_sell(price, volume)
                self.best_sell = self.all_sell_bins[idx]
                if idx + 50 < len(self.all_sell_bins):
                    self.sell_bins = self.all_sell_bins[idx:idx+50]
                    self.sell_volumes = self.all_sell_volumes[idx:idx+50]
                else:
                    self.sell_bins = [p for p in np.arange(self.best_sell, self.best_sell + 50 * self.price_step, self.price_step)]
                    self.sell_volumes = self.all_sell_volumes[idx:] + [0 for i in range(50 - len(self.all_sell_volumes) + idx)]
                self.recalc_spectrum_sell()
            # if does not fall in 50 steps
            elif price > self.best_sell + 50 * self.price_step:
                _ = self.delete_from_sell(price, volume)
                
    def delete_buy_order(self, price, volume):
        # does not remove current best
        if self.best_buy - 50 * self.price_step < price < self.best_buy or price == self.best_buy and volume < self.buy_volumes[0]:
            idx = self.find_idx_buy(price)
            self.buy_volumes[idx] = max(0, self.buy_volumes[idx] - volume)
            spect_idx = self.find_idx_spectrum_buy(price)
            self.spectrum_buy[spect_idx] = max(0, self.spectrum_buy[spect_idx] - volume)
        else:
            # if removes current best
            if price == self.best_buy and volume >= self.buy_volumes[0]:
                idx = self.delete_from_buy(price, volume)
                self.best_buy = self.all_buy_bins[idx]
                if idx + 50 < len(self.all_buy_bins):
                    self.buy_bins = self.all_buy_bins[idx:idx+50]
                    self.buy_volumes = self.all_buy_volumes[idx:idx+50]
                else:
                    self.buy_bins = [p for p in np.arange(self.best_buy, self.best_buy - 50 * self.price_step, -self.price_step)]
                    self.buy_volumes = self.all_buy_volumes[idx:] + [0 for i in range(50 - len(self.all_buy_volumes) + idx)]
                self.recalc_spectrum_buy()
            # if does not fall in 50 steps
            elif price > self.best_buy + 50 * self.price_step:
                _ = self.delete_from_buy(price, volume)
