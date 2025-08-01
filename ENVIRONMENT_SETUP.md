# Environment Setup and Logging Documentation

## Overview
This document describes the environment variable setup and comprehensive logging implementation for the Crypto Portfolio Tracker.

## Environment Variables

### Setup
1. **Create `.env` file** in the project root:
```bash
# API Keys
ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

2. **Install python-dotenv**:
```bash
pip install python-dotenv==1.0.0
```

### Usage
The application now uses environment variables instead of hardcoded API keys:

- **crypt_1.py**: Uses `os.getenv('ETHERSCAN_API_KEY')`
- **app.py**: Uses `os.getenv('ETHERSCAN_API_KEY')` for all Etherscan API calls

## Logging Implementation

### Backend Logging (Python)

#### File: `app.py`
- **Log Configuration**: Set up with file and console output
- **API Endpoints**: Comprehensive logging for all endpoints
- **Error Handling**: Full stack traces and detailed error messages
- **Request Tracking**: Logs all API calls with parameters and responses

#### File: `crypt_1.py`
- **ETH Balance**: Logs balance retrieval attempts and results
- **ETH Price**: Logs price fetching from CoinGecko
- **Error Context**: Detailed error logging with API responses

#### File: `price_history.py`
- **Logging Infrastructure**: Added logging setup for price history functions

### Frontend Logging (JavaScript)

#### File: `templates/wallet.html`
- **Console Logging**: Detailed logging for all API calls
- **HTTP Status**: Logs response status codes and error messages
- **API Responses**: Logs full response data for debugging
- **Error Context**: Enhanced error messages with specific details

## Log Files

### `app.log`
- **Location**: Project root directory
- **Content**: All server-side logs including API calls, errors, and debugging info
- **Format**: Timestamped entries with log levels (INFO, ERROR)

### Console Output
- **Real-time**: Logs appear in terminal during development
- **Debugging**: Immediate feedback for API issues

## Key Features

### Security
- ✅ API keys stored in `.env` file (not in code)
- ✅ `.env` file in `.gitignore` (not committed to version control)
- ✅ Environment variable validation

### Debugging
- ✅ Comprehensive error logging
- ✅ API response tracking
- ✅ Request/response correlation
- ✅ Performance monitoring

### Error Handling
- ✅ HTTP status code checking
- ✅ API error message extraction
- ✅ Graceful error recovery
- ✅ User-friendly error messages

## Usage Examples

### Backend Logs
```python
# Example log entries
2025-08-01 00:52:22,778 - __main__ - INFO - Getting wallet data for address: 0xe688b84b23f322a994A53dbF8E15FA82CDB71127
2025-08-01 00:52:22,793 - __main__ - INFO - Retrieved 10 transactions for 0xe688b84b23f322a994A53dbF8E15FA82CDB71127
```

### Frontend Logs
```javascript
// Example console logs
console.log('Wallet API response status:', walletResponse.status);
console.error('Wallet API error:', walletData);
```

## Troubleshooting

### Common Issues

1. **Environment Variable Not Found**
   - Check `.env` file exists in project root
   - Verify `ETHERSCAN_API_KEY` is set correctly
   - Ensure `python-dotenv` is installed

2. **API Errors**
   - Check `app.log` for detailed error messages
   - Verify API key is valid and has sufficient quota
   - Review HTTP status codes in logs

3. **Frontend Issues**
   - Open browser developer tools (F12)
   - Check console for JavaScript errors
   - Review network tab for API call failures

## Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Monitor logs regularly** for debugging and performance
4. **Test API endpoints** before deploying to production
5. **Keep logs organized** and rotate them periodically 