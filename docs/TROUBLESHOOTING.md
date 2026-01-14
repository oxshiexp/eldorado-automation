# Troubleshooting Guide

## Common Issues and Solutions

### 1. Scraping Issues

#### Problem: "No products found"
**Symptoms**: Scraper returns empty results

**Solutions**:
- Verify the seller URL is correct and active
- Check if the seller has any active listings
- Website structure may have changed - update CSS selectors in `scraper.py`
- Try with a different seller URL first

```bash
# Test with a known working seller
python scraper.py --url "https://www.eldorado.gg/users/Alayon?category=Currency"
```

#### Problem: Rate limiting / 429 errors
**Symptoms**: "Too many requests" or blocked IP

**Solutions**:
- Increase delay between requests in `scraper.py` (line 45):
```python
time.sleep(2)  # Increase from 1 to 2 seconds
```
- Use proxy rotation (add proxy support)
- Reduce scraping frequency

### 2. API Issues

#### Problem: "Invalid API key"
**Symptoms**: 401 Unauthorized errors

**Solutions**:
- Verify API key is correct in `.env` file
- Check if API key has expired
- Regenerate API key from seller dashboard
- Ensure no extra spaces in `.env` file

```bash
# Test API key
curl -H "Authorization: Bearer YOUR_KEY" https://api.eldorado.gg/v1/listings
```

#### Problem: "API endpoint not found"
**Symptoms**: 404 errors on API calls

**Solutions**:
- Verify you have Seller API access (not all sellers have it)
- Check if you're using correct API version
- Contact Eldorado support for API documentation
- API may not be publicly available yet

### 3. Upload Issues

#### Problem: "Product upload failed"
**Symptoms**: Listings don't appear on your profile

**Solutions**:
- Verify seller account is verified
- Check if product data matches required format
- Ensure prices are within acceptable range
- Verify stock quantities are valid

```python
# Validate listing data before upload
listing = {
    "game": "osrs",  # Must be valid game slug
    "price_per_unit": 0.45,  # Must be > 0
    "stock": 1000  # Must be > 0
}
```

#### Problem: "Bulk upload partial failure"
**Symptoms**: Some products uploaded, others failed

**Solutions**:
- Check error messages for specific failed items
- Validate all required fields are present
- Reduce batch size (from 100 to 50)
- Retry failed items individually

### 4. Monitoring Issues

#### Problem: "Changes not detected"
**Symptoms**: Price changes missed by monitor

**Solutions**:
- Verify monitoring interval is reasonable (not too long)
- Check if comparison logic is working:
```python
# Debug price comparison
print(f"Old: {old_price}, New: {new_price}, Changed: {old_price != new_price}")
```
- Ensure price history is being saved correctly
- Verify float comparison (use tolerance for small differences)

#### Problem: "Too many notifications"
**Symptoms**: Spam of notification emails

**Solutions**:
- Increase change threshold:
```python
# Only notify if price changes by more than 5%
if abs(new_price - old_price) / old_price > 0.05:
    send_notification()
```
- Implement notification cooldown period
- Batch notifications (send once per hour instead of instant)

### 5. Installation Issues

#### Problem: "Module not found"
**Symptoms**: ImportError when running scripts

**Solutions**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or install individually
pip install requests beautifulsoup4 lxml pandas python-dotenv
```

#### Problem: "Python version incompatible"
**Symptoms**: Syntax errors or feature not available

**Solutions**:
```bash
# Check Python version (needs 3.8+)
python --version

# Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 6. Performance Issues

#### Problem: "Scraping too slow"
**Symptoms**: Takes hours to scrape one seller

**Solutions**:
- Reduce delay between requests (carefully):
```python
time.sleep(0.5)  # Reduce from 1 second
```
- Implement concurrent scraping (use threading)
- Cache results that don't change often
- Scrape only specific categories instead of all

#### Problem: "High memory usage"
**Symptoms**: Script crashes with MemoryError

**Solutions**:
- Process products in batches instead of loading all at once
- Clear data structures after processing
- Use generators instead of lists for large datasets
```python
# Instead of loading all in memory
for product in process_products_generator(url):
    upload_product(product)
```

### 7. Automation Issues

#### Problem: "Scheduled tasks not running"
**Symptoms**: Cron jobs or triggers not executing

**Solutions**:
- Verify cron syntax is correct:
```bash
# Every 6 hours
0 */6 * * *

# Check cron logs
tail -f /var/log/cron
```
- Ensure script has execute permissions:
```bash
chmod +x automation.py
```
- Check if environment variables are available in cron context

#### Problem: "Automation stops after errors"
**Symptoms**: Script exits on first error

**Solutions**:
- Wrap in try-catch with retry logic:
```python
for attempt in range(3):
    try:
        result = scrape_and_upload()
        break
    except Exception as e:
        if attempt == 2:
            log_error(e)
        time.sleep(60)  # Wait before retry
```

### 8. Data Issues

#### Problem: "Prices parsed incorrectly"
**Symptoms**: $450 instead of $0.45

**Solutions**:
- Check decimal parsing logic
- Verify currency symbols are handled correctly
- Add validation after parsing:
```python
if price > 100:  # Suspiciously high for per-unit price
    print(f"Warning: Unusual price detected: ${price}")
```

#### Problem: "Character encoding issues"
**Symptoms**: Special characters display as ???

**Solutions**:
```python
# Ensure UTF-8 encoding
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
```

## Getting Help

If none of these solutions work:

1. **Check Logs**: Review error messages in detail
2. **Enable Debug Mode**: Run with verbose logging
3. **Test Components Individually**: Isolate the problem
4. **Update Dependencies**: `pip install -r requirements.txt --upgrade`
5. **Contact Support**: 
   - GitHub Issues: [Create an issue](https://github.com/yourusername/eldorado-automation/issues)
   - Email: your-email@example.com
   - Include: error message, Python version, OS, steps to reproduce

## Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or run with verbose flag:
```bash
python automation.py scrape --url URL --verbose
```

## Useful Debug Commands

```bash
# Test scraping only
python scraper.py --url "SELLER_URL" --output test.json

# Test API connection
python -c "from uploader import EldoradoUploader; u = EldoradoUploader('API_KEY'); print(u.test_connection())"

# Validate product data
python -c "import json; data = json.load(open('scraped_products.json')); print(f'{len(data)} products loaded')"

# Check environment variables
python -c "import os; print(os.getenv('ELDORADO_API_KEY', 'NOT SET'))"
```

## Best Practices to Avoid Issues

1. **Always validate data** before uploading
2. **Use try-catch blocks** for external calls
3. **Log everything** for debugging
4. **Test with small batches** first
5. **Monitor rate limits** proactively
6. **Keep backups** of configurations
7. **Version control** your changes
8. **Document** any customizations you make

---

**Remember**: When in doubt, start with the simplest test case and gradually increase complexity.
