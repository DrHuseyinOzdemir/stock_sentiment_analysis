"""
COMPREHENSIVE SENTIMENT TRADING SYSTEM
Uses Multiple Real Social Media APIs

Data Sources:
1. Reddit (PRAW) - WallStreetBets mentions
2. StockTwits - Bullish/Bearish sentiment
3. Twitter/X (Tweepy) - Tweet volume and sentiment
4. NewsAPI - News sentiment
5. Yahoo Finance - Analyst ratings

Setup Instructions at bottom of file!
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re

# ============================================================================
# CONFIGURATION - ADD YOUR API KEYS HERE
# ============================================================================

# Reddit API (PRAW) - Get from: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = "YOUR_CLIENT_ID_HERE"
REDDIT_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
REDDIT_USER_AGENT = "sentiment_trader_1.0"

# Twitter API (Optional) - Get from: https://developer.twitter.com
TWITTER_BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"

# News API (Optional) - Get from: https://newsapi.org
NEWS_API_KEY = "YOUR_API_KEY_HERE"

# StockTwits - No API key needed for basic access!

# ============================================================================


class MultiSourceSentimentAnalyzer:
    """
    Advanced sentiment analyzer using multiple social media sources
    """
    
    def __init__(self, use_reddit=True, use_stocktwits=True, 
                 use_twitter=False, use_news=False):
        self.use_reddit = use_reddit
        self.use_stocktwits = use_stocktwits
        self.use_twitter = use_twitter
        self.use_news = use_news
        
        # Initialize APIs
        self._init_reddit()
        self._init_twitter()
        
    def _init_reddit(self):
        """Initialize Reddit API"""
        if not self.use_reddit:
            self.reddit = None
            return
            
        try:
            import praw
            
            if REDDIT_CLIENT_ID == "YOUR_CLIENT_ID_HERE":
                print("⚠️  Reddit API not configured (see setup instructions)")
                self.reddit = None
                return
            
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
            print("✓ Reddit API connected")
        except ImportError:
            print("⚠️  Install PRAW: pip install praw")
            self.reddit = None
        except Exception as e:
            print(f"⚠️  Reddit API error: {e}")
            self.reddit = None
    
    def _init_twitter(self):
        """Initialize Twitter API"""
        if not self.use_twitter:
            self.twitter = None
            return
            
        try:
            import tweepy
            
            if TWITTER_BEARER_TOKEN == "YOUR_BEARER_TOKEN_HERE":
                print("⚠️  Twitter API not configured")
                self.twitter = None
                return
            
            self.twitter = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
            print("✓ Twitter API connected")
        except ImportError:
            print("⚠️  Install Tweepy: pip install tweepy")
            self.twitter = None
        except Exception as e:
            print(f"⚠️  Twitter API error: {e}")
            self.twitter = None
    
    def get_reddit_sentiment(self, ticker, days=7, limit=100):
        """
        Get Reddit sentiment from WallStreetBets and r/stocks
        Returns: (sentiment_score, mention_count, bullish_count, bearish_count)
        """
        if not self.reddit:
            return 0, 0, 0, 0
        
        try:
            subreddits = ['wallstreetbets', 'stocks', 'investing']
            
            total_mentions = 0
            bullish_posts = 0
            bearish_posts = 0
            total_score = 0
            
            # Search in each subreddit
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for ticker mentions
                    query = f"${ticker} OR {ticker}"
                    
                    for post in subreddit.search(query, time_filter='week', limit=limit):
                        # Check if ticker is actually mentioned (not just in search)
                        text = (post.title + " " + post.selftext).upper()
                        
                        if f"${ticker}" in text or f" {ticker} " in text:
                            total_mentions += 1
                            
                            # Sentiment from upvotes and keywords
                            upvote_ratio = post.upvote_ratio
                            score = post.score
                            
                            # Keyword sentiment
                            bullish_words = ['buy', 'calls', 'moon', 'bullish', 'rocket', 
                                           'to the moon', 'yolo', 'long', 'undervalued']
                            bearish_words = ['sell', 'puts', 'crash', 'bearish', 'dump', 
                                           'overvalued', 'short', 'bubble']
                            
                            text_lower = text.lower()
                            bull_count = sum(1 for word in bullish_words if word in text_lower)
                            bear_count = sum(1 for word in bearish_words if word in text_lower)
                            
                            if bull_count > bear_count and upvote_ratio > 0.7:
                                bullish_posts += 1
                                total_score += score * upvote_ratio
                            elif bear_count > bull_count:
                                bearish_posts += 1
                                total_score -= score * upvote_ratio
                            else:
                                total_score += (score * upvote_ratio * 0.5)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    continue
            
            if total_mentions == 0:
                return 0, 0, 0, 0
            
            # Calculate sentiment (-1 to 1)
            sentiment = (bullish_posts - bearish_posts) / total_mentions
            
            return sentiment, total_mentions, bullish_posts, bearish_posts
            
        except Exception as e:
            print(f"    Reddit error: {e}")
            return 0, 0, 0, 0
    
    def get_stocktwits_sentiment(self, ticker):
        """
        Get sentiment from StockTwits (no API key needed!)
        Returns: (sentiment_score, message_count, bullish_pct)
        """
        if not self.use_stocktwits:
            return 0, 0, 0
        
        try:
            import requests
            
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return 0, 0, 0
            
            data = response.json()
            
            if 'messages' not in data:
                return 0, 0, 0
            
            messages = data['messages']
            
            bullish_count = 0
            bearish_count = 0
            
            for msg in messages:
                if 'entities' in msg and 'sentiment' in msg['entities']:
                    sentiment = msg['entities']['sentiment']
                    if sentiment:
                        if sentiment.get('basic') == 'Bullish':
                            bullish_count += 1
                        elif sentiment.get('basic') == 'Bearish':
                            bearish_count += 1
            
            total = bullish_count + bearish_count
            
            if total == 0:
                return 0, len(messages), 0
            
            # Sentiment score (-1 to 1)
            sentiment_score = (bullish_count - bearish_count) / total
            bullish_pct = (bullish_count / total) * 100
            
            return sentiment_score, len(messages), bullish_pct
            
        except Exception as e:
            print(f"    StockTwits error: {e}")
            return 0, 0, 0
    
    def get_twitter_sentiment(self, ticker, days=7):
        """
        Get Twitter sentiment (requires API access)
        Returns: (sentiment_score, tweet_count)
        """
        if not self.twitter:
            return 0, 0
        
        try:
            # Search for tweets mentioning ticker
            query = f"${ticker} OR #{ticker} -is:retweet lang:en"
            
            tweets = self.twitter.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics', 'text']
            )
            
            if not tweets.data:
                return 0, 0
            
            bullish_keywords = ['buy', 'bullish', 'moon', 'calls', 'long', 'breakout']
            bearish_keywords = ['sell', 'bearish', 'puts', 'short', 'crash', 'dump']
            
            sentiment_scores = []
            
            for tweet in tweets.data:
                text = tweet.text.lower()
                
                bull_count = sum(1 for word in bullish_keywords if word in text)
                bear_count = sum(1 for word in bearish_keywords if word in text)
                
                if bull_count > bear_count:
                    sentiment_scores.append(1)
                elif bear_count > bull_count:
                    sentiment_scores.append(-1)
                else:
                    sentiment_scores.append(0)
            
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
            
            return avg_sentiment, len(tweets.data)
            
        except Exception as e:
            print(f"    Twitter error: {e}")
            return 0, 0
    
    def get_news_sentiment(self, ticker):
        """
        Get news sentiment from NewsAPI
        Returns: (sentiment_score, article_count)
        """
        if not self.use_news or NEWS_API_KEY == "YOUR_API_KEY_HERE":
            return 0, 0
        
        try:
            import requests
            
            # Get company name for better search
            stock = yf.Ticker(ticker)
            company_name = stock.info.get('longName', ticker)
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'"{company_name}" OR ${ticker}',
                'apiKey': NEWS_API_KEY,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 50,
                'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return 0, 0
            
            data = response.json()
            articles = data.get('articles', [])
            
            if not articles:
                return 0, 0
            
            positive_words = ['surge', 'soar', 'rally', 'gain', 'beat', 'growth', 
                            'record', 'strong', 'bullish', 'upgrade', 'outperform']
            negative_words = ['drop', 'fall', 'plunge', 'loss', 'miss', 'weak', 
                            'decline', 'bearish', 'downgrade', 'concern', 'warning']
            
            sentiment_scores = []
            
            for article in articles:
                title = (article.get('title', '') + ' ' + 
                        article.get('description', '')).lower()
                
                pos_count = sum(1 for word in positive_words if word in title)
                neg_count = sum(1 for word in negative_words if word in title)
                
                if pos_count > neg_count:
                    sentiment_scores.append(1)
                elif neg_count > pos_count:
                    sentiment_scores.append(-1)
                else:
                    sentiment_scores.append(0)
            
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
            
            return avg_sentiment, len(articles)
            
        except Exception as e:
            print(f"    News error: {e}")
            return 0, 0
    
    def calculate_composite_sentiment(self, ticker):
        """
        Combine all sentiment sources
        """
        print(f"  Analyzing {ticker}...", end='', flush=True)
        
        try:
            # Get all sentiment sources
            reddit_sent, reddit_mentions, reddit_bull, reddit_bear = self.get_reddit_sentiment(ticker)
            st_sent, st_messages, st_bullish_pct = self.get_stocktwits_sentiment(ticker)
            twitter_sent, twitter_count = self.get_twitter_sentiment(ticker)
            news_sent, news_count = self.get_news_sentiment(ticker)
            
            # Get analyst data from yfinance
            stock = yf.Ticker(ticker)
            info = stock.info
            
            recommendation = info.get('recommendationKey', 'none')
            rec_scores = {
                'strong_buy': 100, 'buy': 80, 'outperform': 80,
                'hold': 50, 'underperform': 20, 'sell': 10,
                'strong_sell': 0, 'none': 50
            }
            analyst_score = rec_scores.get(recommendation, 50)
            
            # Calculate buzz score (how much people are talking about it)
            total_buzz = reddit_mentions + st_messages + twitter_count + news_count
            
            # Normalize buzz (0-100)
            buzz_score = min(100, (total_buzz / 5) * 10)  # 50+ mentions = 100 score
            
            # Weight the sources
            weights = {
                'analyst': 0.25,      # Professional opinion
                'stocktwits': 0.25,   # Dedicated stock sentiment
                'reddit': 0.20,       # Social buzz
                'news': 0.15,         # News sentiment
                'twitter': 0.10,      # Twitter buzz
                'buzz': 0.05          # Overall volume
            }
            
            # Convert sentiments (-1 to 1) to scores (0 to 100)
            reddit_score = (reddit_sent + 1) * 50
            st_score = (st_sent + 1) * 50
            twitter_score = (twitter_sent + 1) * 50
            news_score = (news_sent + 1) * 50
            
            # Calculate composite
            composite = (
                weights['analyst'] * analyst_score +
                weights['stocktwits'] * st_score +
                weights['reddit'] * reddit_score +
                weights['news'] * news_score +
                weights['twitter'] * twitter_score +
                weights['buzz'] * buzz_score
            )
            
            # Determine signal
            if composite >= 75 and total_buzz >= 20:
                signal = 'STRONG_BUY'
            elif composite >= 65:
                signal = 'BUY'
            elif composite <= 35:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            print(f" ✓ Score: {composite:.1f} | {signal} | Buzz: {total_buzz}")
            
            return {
                'ticker': ticker,
                'composite_score': composite,
                'signal': signal,
                'analyst_score': analyst_score,
                'reddit_sentiment': reddit_sent,
                'reddit_mentions': reddit_mentions,
                'reddit_bullish': reddit_bull,
                'reddit_bearish': reddit_bear,
                'stocktwits_sentiment': st_sent,
                'stocktwits_messages': st_messages,
                'stocktwits_bullish_pct': st_bullish_pct,
                'twitter_sentiment': twitter_sent,
                'twitter_count': twitter_count,
                'news_sentiment': news_sent,
                'news_count': news_count,
                'total_buzz': total_buzz,
                'recommendation': recommendation
            }
            
        except Exception as e:
            print(f" ✗ Error: {e}")
            return None
    
    def screen_stocks(self, stock_list, top_n=15):
        """
        Screen stocks and return top opportunities
        """
        print(f"\n{'='*80}")
        print(f"MULTI-SOURCE SENTIMENT SCREENING: {len(stock_list)} STOCKS")
        print(f"{'='*80}\n")
        
        results = []
        
        for i, ticker in enumerate(stock_list, 1):
            print(f"[{i}/{len(stock_list)}] ", end='')
            result = self.calculate_composite_sentiment(ticker)
            if result:
                results.append(result)
            time.sleep(1)  # Rate limiting
        
        if not results:
            return pd.DataFrame(), pd.DataFrame()
        
        df = pd.DataFrame(results)
        df = df.sort_values('composite_score', ascending=False)
        
        buy_signals = df[df['signal'].isin(['STRONG_BUY', 'BUY'])]
        
        print(f"\n{'='*80}")
        print(f"TOP {top_n} OPPORTUNITIES")
        print(f"{'='*80}")
        print(f"{'#':<4}{'Ticker':<8}{'Signal':<14}{'Score':<8}{'Analyst':<10}{'Reddit':<10}{'StockTwits':<12}{'Buzz'}")
        print(f"{'-'*80}")
        
        for idx, (_, row) in enumerate(buy_signals.head(top_n).iterrows(), 1):
            print(f"{idx:<4}"
                  f"{row['ticker']:<8}"
                  f"{row['signal']:<14}"
                  f"{row['composite_score']:>6.1f}  "
                  f"{row['analyst_score']:>8.1f}  "
                  f"{row['reddit_mentions']:>8.0f}  "
                  f"{row['stocktwits_bullish_pct']:>10.1f}%  "
                  f"{row['total_buzz']:>4.0f}")
        
        df.to_csv('multi_source_sentiment.csv', index=False)
        print(f"\n💾 Results saved to 'multi_source_sentiment.csv'")
        
        return buy_signals.head(top_n), df


# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

SETUP_INSTRUCTIONS = """
╔══════════════════════════════════════════════════════════════════════════╗
║                      API SETUP INSTRUCTIONS                               ║
╚══════════════════════════════════════════════════════════════════════════╝

