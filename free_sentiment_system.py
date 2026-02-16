"""
FREE SENTIMENT TRADING SYSTEM (NO API KEYS NEEDED!)
Uses completely free data sources via web scraping

Data Sources:
1. StockTwits - Free, no API key (best sentiment source!)
2. Yahoo Finance - News, analyst ratings
3. Finviz - Social sentiment indicators
4. Reddit via web scraping (no API needed)
5. Google Trends - Search volume

All completely FREE with no registration!
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
import time
import warnings
warnings.filterwarnings('ignore')

class FreeSentimentAnalyzer:
    """
    Sentiment analyzer using only free sources (no API keys!)
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stocktwits_sentiment(self, ticker):
        """
        Get StockTwits sentiment (FREE, no API key!)
        This is the BEST free sentiment source
        """
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return 50, 0, 0, 0
            
            data = response.json()
            
            if 'messages' not in data:
                return 50, 0, 0, 0
            
            messages = data['messages']
            
            bullish = 0
            bearish = 0
            total = 0
            
            for msg in messages:
                total += 1
                if 'entities' in msg and 'sentiment' in msg['entities']:
                    sentiment = msg['entities']['sentiment']
                    if sentiment:
                        if sentiment.get('basic') == 'Bullish':
                            bullish += 1
                        elif sentiment.get('basic') == 'Bearish':
                            bearish += 1
            
            if bullish + bearish == 0:
                sentiment_score = 50
            else:
                sentiment_score = (bullish / (bullish + bearish)) * 100
            
            return sentiment_score, total, bullish, bearish
            
        except Exception as e:
            return 50, 0, 0, 0
    
    def get_yahoo_news_sentiment(self, ticker):
        """
        Scrape Yahoo Finance news for sentiment
        """
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return 50, 0
            
            positive_words = ['surge', 'soar', 'rally', 'gain', 'beat', 'growth', 
                            'record', 'strong', 'bullish', 'upgrade', 'outperform',
                            'buy', 'positive', 'breakthrough', 'success']
            negative_words = ['drop', 'fall', 'plunge', 'loss', 'miss', 'weak', 
                            'decline', 'bearish', 'downgrade', 'concern', 'warning',
                            'sell', 'negative', 'disappointing', 'trouble']
            
            sentiment_scores = []
            
            for article in news[:20]:  # Last 20 articles
                title = article.get('title', '').lower()
                
                pos_count = sum(1 for word in positive_words if word in title)
                neg_count = sum(1 for word in negative_words if word in title)
                
                if pos_count > neg_count:
                    sentiment_scores.append(75)
                elif neg_count > pos_count:
                    sentiment_scores.append(25)
                else:
                    sentiment_scores.append(50)
            
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 50
            
            return avg_sentiment, len(news)
            
        except Exception as e:
            return 50, 0
    
    def get_finviz_sentiment(self, ticker):
        """
        Get sentiment from Finviz (free stock screener)
        """
        try:
            url = f"https://finviz.com/quote.ashx?t={ticker}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return 50, 0
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for news headlines
            news_table = soup.find('table', {'id': 'news-table'})
            
            if not news_table:
                return 50, 0
            
            headlines = news_table.find_all('a')
            
            positive_words = ['surge', 'rally', 'gain', 'upgrade', 'buy', 'bullish']
            negative_words = ['drop', 'fall', 'downgrade', 'sell', 'bearish', 'concern']
            
            sentiment_scores = []
            
            for headline in headlines[:15]:
                text = headline.text.lower()
                
                pos = sum(1 for word in positive_words if word in text)
                neg = sum(1 for word in negative_words if word in text)
                
                if pos > neg:
                    sentiment_scores.append(75)
                elif neg > pos:
                    sentiment_scores.append(25)
                else:
                    sentiment_scores.append(50)
            
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 50
            
            return avg_sentiment, len(headlines)
            
        except Exception as e:
            return 50, 0
    
    def get_reddit_mentions_scrape(self, ticker):
        """
        Scrape Reddit for mentions (no API needed)
        Uses old.reddit.com which is easier to scrape
        """
        try:
            # Search WallStreetBets
            url = f"https://old.reddit.com/r/wallstreetbets/search/?q={ticker}&restrict_sr=1&sort=new"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return 0, 0, 0
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Count posts
            posts = soup.find_all('div', class_='search-result')
            
            bullish_keywords = ['buy', 'calls', 'moon', 'yolo', 'bullish', 'long']
            bearish_keywords = ['sell', 'puts', 'bearish', 'short', 'crash']
            
            bullish_count = 0
            bearish_count = 0
            
            for post in posts[:20]:
                title = post.text.lower()
                
                if any(word in title for word in bullish_keywords):
                    bullish_count += 1
                elif any(word in title for word in bearish_keywords):
                    bearish_count += 1
            
            total_mentions = len(posts)
            
            return total_mentions, bullish_count, bearish_count
            
        except Exception as e:
            return 0, 0, 0
    
    def get_analyst_ratings(self, ticker):
        """
        Get analyst recommendations from yfinance
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            recommendation = info.get('recommendationKey', 'none')
            
            rec_scores = {
                'strong_buy': 95,
                'buy': 80,
                'outperform': 80,
                'hold': 50,
                'underperform': 20,
                'sell': 10,
                'strong_sell': 5,
                'none': 50
            }
            
            score = rec_scores.get(recommendation, 50)
            
            # Get target upside
            target = info.get('targetMeanPrice', None)
            current = info.get('currentPrice', None)
            
            upside = 0
            if target and current and current > 0:
                upside = ((target - current) / current) * 100
                
                # Boost score for big upside
                if upside > 25:
                    score = min(score + 15, 100)
                elif upside > 15:
                    score = min(score + 10, 100)
            
            num_analysts = info.get('numberOfAnalystOpinions', 0)
            
            return score, recommendation, upside, num_analysts
            
        except Exception as e:
            return 50, 'none', 0, 0
    
    def get_price_momentum(self, ticker):
        """
        Get price momentum (institutional buying signal)
        """
        try:
            data = yf.download(ticker, period='3mo', progress=False)
            
            if len(data) < 20:
                return 50
            
            # Handle MultiIndex
            if isinstance(data.columns, pd.MultiIndex):
                data = data.xs(ticker, level=1, axis=1)
            
            price_col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
            
            current = data[price_col].iloc[-1]
            month_ago = data[price_col].iloc[-20]
            
            # Calculate return
            momentum = ((current - month_ago) / month_ago) * 100
            
            # Volume analysis
            avg_vol_recent = data['Volume'].tail(10).mean()
            avg_vol_baseline = data['Volume'].head(40).mean()
            
            volume_surge = 0
            if avg_vol_baseline > 0:
                volume_surge = ((avg_vol_recent - avg_vol_baseline) / avg_vol_baseline) * 100
            
            # Score based on momentum and volume
            score = 50
            
            if momentum > 20:
                score += 25
            elif momentum > 10:
                score += 15
            elif momentum > 5:
                score += 5
            elif momentum < -20:
                score -= 25
            elif momentum < -10:
                score -= 15
            
            if volume_surge > 50:
                score += 10
            elif volume_surge > 25:
                score += 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            return 50
    
    def calculate_composite_score(self, ticker):
        """
        Calculate final composite sentiment score
        """
        print(f"  [{ticker}] ", end='', flush=True)
        
        try:
            # Get all signals
            st_score, st_total, st_bull, st_bear = self.get_stocktwits_sentiment(ticker)
            news_score, news_count = self.get_yahoo_news_sentiment(ticker)
            finviz_score, finviz_count = self.get_finviz_sentiment(ticker)
            reddit_mentions, reddit_bull, reddit_bear = self.get_reddit_mentions_scrape(ticker)
            analyst_score, recommendation, upside, num_analysts = self.get_analyst_ratings(ticker)
            momentum_score = self.get_price_momentum(ticker)
            
            # Calculate Reddit sentiment
            reddit_score = 50
            if reddit_bull + reddit_bear > 0:
                reddit_score = (reddit_bull / (reddit_bull + reddit_bear)) * 100
            
            # Total buzz
            total_buzz = st_total + news_count + finviz_count + reddit_mentions
            
            # Weighted composite
            weights = {
                'stocktwits': 0.30,    # Best free source
                'analyst': 0.25,       # Professional opinion
                'momentum': 0.20,      # Price action
                'news': 0.15,          # News sentiment
                'finviz': 0.05,        # Additional news
                'reddit': 0.05         # Social buzz
            }
            
            composite = (
                weights['stocktwits'] * st_score +
                weights['analyst'] * analyst_score +
                weights['momentum'] * momentum_score +
                weights['news'] * news_score +
                weights['finviz'] * finviz_score +
                weights['reddit'] * reddit_score
            )
            
            # Determine signal
            if composite >= 75 and total_buzz >= 15 and st_bull > st_bear:
                signal = 'STRONG_BUY'
            elif composite >= 65:
                signal = 'BUY'
            elif composite <= 35:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            print(f"Score: {composite:.1f} | {signal} | Buzz: {total_buzz} | ST: {st_bull}B/{st_bear}B")
            
            return {
                'ticker': ticker,
                'composite_score': composite,
                'signal': signal,
                'stocktwits_score': st_score,
                'stocktwits_bullish': st_bull,
                'stocktwits_bearish': st_bear,
                'stocktwits_total': st_total,
                'analyst_score': analyst_score,
                'analyst_recommendation': recommendation,
                'target_upside': upside,
                'num_analysts': num_analysts,
                'momentum_score': momentum_score,
                'news_score': news_score,
                'news_count': news_count,
                'reddit_mentions': reddit_mentions,
                'reddit_bullish': reddit_bull,
                'reddit_bearish': reddit_bear,
                'total_buzz': total_buzz
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def screen_stocks(self, stock_list, top_n=15):
        """
        Screen stocks for best opportunities
        """
        print(f"\n{'='*80}")
        print(f"FREE SENTIMENT SCREENING: {len(stock_list)} STOCKS")
        print(f"{'='*80}")
        print("Sources: StockTwits + Yahoo News + Finviz + Reddit + Analysts\n")
        
        results = []
        
        for i, ticker in enumerate(stock_list, 1):
            print(f"[{i}/{len(stock_list)}] ", end='')
            result = self.calculate_composite_score(ticker)
            if result:
                results.append(result)
            time.sleep(1)  # Be polite to servers
        
        if not results:
            print("\n❌ No results obtained")
            return pd.DataFrame(), pd.DataFrame()
        
        df = pd.DataFrame(results)
        df = df.sort_values('composite_score', ascending=False)
        
        buy_signals = df[df['signal'].isin(['STRONG_BUY', 'BUY'])]
        
        print(f"\n{'='*80}")
        print(f"TOP {top_n} OPPORTUNITIES")
        print(f"{'='*80}")
        print(f"{'#':<4}{'Ticker':<8}{'Signal':<14}{'Score':<8}{'ST Bull':<9}{'Analyst':<10}{'Mom':<8}{'Buzz':<8}{'Upside'}")
        print(f"{'-'*80}")
        
        for idx, (_, row) in enumerate(buy_signals.head(top_n).iterrows(), 1):
            print(f"{idx:<4}"
                  f"{row['ticker']:<8}"
                  f"{row['signal']:<14}"
                  f"{row['composite_score']:>6.1f}  "
                  f"{row['stocktwits_bullish']:>7.0f}  "
                  f"{row['analyst_score']:>8.1f}  "
                  f"{row['momentum_score']:>6.1f}  "
                  f"{row['total_buzz']:>6.0f}  "
                  f"{row['target_upside']:>6.1f}%")
        
        print(f"\n💾 Full results saved to 'free_sentiment_analysis.csv'")
        df.to_csv('free_sentiment_analysis.csv', index=False)
        
        # Show best pick details
        if len(buy_signals) > 0:
            best = buy_signals.iloc[0]
            print(f"\n{'='*80}")
            print(f"🏆 TOP PICK: {best['ticker']}")
            print(f"{'='*80}")
            print(f"Signal: {best['signal']}")
            print(f"Composite Score: {best['composite_score']:.1f}/100")
            print(f"Analyst Rating: {best['analyst_recommendation']} (upside: {best['target_upside']:.1f}%)")
            print(f"StockTwits: {best['stocktwits_bullish']:.0f} bullish vs {best['stocktwits_bearish']:.0f} bearish")
            print(f"Total Buzz: {best['total_buzz']:.0f} mentions")
            print(f"{'='*80}")
        
        return buy_signals.head(top_n), df


def get_stock_universe():
    """
    Get curated stock list (focus on high social media coverage)
    """
    return {
        'Mega-Cap Tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
        'Meme Stocks': ['GME', 'AMC', 'BBBY', 'PLTR', 'BB'],
        'Crypto/Fintech': ['COIN', 'MSTR', 'SQ', 'HOOD', 'SOFI'],
        'Semiconductors': ['AMD', 'INTC', 'MU', 'AVGO', 'QCOM'],
        'AI/Cloud': ['SNOW', 'CRWD', 'NET', 'DDOG', 'AI', 'SMCI'],
        'Popular Growth': ['SHOP', 'ROKU', 'UBER', 'LYFT', 'RIVN'],
        'Indices': ['SPY', 'QQQ', 'IWM']
    }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FREE SENTIMENT TRADING SYSTEM")
    print("="*80)
    print("\n✅ NO API KEYS NEEDED!")
    print("✅ NO REGISTRATION REQUIRED!")
    print("✅ COMPLETELY FREE!")
    print("\nData Sources:")
    print("  • StockTwits (best free sentiment)")
    print("  • Yahoo Finance (news & analysts)")
    print("  • Finviz (news sentiment)")
    print("  • Reddit (web scraping)")
    print("  • Price momentum (institutional signals)")
    print("\n" + "="*80)
    
    analyzer = FreeSentimentAnalyzer()
    universe = get_stock_universe()
    
    print("\nSelect stocks to screen:")
    print("1. All stocks (~50, takes 5-7 minutes)")
    print("2. Specific category (fast)")
    print("3. Top 20 most popular (recommended)")
    
    choice = input("\nEnter choice (1/2/3) or press Enter for #3: ").strip()
    
    if choice == '1':
        # All stocks
        all_stocks = []
        for category, stocks in universe.items():
            all_stocks.extend(stocks)
        stocks_to_screen = list(set(all_stocks))
        
    elif choice == '2':
        # Pick category
        print("\nCategories:")
        categories = list(universe.keys())
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat} ({len(universe[cat])} stocks)")
        
        cat_choice = input("\nEnter category number: ").strip()
        try:
            cat_name = categories[int(cat_choice) - 1]
            stocks_to_screen = universe[cat_name]
        except:
            stocks_to_screen = universe['Mega-Cap Tech']
    
    else:
        # Top 20 popular (default)
        stocks_to_screen = [
            'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'GME', 'PLTR',
            'COIN', 'SNOW', 'CRWD', 'META', 'GOOGL', 'AMZN',
            'SPY', 'QQQ', 'MSTR', 'HOOD', 'SOFI', 'NET', 'SMCI'
        ]
    
    print(f"\n🔍 Screening {len(stocks_to_screen)} stocks...")
    print(f"⏱️  Estimated time: ~{len(stocks_to_screen)} minutes\n")
    
    top_picks, all_results = analyzer.screen_stocks(stocks_to_screen, top_n=15)
    
    print("\n" + "="*80)
    print("SCREENING COMPLETE!")
    print("="*80)
    print(f"\nFound {len(top_picks)} BUY/STRONG_BUY signals")
    print("\nNext steps:")
    print("1. Review 'free_sentiment_analysis.csv' for full details")
    print("2. Research the top picks")
    print("3. Check StockTwits.com for each ticker to verify sentiment")
    print("4. Make your trading decisions!")
    print("\n" + "="*80)
