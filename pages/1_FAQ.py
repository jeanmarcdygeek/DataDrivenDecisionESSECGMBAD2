import streamlit as st

st.set_page_config(layout="wide", page_title="FAQ - Insurance Pricing Basics")

st.title("📚 FAQ: Basics to Know About Insurance Pricing")

st.markdown("""
This page provides essential information about insurance pricing fundamentals to help you make informed strategic decisions.
""")

st.header("1. What is Insurance Premium Pricing?")
st.markdown("""
**Insurance premium pricing** is the process of determining how much customers should pay for their insurance coverage. 
The premium must cover:
- **Expected Losses**: The amount the insurer expects to pay out in claims
- **Operating Costs**: Administrative expenses, commissions, and overhead
- **Profit Margin**: The target profit for the insurance company
- **Risk Loading**: Additional amount to account for uncertainty and volatility

**Formula**: Premium = Expected Loss + Operating Costs + Profit Margin + Risk Loading
""")

st.header("2. Key Components of Insurance Pricing")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Expected Loss")
    st.markdown("""
    - Calculated as: **Insured Amount × Probability of Loss**
    - Represents the average amount the insurer expects to pay
    - Based on historical data and actuarial models
    - Example: If a property worth €100,000 has a 2% chance of loss, expected loss = €2,000
    """)

with col2:
    st.subheader("Operating Costs")
    st.markdown("""
    - Fixed and variable costs of running the insurance business
    - Includes: salaries, marketing, technology, regulatory compliance
    - Typically expressed as a percentage of premium or a fixed amount per policy
    - Can vary by distribution channel and customer segment
    """)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Profit Margin")
    st.markdown("""
    - The target profit the insurer wants to achieve
    - Ensures financial sustainability and return to shareholders
    - Can be set at portfolio level or by product/segment
    - Must be competitive to maintain market position
    """)

with col4:
    st.subheader("Risk Loading")
    st.markdown("""
    - Additional premium to account for uncertainty
    - Protects against adverse deviations from expected losses
    - Higher for volatile or unpredictable risks
    - Helps maintain solvency during bad years
    """)

st.header("3. Pricing Strategies")

st.subheader("Risk-Based Pricing")
st.markdown("""
- Premiums vary based on individual risk characteristics
- Higher risk = Higher premium
- More accurate and fair pricing
- Requires good data and sophisticated models
""")

st.subheader("Geographic Pricing")
st.markdown("""
- Premiums vary by location (e.g., arrondissement, city, region)
- Accounts for local risk factors:
  - Crime rates
  - Natural disaster exposure
  - Economic conditions
  - Demographics
- Allows for market segmentation and competitive positioning
""")

st.subheader("Portfolio-Level Pricing")
st.markdown("""
- Set overall profit target for entire portfolio
- Allocate target across segments/regions
- Balance between:
  - Profitability objectives
  - Market competitiveness
  - Growth targets
  - Risk diversification
""")

st.header("4. Key Metrics to Monitor")

metrics_cols = st.columns(3)

with metrics_cols[0]:
    st.markdown("""
    **Loss Ratio**
    - Losses / Premiums
    - Target: < 70% (varies by line of business)
    - Measures underwriting profitability
    """)

with metrics_cols[1]:
    st.markdown("""
    **Combined Ratio**
    - (Losses + Expenses) / Premiums
    - Target: < 100% for profitability
    - Comprehensive profitability measure
    """)

with metrics_cols[2]:
    st.markdown("""
    **Profit Margin**
    - (Premium - Expected Loss - Costs) / Premium
    - Measures efficiency and profitability
    - Higher margin = more profitable
    """)

st.header("5. Pricing Allocation Strategies")

st.subheader("Equal Allocation")
st.markdown("""
- Divide target equally across all segments
- Simple but may not reflect risk differences
- Can lead to over/under-pricing in some areas
""")

st.subheader("Proportional to Exposure")
st.markdown("""
- Allocate based on insured amounts or number of customers
- Larger segments get larger share of target
- Maintains relative pricing structure
""")

st.subheader("Risk-Adjusted Allocation")
st.markdown("""
- Allocate more to higher-risk areas
- Reflects actual risk profile
- More sophisticated and accurate
- Requires good risk assessment
""")

st.subheader("Market-Based Allocation")
st.markdown("""
- Consider competitive position in each area
- Adjust allocation based on market conditions
- Balance profitability with growth objectives
- May require market research
""")

st.header("6. Common Challenges in Insurance Pricing")

st.markdown("""
- **Data Quality**: Incomplete or inaccurate data affects pricing accuracy
- **Regulatory Constraints**: Some jurisdictions limit pricing flexibility
- **Market Competition**: Need to balance profitability with competitiveness
- **Risk Assessment**: Difficulty in accurately predicting future losses
- **Customer Behavior**: Price sensitivity and elasticity vary by segment
- **External Factors**: Economic conditions, climate change, etc.
""")

st.header("7. Best Practices")

st.markdown("""
✅ **Use data-driven approaches**: Base decisions on historical data and statistical models
✅ **Regular review**: Update pricing based on emerging trends and results
✅ **Segmentation**: Price differently for different risk profiles
✅ **Transparency**: Ensure pricing logic is explainable and defensible
✅ **Balance objectives**: Consider profitability, growth, and market position
✅ **Monitor results**: Track actual vs. expected outcomes and adjust accordingly
""")

st.info("💡 **Tip**: In this workshop, you'll apply these concepts to allocate a profit target across Paris arrondissements. Consider risk profiles, market conditions, and strategic objectives when making your allocation decisions.")