🔥 REDDIT API (RECOMMENDED - FREE)
──────────────────────────────────
1. Go to: https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - Name: "Sentiment Trader"
   - App type: Select "script"
   - Redirect URI: http://localhost:8080
4. Click "Create app"
5. Copy your credentials:
   - Client ID (under app name)
   - Client Secret (labeled "secret")
6. Paste into this file at the top

Installation: pip install praw

──────────────────────────────────

🔥 STOCKTWITS (NO API KEY NEEDED!)
──────────────────────────────────
Works out of the box! No setup required.

──────────────────────────────────

TWITTER API (OPTIONAL - LIMITED FREE)
──────────────────────────────────
1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Create a project and app
3. Get Bearer Token from "Keys and tokens"
4. Free tier: 500K tweets/month

Installation: pip install tweepy

──────────────────────────────────

NEWS API (OPTIONAL - LIMITED FREE)
──────────────────────────────────
1. Go to: https://newsapi.org/register
2. Get free API key (100 requests/day)
3. Paste into this file

──────────────────────────────────

RECOMMENDED SETUP:
✅ Reddit (MUST HAVE - Best data)
✅ StockTwits (FREE - Works automatically)
⭕ Twitter (Optional - Limited free tier)
⭕ News (Optional - Limited requests)

MINIMUM TO START:
Just Reddit + StockTwits gives you great results!

