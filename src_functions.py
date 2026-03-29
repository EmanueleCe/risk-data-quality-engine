import pandas as pd
import numpy as np

def cleaning(df):
    df = df.copy()
    equity_spread = 0.0015
    bond_spread = 0.0008
    commodity_spread = 0.001
    fx_spread = 0.0002

    df['asset_class'] = np.select([(df['asset'] == "SPY") , (df['asset'] == "AAPL") , (df['asset'] == "TLT"), (df['asset'] == "GLD") , (df['asset'] == "EURUSD=X")], ['Equity ETF', 'Equity', 'Fixed Income', 'Commodity', 'FX'], default= 'sth wrong')
    df['ccy'] = 'USD'
    df['fx_rate'] = float(1)

    # Bid, Ask and Spread
    choice_spread = (round((df['close'] * equity_spread), 5), round((df['close'] * bond_spread),5), round((df['close'] * commodity_spread),5), round((df['close'] * fx_spread),5))
    df['spread'] = np.select([((df['asset'] == "SPY") | (df['asset'] == "AAPL")) , (df['asset'] == "TLT") , (df['asset'] == "GLD") , (df['asset'] == "EURUSD=X")], choice_spread, default= float(0)).astype(float)
    df['bid'] = df['close'] - (df['spread']/2)
    df['ask'] = df['close'] + (df['spread']/2)

    # source creation
    df['source'] = np.select([((df['asset'] == "SPY") | (df['asset'] == "AAPL")) , ((df['asset'] == "TLT") | (df['asset'] == "GLD")), (df['asset'] == "EURUSD=X")], ['Bloomberg', 'Reuters', 'Internal'],default= 'sth wrong')
    
    df['date'] = pd.to_datetime(df['date'])
    df['week_day'] = df['date'].dt.day_name()
    df['business_day'] = np.where (df['week_day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']), True, False)

    return df

def inject_data_quality_issues(df):
    df = df.copy()
    np.random.seed(42)

    # ------------------------ # 
    def inject_missing_by_asset(dataframe, asset, column, pct_missing):
        idx = dataframe[dataframe['asset'] == asset].index
        n_missing = int(len(idx) * pct_missing)
        if n_missing > 0:
            chosen = np.random.choice(idx, size=n_missing, replace=False)
            dataframe.loc[chosen, column] = np.nan

    inject_missing_by_asset(df, 'AAPL', 'close', 0.05)
    inject_missing_by_asset(df, 'GLD',  'close', 0.07)

    inject_missing_by_asset(df, 'AAPL', 'volume', 0.40)   
    inject_missing_by_asset(df, 'GLD',  'volume', 0.28)   
    inject_missing_by_asset(df, 'SPY',  'volume', 0.08)

    inject_missing_by_asset(df, 'GLD',  'source', 0.55)  
    inject_missing_by_asset(df, 'AAPL', 'source', 0.30)   
    inject_missing_by_asset(df, 'TLT',  'source', 0.08)

    inject_missing_by_asset(df, 'SPY',  'bid', 0.35)      
    inject_missing_by_asset(df, 'GLD',  'bid', 0.18)
    inject_missing_by_asset(df, 'AAPL', 'bid', 0.10)

    inject_missing_by_asset(df, 'TLT',  'ask', 0.30)    
    inject_missing_by_asset(df, 'SPY',  'ask', 0.22)
    inject_missing_by_asset(df, 'AAPL', 'ask', 0.10)

    # -------------------------
    # 2) OUTLIERS ON CLOSE

    idx_close_valid = df[df['close'].notna()].index
    idx_outliers = np.random.choice(idx_close_valid, size=int(0.01 * len(idx_close_valid)), replace=False)

    half = len(idx_outliers) // 2
    df.loc[idx_outliers[:half], 'close'] *= 1.8
    df.loc[idx_outliers[half:], 'close'] *= 0.5

    # -------------------------
    # 3) STALE PRICES

    for asset in ['TLT', 'GLD', 'SPY']:
        asset_idx = df[(df['asset'] == asset) & (df['close'].notna())].index.tolist()

        if len(asset_idx) > 15:
            for _ in range(2):  # two stale blocks per selected asset
                start_pos = np.random.randint(0, len(asset_idx) - 4)
                stale_idx = asset_idx[start_pos:start_pos + 4]
                stale_value = df.loc[stale_idx[0], 'close']
                df.loc[stale_idx, 'close'] = stale_value

    # -------------------------
    # 4) BID / ASK INCONSISTENCIES

    valid_two_sided_idx = df[df['bid'].notna() & df['ask'].notna() & df['close'].notna()].index
    idx_bad_spread = np.random.choice(valid_two_sided_idx, size=max(5, int(0.015 * len(valid_two_sided_idx))), replace=False)

    df.loc[idx_bad_spread, 'bid'] = df.loc[idx_bad_spread, 'close'] * 1.01
    df.loc[idx_bad_spread, 'ask'] = df.loc[idx_bad_spread, 'close'] * 0.99

    df['spread'] = df['ask'] - df['bid']

    return df

