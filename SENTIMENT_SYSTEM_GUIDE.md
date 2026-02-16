# Advanced Sentiment Trading System
## Complete Implementation Guide

---

## 🎯 NEW STRATEGY OVERVIEW

### **What Changed:**
❌ **OLD**: Fake sentiment (just momentum math) + slow MA signals  
✅ **NEW**: Real sentiment from social media + analyst ratings + news

### **New Data Sources:**

1. **Reddit API** (Free)
   - WallStreetBets mentions
   - r/stocks discussions
   - Upvote sentiment
   - Buzz metrics

2. **Yahoo Finance** (Free, via yfinance)
   - Analyst ratings (Strong Buy/Buy/Hold/Sell)
   - News headlines
   - Recommendation trends

3. **News Sentiment** (Free)
   - Keyword analysis
   - Title sentiment
   - Recent articles

---

## 📊 NEW STRATEGY LOGIC

### **Step 1: Screen 200+ Stocks**
```
For each stock:
  ├── Get Reddit mentions (last 7 days)
  ├── Get analyst ratings (Strong Buy to Sell)
  ├── Analyze news headlines
  └── Calculate composite score (0-100)

Rank all stocks by score
```

### **Step 2: Identify Signals**
```
Score >= 80 + Reddit buzz >= 5 mentions = STRONG_BUY 🔥
Score >= 70                              = BUY
Score <= 30                              = SELL
Everything else                          = HOLD
```

### **Step 3: Trade on Signals**
```
STRONG_BUY or BUY:
  → Enter position (100% of capital)
  → Hold until...

SELL signal appears:
  → Exit position
  → Take profit/loss
  → Wait for next BUY
```

### **Key Differences:**
- ✅ **Real sentiment** (not fake math)
- ✅ **Large universe** (200+ stocks, not 39)
- ✅ **Hold until sell signal** (not time-based MA)
- ✅ **Strong Buy focus** (high-conviction picks)

---

## 🚀 QUICK START

### **1. Install Required Packages**
```bash
pip install yfinance pandas numpy requests --break-system-packages
```

### **2. Run the Screener**
```bash
python sentiment_trading_system.py
```

This will:
- Screen 50 stocks (adjust as needed)
- Show top 10 opportunities
- Display sentiment breakdown
- Save results to CSV

### **3. View Results**
```
TOP 10 OPPORTUNITIES
======================================================================
Rank  Ticker  Signal         Score     Analyst   News      Reddit    Buzz
----------------------------------------------------------------------
1     NVDA    STRONG_BUY     92.3      95.0      90.0      92.5      15
2     PLTR    STRONG_BUY     88.5      85.0      88.0      95.0      23
3     AMD     BUY            78.2      80.0      75.0      80.0      8
...
```

---

## 🔧 CUSTOMIZATION

### **Adjust Stock Universe**
Edit in `sentiment_trading_system.py`:
```python
# Screen just semiconductors
universe = ['NVDA', 'AMD', 'INTC', 'MU', 'AVGO', 'QCOM', 'TSM', 'ASML']

# Or screen everything
universe = get_large_stock_universe()  # 200+ stocks
```

### **Adjust Sensitivity**
```python
# More aggressive (more trades)
if composite >= 65:  # Lower threshold
    signal = 'BUY'

# More conservative (fewer, higher quality trades)
if composite >= 85:  # Higher threshold
    signal = 'BUY'
```

### **Adjust Weights**
```python
weights = {
    'analyst': 0.6,    # Trust analysts more
    'news': 0.3,       
    'reddit': 0.1      # Trust Reddit less
}
```

---

## 📈 USAGE EXAMPLES

### **Example 1: Screen for Opportunities**
```python
from sentiment_trading_system import SentimentTradingSystem, get_large_stock_universe

system = SentimentTradingSystem()
universe = get_large_stock_universe()

# Screen top 100 stocks
top_picks, all_data = system.screen_universe(universe[:100], top_n=10)

# View results
print(top_picks[['ticker', 'signal', 'composite_score']])
```

### **Example 2: Backtest a Specific Stock**
```python
from datetime import datetime

# Backtest NVDA with sentiment signals
results = system.backtest_signal_based(
    ticker='NVDA',
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2024, 12, 31),
    check_interval_days=7  # Check sentiment weekly
)

print(f"Return: {results['total_return']:.1f}%")
```

### **Example 3: Focus on Specific Sector**
```python
# Just tech stocks
tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'TSLA', 'META']
top_tech, _ = system.screen_universe(tech_stocks, top_n=3)
```

---

## 🎯 EXPECTED PERFORMANCE

### **Advantages Over Old System:**

1. **Catches Early Moves**
   - Old: Wait for 50/200 MA cross (late)
   - New: Enter on Strong Buy signals (early)

2. **Better Stock Selection**
   - Old: Just momentum ranking
   - New: Multi-source validation (analysts + social + news)

3. **Larger Opportunity Set**
   - Old: 39 stocks
   - New: 200+ stocks screened