══════════════════════════════════════════════════════════════════════════
"""


if __name__ == "__main__":
    # Check if APIs are configured
    if REDDIT_CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        print(SETUP_INSTRUCTIONS)
        print("\n⚠️  Please configure Reddit API first (see instructions above)")
        print("\nYou can still test with StockTwits only:")
        response = input("\nContinue with StockTwits only? (y/n): ").strip().lower()
        if response != 'y':
            exit()
        use_reddit = False
    else:
        use_reddit = True
    
    print("\n" + "="*80)
    print("MULTI-SOURCE SENTIMENT ANALYSIS")
    print("="*80)
    
    # Initialize
    analyzer = MultiSourceSentimentAnalyzer(
        use_reddit=use_reddit,
        use_stocktwits=True,  # Always works!
        use_twitter=False,     # Set to True if you have API
        use_news=False         # Set to True if you have API
    )
    
    # Get stock list
    popular_stocks = [
        # Mega-cap
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
        # Meme stocks
        'GME', 'AMC', 'PLTR', 'COIN',
        # Semiconductors
        'AMD', 'INTC', 'MU', 'AVGO',
        # Growth
        'SNOW', 'CRWD', 'NET', 'DDOG',
        # Others
        'SPY', 'QQQ'
    ]
    
    print(f"\nScreening {len(popular_stocks)} popular stocks...")
    print("This takes ~2-3 minutes with rate limiting...\n")
    
    top_picks, all_data = analyzer.screen_stocks(popular_stocks, top_n=10)
    
    print("\n" + "="*80)
    print("SCREENING COMPLETE!")
    print("="*80)
    print(f"\nFound {len(top_picks)} BUY/STRONG_BUY signals")
    print("\nReview 'multi_source_sentiment.csv' for full details")
