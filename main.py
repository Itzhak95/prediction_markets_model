# PACKAGES

import numpy as np
import math
from random import randint
import pandas as pd

# Number of simulations
s = 10000

big_prices = []
for sim in range(s):

    # SET THE INITIAL PARAMETERS

    # Initial wealth
    w = 100

    # Initial reserves of the AMM
    y = 1000
    n = 1000

    # Population size
    size = 10

    # Number of trading opportunities (not including the manipulation)
    final_time = 200

    # Time of manipulation
    man_time = 100

    # Learning parameter
    l = 0

    # FUNCTIONS

    # This function returns the optimal amount to spend on yes shares and how many shares this buys you
    # [Calling the function will also update the AMM's reserves]
    def optimal_yes(p, w_t):
        global y, n
        if p == n/(n + y):
            optimal_spend = 0
        elif p == 1:
            optimal_spend = w_t
        else:
            numerator = n*(y - 2*(p - 1)*w_t) - math.sqrt(n*y * (n * (-4 * p ** 2 * w_t + 4 * p * w_t + y) - 4 * (p - 1) * p * w_t * (w_t + y)))
            denominator = 2 * (p - 1) * (w_t + y)
            optimal_spend = numerator / denominator
        optimal_shares = (optimal_spend*(n + optimal_spend + y))/(n + optimal_spend)
        # Update the reserves
        y += optimal_spend - optimal_shares
        n += optimal_spend
        return [optimal_spend, optimal_shares]

    # This function does the same thing for no shares [again, the function also updates the reserves]
    def optimal_no(p, w_t):
        global y, n
        if p == n/(n + y):
            optimal_spend = 0
        elif p == 0:
            optimal_spend = w_t
        else:
            numerator = np.sqrt(n * y * (n * (-4 * p**2 * w_t + 4 * p * w_t + y) - 4 * (p - 1) * p * w_t * (w_t + y))) - n*y - 2*p*w_t*y
            denominator = 2 * p * (n + w_t)
            optimal_spend = numerator / denominator
        optimal_shares = (optimal_spend*(n + optimal_spend + y))/(y + optimal_spend)
        # Update the reserves
        y += optimal_spend
        n += optimal_spend - optimal_shares
        return [optimal_spend, optimal_shares]

    # This function allows you to sell g yes shares:

    def sell_yes(g):
        global y, n
        x = 0.5 * (-math.sqrt(g**2 - 2*g*(n-y) + (n+y)**2) + g + n + y)
        # Update the reserves
        y += g - x
        n -= x
        return x

    # This function allows you to sell g no shares:

    def sell_no(g):
        global y, n
        x = 0.5 * (-math.sqrt(g**2 - 2*g*(y-n) + (n+y)**2) + g + n + y)
        # Update the reserves
        y -= x
        n += g - x
        return x

    # This function pushes the 'price' up by D

    def manipulate(D):
        global y, n
        numerator = -math.sqrt(-D**2 * n**3 * y - 2 * D**2 * n**2 * y**2 - D**2 * n * y**3 - D * n**3 * y + D * n * y**3 + n**2 * y**2) - D * n**2 - D * n * y + n * y
        denominator = D*n + D*y - y
        x = numerator/denominator
        # Update the reserves
        y = y*n/(n + x)
        n = n+x

    # BUILD THE POPULATION

    beliefs = [i/size for i in range(size + 1)]
    wealth = [w for i in range(size + 1)]
    assets = [0 for i in range(size + 1)]

    # RUN THE SIMULATION

    prices = []
    prices.append(n/(n+y))

    for t in range(final_time):
        print(f'Time: {t}')
        print('Reserves')
        print(y)
        print(n)
        print(f'Product: {y*n}')
        # Randomly pick an agent
        agent = randint(0, size)
        # Sell holdings if necessary
        agent_assets = assets[agent]
        print(f' Assets: {assets}')
        print(f'Their assets: {agent_assets}')
        if agent_assets > 0:
            print(f'Has {agent_assets} yes shares')
            # Give the agent the cash
            wealth[agent] += sell_yes(agent_assets)
            print(f'Wealth: {wealth}')
            print('Reserves')
            print(y)
            print(n)
            # Reduce the agent's assets
            assets[agent] = 0
        elif agent_assets < 0:
            print(f'Has {-agent_assets} no shares')
            # Give the agent the cash
            wealth[agent] += sell_no(-agent_assets)
            print(f'Wealth: {wealth}')
            print('Reserves')
            print(y)
            print(n)
            # Reduce the agent's assets
            assets[agent] = 0
        # Find the optimal purchases
        # If necessary, update their beliefs
        price = n/(n + y)
        belief = l * price + (1 - l) * beliefs[agent]
        print(f'Belief {belief}')
        if belief > n/(n + y):
            print(f'Wants to buy yes')
            # Buy yes shares
            purchase = optimal_yes(belief, wealth[agent])
            print(f'Purchase: {purchase}')
            wealth[agent] -= purchase[0]
            print(f'Wealth: {wealth}')
            assets[agent] += purchase[1]
            print(f'Assets: {assets}')
        elif belief < n/(n + y):
            print(f'Wants to buy no')
            # Buy no shares
            purchase = optimal_no(belief, wealth[agent])
            print(f'Purchase: {purchase}')
            wealth[agent] -= purchase[0]
            print(f'Wealth: {wealth}')
            assets[agent] -= purchase[1]
            print(f'Assets: {assets}')
        prices.append(n/(n+y))
        print(f'Price: {n/(n + y)}')
        if t == man_time:
            manipulate(0.05)
            prices.append(n / (n + y))
            print(f'Price: {n/(n + y)}')
    print('End of simulation')
    big_prices.append(prices)

print('RESULTS')

average_prices = [sum(prices) / len(prices) for prices in zip(*big_prices)]
high_prices = [np.percentile(prices, 95) for prices in zip(*big_prices)]
low_prices = [np.percentile(prices, 5) for prices in zip(*big_prices)]

print('Average prices')

for element in average_prices:
    print(element)

# print(' ')
# print('High prices')
#
# for element in high_prices:
#     print(element)
#
# print(' ')
# print('Low prices')

# for element in low_prices:
#     print(element)

df = pd.DataFrame(big_prices)

df.to_excel('output.xlsx', index=False, header=False)
