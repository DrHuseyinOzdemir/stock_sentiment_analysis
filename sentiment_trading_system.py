"""
ADVANCED SENTIMENT-DRIVEN TRADING SYSTEM
Uses real social media, news sentiment, and analyst ratings
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from collections import Counter
import time

class SentimentTradingSystem:
    """
    Real sentiment-based trading using:
    1. Reddit mentions (via pushshift API)
    2. News sentiment (via yfinance news)
    3. Analyst ratings (Strong Buy/Buy/Hold/Sell)
    4. Social media buzz metrics
    """
    
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.portfolio = {}
        self.trades = []
        
        # Free API sources (no key required)
        self.reddit_base = "https://api.pushshift.io/reddit/search/submission"
        
    def get_reddit_sentiment(self, ticker, days=7):
        """
        Get Reddit sentiment from WallStreetBets and stocks subreddits
        Returns: sentiment score (-1 to 1) and mention count
        """
        try:
            # Search last 7 days
            end_time = int(time.time())
            start_time = end_time - (days * 86400)
            
            subreddits = ['wallstreetbets', 'stocks', 'investing']
            total_mentions = 0
            positive_mentions = 0
            negative_mentions = 0
            
            for subreddit in subreddits:
                url = f"{self.reddit_base}?subreddit={subreddit}&q=${ticker}&after={start_time}&before={end_time}&size=100"
                
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', [])
                        
                        for post in posts:
                            total_mentions += 1
                            title = post.get('title', '').lower()
                            score = post.get('score', 0)
                            
                            # Simple sentiment from upvotes and keywords
                            if score > 50:  # Popular post
                                if any(word in title for word in ['buy', 'calls', 'moon', 'bullish', 'rocket']):
                                    positive_mentions += 1
                                elif any(word in title for word in ['sell', 'puts', 'crash', 'bearish', 'dump']):
                                    negative_mentions += 1
                
                except:
                    continue
            
            if total_mentions == 0:
                return 0, 0
            
            sentiment = (positive_mentions - negative_mentions) / total_mentions
            return sentiment, total_mentions
            
        except Exception as e:
            print(f"  Reddit error for {ticker}: {e}")
            return 0, 0
    
    def get_analyst_ratings(self, ticker):
        """
        Get analyst recommendations from yfinance
        Returns: Strong Buy score (0-100)
        """
        try:
            stock = yf.Ticker(ticker)
            recommendations = stock.recommendations
            
            if recommendations is None or len(recommendations) == 0:
                return 50  # Neutral
            
            # Get last 3 months of ratings
            recent = recommendations.tail(12)  # Last 12 ratings
            
            # Count recommendations
            counts = recent['To Grade'].value_counts()
            
            # Scoring system
            scores = {
                'Strong Buy': 100,
                'Buy': 75,
                'Outperform': 75,
                'Overweight': 75,
                'Hold': 50,
                'Neutral': 50,
                'Underperform': 25,
                'Sell': 0,
                'Strong Sell': 0
            }
            
            total_score = 0
            total_ratings = 0
            
            for grade, count in counts.items():
                score = scores.get(grade, 50)
                total_score += score * count
                total_ratings += count
            
            if total_ratings == 0:
                return 50
            
            return total_score / total_ratings
            
        except Exception as e:
            print(f"  Analyst error for {ticker}: {e}")
            return 50
    
    def get_news_sentiment(self, ticker):
        """
        Get news sentiment from yfinance news
        Returns: sentiment score (0-100)
        """
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return 50
            
            # Simple keyword-based sentiment
            positive_words = ['surge', 'soar', 'rally', 'gain', 'beat', 'growth', 'record', 'strong', 'bullish']
            negative_words = ['drop', 'fall', 'plunge', 'loss', 'miss', 'weak', 'decline', 'bearish', 'concern']
            
            sentiment_scores = []
            
            for article in news[:10]:  # Last 10 articles
                title = article.get('title', '').lower()
                
                positive_count = sum(1 for word in positive_words if word in title)
                negative_count = sum(1 for word in negative_words if word in title)
                
                if positive_count > negative_count:
                    sentiment_scores.append(75)
                elif negative_count > positive_count:
                    sentiment_scores.append(25)
                else:
                    sentiment_scores.append(50)
            
            return np.mean(sentiment_scores) if sentiment_scores else 50
            
        except Exception as e:
            print(f"  News error for {ticker}: {e}")
            return 50
    
    def calculate_composite_sentiment(self, ticker):
        """
        Combine all sentiment sources into one score
        Returns: score (0-100), signal ('STRONG_BUY', 'BUY', 'HOLD', 'SELL')
        """
        print(f"  Analyzing {ticker}...", end='')
        
        # Get all sentiment sources
        reddit_sentiment, reddit_mentions = self.get_reddit_sentiment(ticker)
        analyst_score = self.get_analyst_ratings(ticker)
        news_score = self.get_news_sentiment(ticker)
        
        # Weight the sources
        weights = {
            'analyst': 0.5,    # Analysts are most reliable
            'news': 0.3,       # News is fairly reliable
            'reddit': 0.2      # Reddit is least reliable but shows buzz
        }
        
        # Convert reddit sentiment (-1 to 1) to (0 to 100)
        reddit_score = (reddit_sentiment + 1) * 50
        
        # Composite score
        composite = (
            weights['analyst'] * analyst_score +
            weights['news'] * news_score +
            weights['reddit'] * reddit_score
        )
        
        # Determine signal
        if composite >= 80 and reddit_mentions >= 5:
            signal = 'STRONG_BUY'
        elif composite >= 70:
            signal = 'BUY'
        elif composite <= 30:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        print(f" Score: {composite:.1f} | Signal: {signal} | Reddit: {reddit_mentions} mentions")
        
        return {
            'ticker': ticker,
            'composite_score': composite,
            'signal': signal,
            'analyst_score': analyst_score,
            'news_score': news_score,
            'reddit_score': reddit_score,
            'reddit_mentions': reddit_mentions
        }
    
    def screen_universe(self, stock_universe, top_n=10):
        """
        Screen large universe and find top opportunities
        """
        print(f"\n{'='*70}")
        print(f"SCREENING {len(stock_universe)} STOCKS FOR SENTIMENT")
        print(f"{'='*70}\n")
        
        results = []
        
        for ticker in stock_universe:
            try:
                sentiment_data = self.calculate_composite_sentiment(ticker)
                results.append(sentiment_data)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"  ✗ {ticker}: {e}")
                continue
        
        # Convert to DataFrame and sort
        df = pd.DataFrame(results)
        df = df.sort_values('composite_score', ascending=False)
        
        # Filter for buy signals
        buy_signals = df[df['signal'].isin(['STRONG_BUY', 'BUY'])]
        
        print(f"\n{'='*70}")
        print(f"TOP {top_n} OPPORTUNITIES")
        print(f"{'='*70}")
        print(f"{'Rank':<6}{'Ticker':<8}{'Signal':<15}{'Score':<10}{'Analyst':<10}{'News':<10}{'Reddit':<10}{'Buzz'}")
        print(f"{'-'*70}")
        
        for idx, row in buy_signals.head(top_n).iterrows():
            print(f"{len(buy_signals) - list(buy_signals.index).index(idx):<6}"
                  f"{row['ticker']:<8}"
                  f"{row['signal']:<15}"
                  f"{row['composite_score']:>7.1f}  "
                  f"{row['analyst_score']:>7.1f}  "
                  f"{row['news_score']:>7.1f}  "
                  f"{row['reddit_score']:>7.1f}  "
                  f"{row['reddit_mentions']:>3.0f}")
        
        return buy_signals.head(top_n), df
    
    def backtest_signal_based(self, ticker, start_date, end_date, 
                             check_interval_days=7):
        """
        Backtest using sentiment signals
        Holds until SELL signal appears
        """
        print(f"\n{'='*70}")
        print(f"BACKTESTING {ticker} WITH SENTIMENT SIGNALS")
        print(f"{'='*70}")
        
        # Download price data
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs(ticker, level=1, axis=1)
        
        price_col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
        
        cash = self.initial_capital
        shares = 0
        position_open = False
        entry_price = 0
        entry_date = None
        portfolio_values = []
        trades = []
        
        # Check sentiment periodically
        current_date = start_date
        
        while current_date <= end_date:
            if current_date not in data.index:
                current_date += timedelta(days=1)
                continue
            
            price = data.loc[current_date, price_col]
            
            # Check sentiment every N days
            if (current_date - start_date).days % check_interval_days == 0:
                sentiment = self.calculate_composite_sentiment(ticker)
                signal = sentiment['signal']
                
                # BUY signal
                if signal in ['STRONG_BUY', 'BUY'] and not position_open:
                    shares = int(cash / price)
                    if shares > 0:
                        cost = shares * price
                        cash -= cost
                        position_open = True
                        entry_price = price
                        entry_date = current_date
                        
                        print(f"\n  🟢 BUY  {current_date.date()}: {shares} shares @ ${price:.2f}")
                        print(f"     Signal: {signal} | Score: {sentiment['composite_score']:.1f}")
                
                # SELL signal
                elif signal == 'SELL' and position_open:
                    revenue = shares * price
                    cash += revenue
                    profit = (price - entry_price) * shares
                    profit_pct = ((price - entry_price) / entry_price) * 100
                    days_held = (current_date - entry_date).days
                    
                    trades.append({
                        'entry_date': entry_date,
                        'entry_price': entry_price,
                        'exit_date': current_date,
                        'exit_price': price,
                        'shares': shares,
                        'profit': profit,
                        'profit_pct': profit_pct,
                        'days_held': days_held
                    })
                    
                    print(f"\n  🔴 SELL {current_date.date()}: ${profit:,.2f} profit ({profit_pct:+.1f}%)")
                    print(f"     Signal: {signal} | Held: {days_held} days")
                    
                    shares = 0
                    position_open = False
            
            # Track portfolio value
            portfolio_value = cash + shares * price
            portfolio_values.append({
                'date': current_date,
                'price': price,
                'shares': shares,
                'cash': cash,
                'total_value': portfolio_value
            })
            
            current_date += timedelta(days=1)
        
        # Close position at end
        if position_open:
            final_price = data[price_col].iloc[-1]
            revenue = shares * final_price
            cash += revenue
            profit = (final_price - entry_price) * shares
            profit_pct = ((final_price - entry_price) / entry_price) * 100
            
            trades.append({
                'entry_date': entry_date,
                'entry_price': entry_price,
                'exit_date': end_date,
                'exit_price': final_price,
                'shares': shares,
                'profit': profit,
                'profit_pct': profit_pct,
                'days_held': (end_date - entry_date).days
            })
        
        # Calculate metrics
        final_value = cash
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        print(f"\n{'='*70}")
        print(f"RESULTS")
        print(f"{'='*70}")
        print(f"Initial Capital:  ${self.initial_capital:,.2f}")
        print(f"Final Value:      ${final_value:,.2f}")
        print(f"Total Return:     {total_return:.2f}%")
        print(f"Total Trades:     {len(trades)}")
        
        if trades:
            winning = [t for t in trades if t['profit'] > 0]
            print(f"Win Rate:         {len(winning)/len(trades)*100:.1f}%")
            print(f"Avg Profit:       ${np.mean([t['profit'] for t in trades]):,.2f}")
        
        return {
            'final_value': final_value,
            'total_return': total_return,
            'trades': trades,
            'portfolio_values': portfolio_values
        }


# Large stock universe for screening
def get_large_stock_universe():
    """
    Get 200+ stocks across all sectors for comprehensive screening
    """
    
    # Mega-cap tech
    tech = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'TSLA', 'AVGO']
    
    # Semiconductors (hot sector)
    semis = ['AMD', 'INTC', 'QCOM', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'MU', 'MRVL', 'ADI',
             'NXPI', 'MCHP', 'ON', 'MPWR', 'SWKS', 'QRVO', 'ASML', 'TSM']
    
    # Cloud/SaaS
    cloud = ['CRM', 'NOW', 'SNOW', 'DDOG', 'TEAM', 'WDAY', 'ZM', 'CRWD', 'OKTA', 'NET',
             'DOCU', 'TWLO', 'ZS', 'PANW', 'FTNT', 'MDB', 'PLTR', 'U']
    
    # Financials
    finance = ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'AXP', 'BLK', 'SCHW', 'USB',
               'V', 'MA', 'PYPL', 'SQ', 'COIN', 'SOFI']
    
    # Healthcare
    health = ['UNH', 'JNJ', 'PFE', 'ABBV', 'LLY', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN',
              'GILD', 'VRTX', 'REGN', 'ISRG', 'MRNA', 'BNTX', 'ZTS', 'DXCM']
    
    # Consumer
    consumer = ['AMZN', 'TSLA', 'WMT', 'HD', 'COST', 'NKE', 'MCD', 'SBUX', 'TGT', 'LOW',
                'DIS', 'NFLX', 'CMCSA', 'PG', 'KO', 'PEP']
    
    # Energy (momentum sector)
    energy = ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'MPC', 'PSX', 'VLO', 'OXY']
    
    # Industrials
    industrial = ['BA', 'CAT', 'HON', 'UPS', 'RTX', 'LMT', 'GE', 'DE', 'MMM', 'FDX']
    
    # E-commerce & Digital
    ecom = ['SHOP', 'MELI', 'BABA', 'JD', 'PDD', 'SE', 'EBAY', 'ETSY', 'W', 'CHWY']
    
    # EV & Clean Energy
    ev = ['TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV', 'PLUG', 'ENPH', 'SEDG', 'RUN']
    
    # Biotech
    biotech = ['MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'GILD', 'ALNY', 'SGEN', 'BMRN']
    
    # Combine all (remove duplicates)
    all_stocks = list(set(tech + semis + cloud + finance + health + consumer + 
                          energy + industrial + ecom + ev + biotech))
    
    return sorted(all_stocks)


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("ADVANCED SENTIMENT TRADING SYSTEM")
    print("="*70)
    print("\nThis system uses:")
    print("  ✓ Reddit mentions & sentiment")
    print("  ✓ Analyst ratings (Strong Buy/Buy/Sell)")
    print("  ✓ News sentiment analysis")
    print("  ✓ Social media buzz metrics")
    print("\n" + "="*70)
    
    # Initialize system
    system = SentimentTradingSystem(initial_capital=100000)
    
    # Get large universe
    universe = get_large_stock_universe()
    print(f"\nTotal stocks to screen: {len(universe)}")
    
    # Screen for opportunities (use subset for speed)
    print("\n⚠️  Screening 50 stocks (for demo - adjust as needed)...")
    print("⚠️  This takes ~2-5 minutes due to API rate limits...")
    
    top_stocks, all_scores = system.screen_universe(
        universe[:50],  # First 50 for speed
        top_n=10
    )
    
    # Save results
    all_scores.to_csv('sentiment_analysis_results.csv', index=False)
    print(f"\n💾 Full results saved to: sentiment_analysis_results.csv")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Review the top opportunities above")
    print("2. Run backtest on interesting stocks")
    print("3. Adjust screening criteria as needed")
    print("\nTo backtest a stock:")
    print("  system.backtest_signal_based('NVDA', datetime(2023,1,1), datetime(2024,12,31))")
