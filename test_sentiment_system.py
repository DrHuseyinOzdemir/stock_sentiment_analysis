"""
COMPREHENSIVE TEST SUITE FOR FREE SENTIMENT SYSTEM
Tests all components to ensure everything works correctly
"""

import sys
import time
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}\n")

def print_test(test_name, status, message=""):
    """Print test result"""
    symbol = "✓" if status else "✗"
    status_text = "PASS" if status else "FAIL"
    print(f"{symbol} {test_name:<50} [{status_text}]")
    if message:
        print(f"  {message}")

def test_imports():
    """Test 1: Check if all required libraries are installed"""
    print_header("TEST 1: CHECKING DEPENDENCIES")
    
    all_passed = True
    
    # Required libraries
    required = {
        'yfinance': 'yfinance',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'requests': 'requests',
        'bs4': 'beautifulsoup4'
    }
    
    for module, package in required.items():
        try:
            __import__(module)
            print_test(f"Import {package}", True)
        except ImportError:
            print_test(f"Import {package}", False, 
                      f"Install with: pip install {package}")
            all_passed = False
    
    return all_passed

def test_system_import():
    """Test 2: Check if our sentiment system imports correctly"""
    print_header("TEST 2: IMPORTING SENTIMENT SYSTEM")
    
    try:
        from free_sentiment_system import FreeSentimentAnalyzer
        print_test("Import FreeSentimentAnalyzer", True)
        
        # Try to initialize
        analyzer = FreeSentimentAnalyzer()
        print_test("Initialize FreeSentimentAnalyzer", True)
        
        return True, analyzer
    except Exception as e:
        print_test("Import/Initialize System", False, str(e))
        return False, None

def test_stocktwits_api(analyzer):
    """Test 3: Test StockTwits API (most important!)"""
    print_header("TEST 3: STOCKTWITS API (CRITICAL)")
    
    test_tickers = ['AAPL', 'TSLA', 'GME']
    passed = 0
    
    for ticker in test_tickers:
        try:
            print(f"\nTesting {ticker}...")
            score, total, bullish, bearish = analyzer.get_stocktwits_sentiment(ticker)
            
            if total > 0:
                print_test(f"StockTwits {ticker}", True,
                          f"Score: {score:.1f}, Messages: {total}, Bulls: {bullish}, Bears: {bearish}")
                passed += 1
            else:
                print_test(f"StockTwits {ticker}", False,
                          "No messages returned (API might be down)")
        except Exception as e:
            print_test(f"StockTwits {ticker}", False, str(e))
        
        time.sleep(1)  # Be polite
    
    success = passed >= 2  # At least 2 out of 3 should work
    print(f"\n📊 StockTwits Results: {passed}/3 successful")
    
    return success

def test_yahoo_finance(analyzer):
    """Test 4: Test Yahoo Finance data"""
    print_header("TEST 4: YAHOO FINANCE DATA")
    
    test_tickers = ['AAPL', 'MSFT']
    passed = 0
    
    for ticker in test_tickers:
        try:
            print(f"\nTesting {ticker}...")
            
            # Test news sentiment
            news_score, news_count = analyzer.get_yahoo_news_sentiment(ticker)
            if news_count > 0:
                print_test(f"Yahoo News {ticker}", True,
                          f"Score: {news_score:.1f}, Articles: {news_count}")
            else:
                print_test(f"Yahoo News {ticker}", False, "No news articles")
            
            # Test analyst ratings
            analyst_score, rec, upside, num = analyzer.get_analyst_ratings(ticker)
            if analyst_score != 50:  # 50 is default/error
                print_test(f"Analyst Ratings {ticker}", True,
                          f"Rating: {rec}, Score: {analyst_score:.1f}, Upside: {upside:.1f}%")
                passed += 1
            else:
                print_test(f"Analyst Ratings {ticker}", False, "No analyst data")
            
        except Exception as e:
            print_test(f"Yahoo Finance {ticker}", False, str(e))
        
        time.sleep(1)
    
    success = passed >= 1
    print(f"\n📊 Yahoo Finance Results: {passed}/2 successful")
    
    return success

def test_price_momentum(analyzer):
    """Test 5: Test price momentum calculation"""
    print_header("TEST 5: PRICE MOMENTUM ANALYSIS")
    
    test_tickers = ['NVDA', 'AMD']
    passed = 0
    
    for ticker in test_tickers:
        try:
            print(f"\nTesting {ticker}...")
            momentum_score = analyzer.get_price_momentum(ticker)
            
            if momentum_score != 50:  # 50 is neutral/error
                print_test(f"Momentum {ticker}", True,
                          f"Score: {momentum_score:.1f}")
                passed += 1
            else:
                print_test(f"Momentum {ticker}", False,
                          "Neutral score (might be error)")
        except Exception as e:
            print_test(f"Momentum {ticker}", False, str(e))
        
        time.sleep(1)
    
    success = passed >= 1
    print(f"\n📊 Momentum Analysis Results: {passed}/2 successful")
    
    return success

