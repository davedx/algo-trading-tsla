# Algo Trading TSLA

Q: What is this?

A: An algorithmic trading script using technical analysis and back tested with TSLA stock data

It uses a simple EMA crossover strategy which aborts the buy if the RSI indicates the stock is overbought.

The script does a grid search to find the best parameters for the EMA and RSI algos.

It back tests with price data scraped from yahoo finance (the ydl.py script).
