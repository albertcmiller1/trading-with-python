import argparse
import sys
import pprint
from trader import Trader
from parse_conf import Env
from datetime import datetime as dt

def main() -> int: 
    if not sys.argv[1:]: print("please use the -h or --help option to get started")
    user, list_portfolio, buy_stock, sell_stock, quantity, graph_portfolio, graph_stock, list_txns = parse_app_args()
    print(f"welcome {user}!\n")

    use_csvs = True
    list_transactions = False
    trader = Trader()

    if list_portfolio: 
        user_transactions = trader.get_user_transactions(user)
        if user_transactions.empty: 
            print(f"{user} does not have any stocks yet!")
            return 
        user_holdings = trader.create_portfolio(user_transactions)
        print('holdings: ')
        pprint.pprint(user_holdings)

    elif buy_stock: 
        print(f'attempting to buy {quantity} shares of {buy_stock}')
        if trader.buy_stock(user, buy_stock, quantity): print("success!")
        
    elif sell_stock: 
        print(f'attempting to sell {quantity} shares of {sell_stock}')
        if trader.sell_stock(user, sell_stock, int(quantity)): print('success!')

    elif graph_portfolio: 
        '''
        1. get user's transactions [x]
        2. find user's unique stocks [x]
        3. loop over unique stocks [x]
        4. for each uniqe stock, find the oldest purchase date [x]
        5. grab stock price history data from oldest purchese date until now [x]
        6. put this information into dictionary for each unique user's stocks [x]
        7. for each dataframe in dictionary, calulate gain/loss for each day 
        8. plot 
        '''

        # datetime_object = dt.strptime(date_time_str, '%m/%d/%Y %H:%M:%S')
        user_transactions = trader.get_user_transactions(user)
        if user_transactions.empty: 
            print(f"{user} does not have any stocks yet!")
            return 

        stock_dfs = {}

        for ticker in user_transactions["ticker"].unique(): 
            user_txns_of_x_ticker = user_transactions.loc[(user_transactions['ticker'] == ticker)]

            if use_csvs: 
                stock_history_df = trader.get_stock_data_from_csv("./stock_csvs/" + ticker + "_1d.csv")
            else: 
                stock_history_df = trader.get_stock_data(ticker, "1d")

            len_txns = len(user_txns_of_x_ticker.index)
            oldest_user_txn_date = user_txns_of_x_ticker.iloc[0]['date'].to_pydatetime()
            # newest_user_txn_date = user_txns_of_x_ticker.iloc[len_txns-1]['date'].to_pydatetime()

            print("\n")
            print(f"oldest_user_txn_date: {oldest_user_txn_date}")
            # print(f"oldest_user_txn_date: {type(oldest_user_txn_date)}")
            # print(f"newest_user_txn_date: {newest_user_txn_date}")
            # print("\n")

            len_stock_data = len(stock_history_df.index)
            oldest_stock_data_date = dt.fromtimestamp(stock_history_df.iloc[0]['date_utc'])
            newest_stock_data_date = dt.fromtimestamp(stock_history_df.iloc[len_stock_data-1]['date_utc'])

            # print(f"oldest_stock_data_date: {oldest_stock_data_date}")
            # print(f"oldest_stock_data_date: {type(oldest_stock_data_date)}")
            # print(f"newest_stock_data_date: {newest_stock_data_date}")
            # print("\n")

            # do a check to ensure all user transactions are within the bounds of oldest-newest stock data

            first_user_txn_row = 0

            for i, row in stock_history_df.iterrows():
                # find what row of the dataframe contains the date of the older_user_txn 
                # there's gotta be a better way to do this ...
                # if cant figure out way using pandas ... use binary search 
                if dt.fromtimestamp(row['date_utc']).date() == oldest_user_txn_date.date():
                    first_user_txn_row = i

     


            print("\n")
            stock_history_len = len(stock_history_df.index)
            print(f"starting len: {stock_history_len}")
            
            trimed_df = stock_history_df.iloc[first_user_txn_row:stock_history_len]

            new_len = len(trimed_df.index) - 1
            print(f"new_len: {new_len}")
            print("\n")



            first_row_of_trimmed_df = trimed_df.iloc[0]['date']
            last_row_of_trimmed_df = trimed_df.iloc[new_len]['date']

            print(f"first_row_of_trimmed_df: {first_row_of_trimmed_df}")
            print(f"last_row_of_trimmed_df: {last_row_of_trimmed_df}")


            # print("\n")
            # print(trimed_df.iloc[0])
            # print("\n")

            # len_df = len(trimed_df.index) -1
            # print(trimed_df.iloc[len_df])

            stock_dfs[ticker] = trimed_df 
        

        # print("\n")
        # print(stock_dfs["TSLA"].head())
        # print("\n")
        # print(stock_dfs["AAPL"].tail())


        '''
        get dataframes for each of the stocks a user owns 
        from the time of the first purchase til now ...
            > ensure the stock_data_df has enough data to span the user's transactions 
            > calculate gain/loss for each day for each stock 
            > aggregate gains/losses into dataframe 
            > y = value_of_portfolio + gain
        '''

    elif graph_stock: 
        print(f"graphing {graph_stock}...")
        # df = trader.get_from_csv("stock_csvs/AAPL_1d.csv")
        df = trader.get_stock_data('AAPL', '1d')
        df = trader.add_moving_average(df, 50)
        # trader.plot_volume(df)
        trader.plot(df, ('high', 'g'), ('low', 'r'), ('50ma', 'b'))
   
    elif list_txns: 
        user_transactions = trader.get_user_transactions(user)
        # find how many rows are in df and use that instead of hardcoding 
        print(df.head(100))
   
    else: 
        print('please use the -h or --help option to list out some of the availiable features of this repository.')

    return 0


def parse_app_args(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", help="use this flag to tell the program your user_id. this is needed to track which stocks you own.", required=True)
    parser.add_argument("--list_portfolio", help="use this flag to list out what socks you currently own and how much they are worth", action='store_true') 
    parser.add_argument("--buy_stock", help="use this flag to buy a stock. must pass in the ticker after the flag")
    parser.add_argument("--sell_stock", help="use this flag to sell a stock. must pass in the ticker after the flag")
    parser.add_argument("--quantity", help="use this flag to specify how many shares of a stock you would like to buy or sell. must pass in an integer after the flag.")
    parser.add_argument("--graph_portfolio", help="use this flag to graph your current portfolio", action='store_true')
    parser.add_argument("--graph_stock", help="use this flag to graph any stock. must pass in the ticker you would like to see")
    parser.add_argument("--list_txns", help="use this flag to list all the transactions of a user.")
    parser.add_argument("--no_csvs", help="by default, the program will download csvs of the stock data so less api calls will be made. use this flag to prevent downloading csv files and only use the stock api.")

    args = parser.parse_args()

    if args.buy_stock or args.sell_stock or args.quantity: 
        if not ((args.buy_stock and args.quantity) or (args.sell_stock and args.quantity)): 
            print("if you're buying or selling a stock, you must specify a ticker and quantity")
            sys.exit()

    return args.user, args.list_portfolio, args.buy_stock, args.sell_stock, args.quantity, args.graph_portfolio, args.graph_stock, args.list_txns

if __name__ == "__main__": 
    main()