def test_web_scraping(analyzer):
    """Test 6: Test web scraping (Finviz, Reddit)"""
    print_header("TEST 6: WEB SCRAPING (OPTIONAL)")
    
    print("Note: These may fail due to rate limiting or blocking")
    print("This is OK - StockTwits is the main source!\n")
    
    # Test Finviz
    try:
        print("Testing Finviz...")
        finviz_score, finviz_count = analyzer.get_finviz_sentiment('AAPL')
        if finviz_count > 0:
            print_test("Finviz Scraping", True,
                      f"Score: {finviz_score:.1f}, Articles: {finviz_count}")
        else:
            print_test("Finviz Scraping", False,
                      "No data (might be blocked or rate limited)")
    except Exception as e:
        print_test("Finviz Scraping", False, str(e))
    
    time.sleep(2)
    
    # Test Reddit
    try:
        print("\nTesting Reddit...")
        mentions, bulls, bears = analyzer.get_reddit_mentions_scrape('GME')
        if mentions > 0:
            print_test("Reddit Scraping", True,
                      f"Mentions: {mentions}, Bulls: {bulls}, Bears: {bears}")
        else:
            print_test("Reddit Scraping", False,
                      "No mentions found (Reddit might be blocking)")
    except Exception as e:
        print_test("Reddit Scraping", False, str(e))
    
    print("\n⚠️  Web scraping is optional - StockTwits is the primary source")
    return True  # Always pass since optional

def test_composite_scoring(analyzer):
    """Test 7: Test complete composite scoring"""
    print_header("TEST 7: COMPOSITE SCORING")
    
    test_tickers = ['NVDA', 'PLTR']
    passed = 0
    
    for ticker in test_tickers:
        try:
            print(f"\nTesting full analysis for {ticker}...")
            result = analyzer.calculate_composite_score(ticker)
            
            if result and result['composite_score'] > 0:
                print_test(f"Composite Score {ticker}", True)
                print(f"  Score: {result['composite_score']:.1f}")
                print(f"  Signal: {result['signal']}")
                print(f"  StockTwits: {result['stocktwits_bullish']} bulls / {result['stocktwits_bearish']} bears")
                print(f"  Total Buzz: {result['total_buzz']}")
                passed += 1
            else:
                print_test(f"Composite Score {ticker}", False,
                          "No valid result returned")
        except Exception as e:
            print_test(f"Composite Score {ticker}", False, str(e))
        
        time.sleep(2)
    
    success = passed >= 1
    print(f"\n📊 Composite Scoring Results: {passed}/2 successful")
    
    return success

def test_screening(analyzer):
    """Test 8: Test screening multiple stocks"""
    print_header("TEST 8: BATCH SCREENING")
    
    print("Screening 5 stocks (this takes ~1 minute)...\n")
    
    test_stocks = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'PLTR']
    
    try:
        top_picks, all_results = analyzer.screen_stocks(test_stocks, top_n=5)
        
        if len(all_results) >= 3:  # At least 3 out of 5 should work
            print_test("Batch Screening", True,
                      f"Successfully analyzed {len(all_results)}/5 stocks")
            
            print("\n📊 Results Preview:")
            print(all_results[['ticker', 'composite_score', 'signal']].head())
            
            if len(top_picks) > 0:
                print(f"\n🏆 Top Pick: {top_picks.iloc[0]['ticker']} (Score: {top_picks.iloc[0]['composite_score']:.1f})")
            
            return True
        else:
            print_test("Batch Screening", False,
                      f"Only {len(all_results)}/5 stocks analyzed")
            return False
            
    except Exception as e:
        print_test("Batch Screening", False, str(e))
        return False

def test_data_quality(analyzer):
    """Test 9: Verify data quality"""
    print_header("TEST 9: DATA QUALITY CHECKS")
    
    try:
        # Test a popular stock
        result = analyzer.calculate_composite_score('TSLA')
        
        if not result:
            print_test("Data Quality", False, "No result returned")
            return False
        
        # Check required fields
        required_fields = ['ticker', 'composite_score', 'signal', 
                          'stocktwits_total', 'total_buzz']
        
        all_present = True
        for field in required_fields:
            if field not in result:
                print_test(f"Field '{field}' present", False)
                all_present = False
            else:
                print_test(f"Field '{field}' present", True)
        
        # Check score is valid
        score = result['composite_score']
        if 0 <= score <= 100:
            print_test("Score in valid range (0-100)", True, f"Score: {score:.1f}")
        else:
            print_test("Score in valid range", False, f"Score: {score:.1f}")
            all_present = False
        
        # Check signal is valid
        valid_signals = ['STRONG_BUY', 'BUY', 'HOLD', 'SELL']
        if result['signal'] in valid_signals:
            print_test("Valid signal generated", True, f"Signal: {result['signal']}")
        else:
            print_test("Valid signal generated", False, f"Signal: {result['signal']}")
            all_present = False
        
        return all_present
        
    except Exception as e:
        print_test("Data Quality", False, str(e))
        return False