4. **Real Sentiment**
   - Old: Fake sentiment (price momentum)
   - New: Actual buzz, analyst opinions, news

### **Example Scenario:**

```
PLTR gets Strong Buy ratings from 5 analysts:
  → Composite score: 88
  → Reddit buzz: 50+ mentions on WSB
  → News: "Palantir wins major contract"
  
OLD SYSTEM: 
  Might not even screen PLTR
  If it does, waits for MA cross (weeks later)
  
NEW SYSTEM:
  ✓ Identifies immediately (within 24 hours)
  ✓ Enters on Strong Buy signal
  ✓ Captures the initial surge
  ✓ Holds until sentiment turns
```

---

## ⚙️ API NOTES

### **Reddit API (Pushshift)**
- **Free**: Yes
- **Rate Limit**: ~60 requests/minute
- **Delay needed**: 0.5 seconds between requests
- **Data**: Last 7 days of posts/mentions

### **Yahoo Finance API (yfinance)**
- **Free**: Yes
- **Rate Limit**: Be reasonable (~1 request/second)
- **Data**: Analyst ratings, news, prices
- **Reliability**: Very good

### **No API Keys Required!**
All data sources are free and don't require registration.

---

## 🔄 WORKFLOW

### **Daily/Weekly Workflow:**

```
1. SCREEN (Morning):
   python sentiment_trading_system.py
   → Get top 10 Strong Buy signals

2. RESEARCH (Afternoon):
   Review each stock:
   - Check why analysts are bullish
   - Read news articles
   - Verify Reddit buzz is legitimate
   - Look at chart

3. EXECUTE (Next Day):
   Buy top 3-5 stocks with highest scores
   
4. MONITOR (Weekly):
   Check sentiment scores
   Exit if score drops to SELL
   
5. REPEAT (Weekly):
   Screen again for new opportunities
```

---

## 📊 COMPARISON: OLD vs NEW

| Feature | Old System | New System |
|---------|-----------|------------|
| **Sentiment Source** | Price momentum (fake) | Reddit + Analysts + News (real) |
| **Universe** | 39 stocks | 200+ stocks |
| **Entry Signal** | 50-day MA crosses 200-day | Strong Buy from multiple sources |
| **Exit Signal** | 50-day crosses below 200-day | Sell rating appears |
| **Speed** | Very slow (weeks lag) | Fast (captures buzz early) |
| **Hold Period** | Until MA cross | Until sentiment changes |
| **Best For** | Major trends | Momentum plays + fundamental strength |

---

## 💡 ADVANCED FEATURES

### **1. Multi-Stock Portfolio**
```python
# Get top 5 signals
top_5 = top_picks.head(5)['ticker'].tolist()

# Allocate 20% to each
for ticker in top_5:
    # Buy $20K worth of each
    ...
```

### **2. Position Sizing by Confidence**
```python
# Bigger position for Strong Buy
if signal == 'STRONG_BUY':
    allocation = 0.30  # 30% of capital
elif signal == 'BUY':
    allocation = 0.15  # 15% of capital
```

### **3. Sector Diversification**
```python
# Force max 2 stocks per sector
top_diverse = select_diverse_portfolio(top_picks, max_per_sector=2)
```

---

## 🚨 IMPORTANT NOTES

### **Rate Limits:**
- Reddit API: Don't hammer it (0.5s delay)
- Yahoo Finance: Be polite (1s delay recommended)
- Screening 200 stocks takes ~5-10 minutes

### **Sentiment Reliability:**
- Analysts: Most reliable (50% weight)
- News: Fairly reliable (30% weight)
- Reddit: Noisy but shows buzz (20% weight)

### **When to Use:**
- ✅ Finding momentum leaders early
- ✅ Catching analyst upgrades
- ✅ Riding social media buzz
- ❌ NOT for long-term value investing
- ❌ NOT for dividend stocks

---

## 🎯 BOTTOM LINE

This new system is **completely different** from the old one:

**What you get:**
- Real sentiment from social media & analysts
- Large universe (200+ stocks screened)
- Fast signals (catch moves early)
- Strong Buy focus (high-conviction picks)
- Hold until sentiment changes

**What you lose:**
- The simple 50/200 MA (but it was too slow anyway)
- Fake "sentiment" that was just momentum

**Expected outcome:**
- Better entry timing
- More opportunities
- Higher quality signals
- Actually uses real data!

---

## 🚀 NEXT STEPS

1. **Run the screener:**
   ```bash
   python sentiment_trading_system.py
   ```

2. **Review top 10 stocks**
   - Check why they're rated Strong Buy
   - Verify the sentiment makes sense

3. **Backtest promising picks:**
   ```python
   system.backtest_signal_based('NVDA', start, end)
   ```

4. **Refine parameters:**
   - Adjust score thresholds
   - Change weight allocation
   - Add filters (volume, price, etc.)

5. **Paper trade for 1 month**
   - Test with fake money first
   - Track actual performance
   - Refine before going live

**This is a REAL sentiment system using actual social/analyst data!** 🎯