def completeness (df):
    df = df.copy()

    # creation scope for completeness calculation - several conditions
    df['source_cond'] = np.where((df['open'].notna() | df['high'].notna() | df['low'].notna() | df['close'].notna() | df['adj_close'].notna()), 'YES', 'NO')
    df['fx_cond'] = np.where(((df['ccy'].notna()) & (df['close'].notna())), 'YES', 'NO')
    df['volume_cond'] = np.where((df['asset_class'] != 'FX') & (df['close'].notna()), 'YES', 'NO')
    df['bid_ask_cond'] = np.where((df['source'].notna()) & (df['close'].notna()), 'YES', 'NO')
    df['spread_cond'] = np.where((df['ask'].notna()) & (df['bid'].notna()), 'YES', 'NO')

    # completeness calculations
    date_completeness_check = pd.DataFrame(df.groupby('asset')['date'].count() / df.groupby('asset')['date'].size()) #just check completeness: tot
    close_completeness_check = pd.DataFrame(df.groupby('asset')['close'].count() / df.groupby('asset')['close'].size())
    ccy_completeness_check = pd.DataFrame(df.groupby('asset')['ccy'].count() / df.groupby('asset')['ccy'].size())
    source_completeness_check = pd.DataFrame(df[df['source_cond'] == 'YES'].groupby('asset')['source'].count() / df[df['source_cond'] == 'YES'].groupby('asset')['source'].size())
    fx_completeness_check = pd.DataFrame(df[df['fx_cond'] == 'YES']).groupby('asset')['fx_rate'].count() / (df[df['fx_cond'] == 'YES']).groupby('asset')['fx_rate'].size() 
    volume_completeness_check = pd.DataFrame(df[df['volume_cond'] == 'YES']).groupby('asset')['volume'].count() / (df[df['volume_cond'] == 'YES']).groupby('asset')['volume'].size() 
    bid_completeness_check = pd.DataFrame(df[df['bid_ask_cond'] == 'YES']).groupby('asset')['bid'].count() / (df[df['bid_ask_cond'] == 'YES']).groupby('asset')['bid'].size() 
    ask_completeness_check = pd.DataFrame(df[df['bid_ask_cond'] == 'YES']).groupby('asset')['ask'].count() / (df[df['bid_ask_cond'] == 'YES']).groupby('asset')['ask'].size() 
    spread_completeness_check = pd.DataFrame(df[df['spread_cond'] == 'YES']).groupby('asset')['spread'].count() / (df[df['spread_cond'] == 'YES']).groupby('asset')['spread'].size() 

    completeness_df = pd.concat([date_completeness_check, close_completeness_check, ccy_completeness_check, source_completeness_check, spread_completeness_check,
                                 fx_completeness_check, volume_completeness_check, bid_completeness_check, ask_completeness_check], axis=1)

    return completeness_df

