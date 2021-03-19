import pandas as pd
from glob import glob
import os
from tqdm import tqdm

instruments = ['USD000000TOD', 'USD000UTSTOM', 'EUR_RUB__TOD', 'EUR_RUB__TOM', 'EURUSD000TOM', 'EURUSD000TOD']

# for inst in instruments:
# 	os.mkdir(f'fx_separated/{inst}')


for ol_fn in tqdm(glob('./*/Order*')):
	ol_df = pd.read_csv(ol_fn)
	for inst in instruments:
		inst_df = ol_df[ol_df['SECCODE'] == inst]
		inst_df.to_csv(f'fx_separated/{inst}/{ol_fn.split("/")[-1]}')