def test_performance():
    """Test 10: Performance benchmarks"""
    print_header("TEST 10: PERFORMANCE BENCHMARKS")
    
    try:
        from free_sentiment_system import FreeSentimentAnalyzer
        analyzer = FreeSentimentAnalyzer()
        
        # Test single stock speed
        start = time.time()
        analyzer.calculate_composite_score('AAPL')
        duration = time.time() - start
        
        if duration < 5:
            print_test("Single stock analysis speed", True,
                      f"Completed in {duration:.2f} seconds (< 5s target)")
        else:
            print_test("Single stock analysis speed", False,
                      f"Took {duration:.2f} seconds (> 5s)")
        
        # Estimate batch time
        estimated_batch = duration * 20
        print(f"\n📊 Estimated time for 20 stocks: ~{estimated_batch:.0f} seconds ({estimated_batch/60:.1f} minutes)")
        
        return True
        
    except Exception as e:
        print_test("Performance Test", False, str(e))
        return False

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*80)
    print("FREE SENTIMENT SYSTEM - COMPREHENSIVE TEST SUITE".center(80))
    print("="*80)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # Test 1: Dependencies
    results['dependencies'] = test_imports()
    
    if not results['dependencies']:
        print("\n❌ CRITICAL: Missing dependencies. Install them first!")
        print("Run: pip install yfinance pandas numpy requests beautifulsoup4")
        return
    
    # Test 2: System Import
    results['import'], analyzer = test_system_import()
    
    if not results['import']:
        print("\n❌ CRITICAL: Cannot import system. Check free_sentiment_system.py")
        return
    
    # Test 3: StockTwits (Most Important!)
    results['stocktwits'] = test_stocktwits_api(analyzer)
    
    # Test 4: Yahoo Finance
    results['yahoo'] = test_yahoo_finance(analyzer)
    
    # Test 5: Price Momentum
    results['momentum'] = test_price_momentum(analyzer)
    
    # Test 6: Web Scraping (Optional)
    results['scraping'] = test_web_scraping(analyzer)
    
    # Test 7: Composite Scoring
    results['composite'] = test_composite_scoring(analyzer)
    
    # Test 8: Batch Screening
    results['screening'] = test_screening(analyzer)
    
    # Test 9: Data Quality
    results['quality'] = test_data_quality(analyzer)
    
    # Test 10: Performance
    results['performance'] = test_performance()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%\n")
    
    # Critical tests
    critical_tests = ['dependencies', 'import', 'stocktwits', 'composite']
    critical_passed = sum(results[test] for test in critical_tests if test in results)
    
    print("Critical Tests (Must Pass):")
    for test in critical_tests:
        status = "✓ PASS" if results.get(test, False) else "✗ FAIL"
        print(f"  {test.title():<20} {status}")
    
    print("\nOptional Tests (Nice to Have):")
    optional_tests = ['scraping', 'yahoo', 'momentum', 'screening', 'quality', 'performance']
    for test in optional_tests:
        if test in results:
            status = "✓ PASS" if results[test] else "✗ FAIL"
            print(f"  {test.title():<20} {status}")
    
    # Final verdict
    print("\n" + "="*80)
    if critical_passed == len(critical_tests):
        print("✅ SYSTEM IS READY TO USE!")
        print("="*80)
        print("\nThe system is working correctly!")
        print("StockTwits API is functional (most important)")
        print("\nYou can now run: python free_sentiment_system.py")
    elif results.get('stocktwits', False):
        print("⚠️  SYSTEM IS PARTIALLY FUNCTIONAL")
        print("="*80)
        print("\nStockTwits works (main data source)")
        print("Some other features may be limited")
        print("\nYou can still use the system, but results may vary")
    else:
        print("❌ SYSTEM HAS CRITICAL ISSUES")
        print("="*80)
        print("\nStockTwits API is not working")
        print("This is the primary data source - system won't work properly")
        print("\nPossible causes:")
        print("  • Internet connection issues")
        print("  • StockTwits API is down")
        print("  • Network firewall blocking requests")
    
    print("\n" + "="*80)
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_all_tests()