def flag_validation (df):
    df = df.copy()

    df['flag_close'] = (df['close'] > 0)
    df['flag_volume'] = (df['volume'] >= 0)
    df['flag_bid'] = (df['bid'] > 0)
    df['flag_ask'] = (df['ask'] > 0)
    df['flag_ask_vs_bid'] = (df['ask'] >= df['bid'])
    df['flag_spread'] = (df['spread'] >= 0)

    return df

def data_validation (df):
    df = df.copy()

    close_valid = ((df.groupby('asset')['flag_close'].sum() / df.groupby('asset')['close'].count()).rename('close_valid'))*100
    volume_valid = (df.groupby('asset')['flag_volume'].sum() / df.groupby('asset')['volume'].count()).rename('volume_valid')*100
    bid_valid = (df.groupby('asset')['flag_bid'].sum() / df.groupby('asset')['bid'].count()).rename('bid_valid')*100
    ask_valid = (df.groupby('asset')['flag_ask'].sum() / df.groupby('asset')['ask'].count()).rename('ask_valid')*100
    spread_valid = (df.groupby('asset')['flag_spread'].sum() / df.groupby('asset')['spread'].count()).rename('spread_valid')*100

    validation_heatmap = pd.concat([close_valid, volume_valid, bid_valid, ask_valid, spread_valid], axis=1)

    return validation_heatmap

def outlier_and_returns (df, k_z_score = 3):
    df = df.copy()
    df['daily_log_ret'] = df.groupby('asset')['close'].transform(lambda x: np.log(x/x.shift(1)))
    returns = df['daily_log_ret']
    df['std'] = df.groupby('asset')['daily_log_ret'].transform('std')
    df['mean'] = df.groupby('asset')['daily_log_ret'].transform('mean')

    df['upper_bound'] = df['mean'] + k_z_score * df['std']
    df['lower_bound'] = df['mean'] - k_z_score * df['std']

    df['outliers'] = (returns > df['upper_bound']) | (returns < df['lower_bound'])
    df['negative_outliers'] = returns < df['lower_bound']

    tot_outlier = (df.groupby('asset')['outliers'].sum().to_frame('tot_outliers_count'))
    n_neg_outliers = (df.groupby('asset')['negative_outliers'].sum().to_frame('neg_outliers_count'))
    perc_neg_outliers_on_total = (df.groupby('asset')['negative_outliers'].mean().mul(100).to_frame('neg_outliers_pct_on_tot'))
    perc_neg_on_tot_outliers = ((df.groupby('asset')['negative_outliers'].sum() / df.groupby('asset')['outliers'].sum()).mul(100).to_frame('neg_outliers_pct_on_tot_outliers'))

    outliers_table =  pd.concat([tot_outlier, n_neg_outliers, perc_neg_outliers_on_total, perc_neg_on_tot_outliers], axis=1)

    return outliers_table

def summary_table(df):

    df = df.copy()

    missing_close = (df.groupby('asset')['close'].apply(lambda x: x.isna().sum()).to_frame('missing_close'))
    missing_volume = (df.groupby('asset')['volume'].apply(lambda x: x.isna().sum()).to_frame('missing_volume'))
    missing_spread = (df.groupby('asset')['spread'].apply(lambda x: x.isna().sum()).to_frame('missing_spread'))
    missing_bid = (df.groupby('asset')['bid'].apply(lambda x: x.isna().sum()).to_frame('missing_bid'))
    missing_ask = (df.groupby('asset')['ask'].apply(lambda x: x.isna().sum()).to_frame('missing_ask'))
    tot_missing = (missing_close.squeeze()+ missing_volume.squeeze()+ missing_bid.squeeze()+ missing_ask.squeeze()+ missing_spread.squeeze()).to_frame('tot_missing_value')

    summary_table = pd.concat([missing_close, missing_volume, missing_bid, missing_ask, missing_spread, tot_missing], axis = 1)

    return summary_table