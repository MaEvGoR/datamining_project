from Spectrum import Spectrum
import numpy as np
import datetime


class OrderBookSpectrum():

    # def __init__(self, tradelog_labels):
    def __init__(self, price_step, spectrum_filename):
        self.ob_df = {}
        self.collisions = 0
        self.spectrum = Spectrum(price_step)
        self.spectrum_file = open(spectrum_filename, "w+")
        self.start_time = None
        # self.order_book_spectrum = open("my_order_book_spectrum.txt", "w") # Add name for particular order book
        # self.price_step = 0.0025

    def write_to_file(self, time):
        buy_spect = np.array(self.spectrum.spectrum_buy)
        sell_spect = np.array(self.spectrum.spectrum_sell)
        if buy_spect.sum() > 0 and sell_spect.sum() > 0:
            buy_norm = buy_spect / buy_spect.sum()
            sell_norm = sell_spect / sell_spect.sum()
            buy = ', '.join([str(i) for i in buy_norm])
            sell = ', '.join([str(i) for i in sell_norm])
            to_write = str(time) + ', ' + sell + ', ' + buy + '\n'
            # print(to_write)
            self.spectrum_file.write(to_write)

    def post_order(self, orderno, volume, buysell, price, time):
        # time segment check



        self.ob_df[orderno] = {'volume': volume, 'buysell': buysell, 'price': price, 'time': time}
        if buysell == 'B':
            self.spectrum.new_buy_order(price, volume)
        else:
            self.spectrum.new_sell_order(price, volume)

    def revoke_order(self, orderno, volume, buysell, price, time):

        if orderno in self.ob_df:
            if volume == self.ob_df[orderno]['volume']:
                self.ob_df.pop(orderno, None)
                if buysell == 'B':
                    self.spectrum.delete_buy_order(price, volume)
                else:
                    self.spectrum.delete_sell_order(price, volume)
            elif volume < self.ob_df[orderno]['volume']:
                self.ob_df[orderno]['volume'] -= volume
                if buysell == 'B':
                    self.spectrum.delete_buy_order(price, volume)
                else:
                    self.spectrum.delete_sell_order(price, volume)
            else:
                print('\nException: not possible volume for match: \n', orderno)
                self.collisions += 1
                self.delete_collision(order)
        else:
            print('\nException: orderno does not exist: \n', orderno)
            self.collisions += 1
            self.delete_collision(order)

    def match_order(self, orderno, volume, buysell, price, time):

        if orderno in self.ob_df:
            if volume == self.ob_df[orderno]['volume']:
                self.ob_df.pop(orderno, None)
                if buysell == 'B':
                    self.spectrum.delete_buy_order(price, volume)
                else:
                    self.spectrum.delete_sell_order(price, volume)
            elif volume < self.ob_df[orderno]['volume']:
                self.ob_df[orderno]['volume'] -= volume
                if buysell == 'B':
                    self.spectrum.delete_buy_order(price, volume)
                else:
                    self.spectrum.delete_sell_order(price, volume)
            else:
                print('\nException: not possible volume for match: \n', orderno)
                self.collisions += 1
        else:
            print('\nException: orderno does not exist: \n', orderno)
            self.collisions += 1

    def delete_collision(self, orderno):
        print('Delete collisioned orders with ORDERNO: ' + orderno)
        self.ob_df.pop(orderno, None)
        print('Current number of collisions: {}\n'.format(self.collisions))

    def new_order(self, action, orderno, volume, buysell, price, time):
        if not self.start_time:
            self.start_time = datetime.datetime.strptime(time, "%H%M%S%f")

        new_time = datetime.datetime.strptime(time, "%H%M%S%f")

        time_diff = new_time - self.start_time

        if self.start_time == new_time:
            exit(0)

        if time_diff.microseconds == 0:
            print('T = 1')

        if time_diff.microseconds == 0 and time_diff.seconds % 5 == 0:
            print('T = 5')

        if time_diff.microseconds == 0 and time_diff.seconds % 15 == 0:
            print('T = 15')

        if time_diff.microseconds == 0 and time_diff.seconds % 30 == 0:
            print('T = 30')

        if time_diff.microseconds == 0 and time_diff.seconds == 0:
            print('T = 60')

        if action == 1:
            self.post_order(orderno, volume, buysell, price, time)
        elif action == 0:
            self.revoke_order(orderno, volume, buysell, price, time)
        elif action == 2:
            self.match_order(orderno, volume, buysell, price, time)
        else:
            self.collisions += 1
        self.write_to_file(time)