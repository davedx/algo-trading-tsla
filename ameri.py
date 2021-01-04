# Import the client
from td.client import TDClient

consumer_key = ''

# Create a new session, credentials path is optional.
TDSession = TDClient(
    client_id = consumer_key,
    redirect_uri = 'http://localhost',
)

# Login to the session
TDSession.login()

# Grab real-time quotes for 'MSFT' (Microsoft)
msft_quotes = TDSession.get_quotes(instruments=['MSFT'])
print(msft_quotes)

# Grab real-time quotes for 'AMZN' (Amazon) and 'SQ' (Square)
multiple_quotes = TDSession.get_quotes(instruments=['AMZN','SQ'])
print(multiple_quotes)
