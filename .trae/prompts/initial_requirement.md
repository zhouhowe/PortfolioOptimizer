## Requirements 
 
 ### Strategy Optimizer (P0) 
 
 Develop an app that can back-test the effect of a combination of LEAP options and Wheel strategy using historical data. 
 
 #### LEAP Strategy (P0) 
 Initial LEAP strategy is as follows: 
 
 1. Pick a target equity, initially, consider QQQ and TSLA as starting point 
 2. Set up a portfolio with x% target equity, y% LEAP call of target equity with 12 to 18 months expiration and with Delta `D`, (1-x-y)% cash. 
 3. User can choose the following options to rebalance the portfolio: 
 	 1. when one of the three asset type is off from preset allocation target by `delta` % 
 	 2. when target equity is down by `delta_down` or up by `delta_up` 
  4. Close the LEAP calls when profit or loss reaches the following limit with each time window 
  
 | Time to Expiration | Profit Loss | Profit Limit | 
 | ------------------ | ----------- | ------------ | 
 | >6 months          | p_6         | l_6          | 
 | 3 to 6 months      | p_3         | l_9          | 
 | < 3 months         | p_0         | l_0          | 
 #### Wheel Strategy (P1) 
 
 Include "Wheel strategy" to sell put and call options depending on the target equity price (MA10/MA20/MA30/MA60 price as signal). Does need to implement for the P0 product, but keep in mind for future implementation 
 
 #### Parameters 
 Asides from the above strategy related parameters, we have the following input parameters: 
 1. Initial Portfolio size ($) 
 2. Monthly cash withdraw amount - certain dollar amount needs to be withdrawn to cover monthly spending ($) 
 
 
 ### Simulator (P1) 
 This component can be used to generate a few scenarios (bear market, bull market, etc.) in lieu of actual historical data. It can be used to test the robustness of strategy. Implement using common models for stock price (random walk model?) 
 
 Now implement P0 features first. Ask clarifying questions if there are ambiguities