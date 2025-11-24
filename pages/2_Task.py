import streamlit as st

st.set_page_config(layout="wide", page_title="Task - Workshop Assignment")

st.title("🎯 Workshop Task: Strategic Pricing Allocation")

st.markdown("""
## Overview
In this workshop, you will make data-driven strategic decisions about insurance pricing. 
Your goal is to determine how to allocate a target profit and operating costs across Paris arrondissements.
""")

st.header("📋 Your Mission")

st.markdown("""
You are the pricing manager for an insurance company operating in Paris. The board has set a **target profit and operating costs** 
that must be achieved across the entire customer portfolio. Your task is to decide how to split this target amongst the 20 Paris arrondissements.
""")

st.header("🎯 Objectives")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Primary Objectives:**
    1. ✅ Achieve the target profit + operating costs
    2. ✅ Allocate strategically across arrondissements
    3. ✅ Consider risk profiles and market conditions
    4. ✅ Make data-driven decisions
    """)

with col2:
    st.markdown("""
    **Strategic Considerations:**
    - Risk levels vary by arrondissement
    - Customer segments differ across areas
    - Market competitiveness varies
    - Growth opportunities differ
    """)

st.header("📊 Available Data")

st.markdown("""
You have access to comprehensive data including:

- **Customer Data**: Individual customer records with insured amounts, current premiums, and risk probabilities
- **Geographic Data**: Information aggregated by arrondissement
- **Risk Metrics**: Expected losses, probabilities, and exposure by location
- **Socioeconomic Data**: Median revenues, census data, and demographic information
- **Current Premiums**: Model premiums currently applied to customers
""")

st.header("🔧 How to Complete the Task")

st.subheader("Step 1: Understand the Current Situation")
st.markdown("""
1. Navigate to the **Dashboard** page
2. Explore the current metrics and customer characteristics
3. Review the portfolio metrics and distribution by arrondissement
4. Understand the risk profile of each arrondissement
""")

st.subheader("Step 2: Set Your Target")
st.markdown("""
1. On the Dashboard, you'll find the **Pricing Allocation** section
2. Enter your target profit + operating costs (in euros)
3. This is the total amount you need to generate across all customers
""")

st.subheader("Step 3: Allocate Across Arrondissements")
st.markdown("""
1. Use the allocation interface to distribute your target
2. You can allocate using different strategies:
   - **Manual**: Enter specific amounts for each arrondissement
   - **Proportional**: Allocate based on exposure, risk, or other factors
3. The system will validate that your allocation sums to the target
""")

st.subheader("Step 4: Analyze Results")
st.markdown("""
1. Review the resulting metrics after allocation:
   - New premiums by arrondissement
   - Profit margins achieved
   - Impact on customers
   - Portfolio-level outcomes
2. Compare with current situation
3. Adjust your allocation if needed
""")

st.subheader("Step 5: Present Your Strategy")
st.markdown("""
1. Document your allocation decisions
2. Explain your reasoning:
   - Why did you allocate more/less to certain arrondissements?
   - What factors influenced your decisions?
   - How does this align with strategic objectives?
3. Be prepared to defend your choices
""")

st.header("💡 Key Questions to Consider")

st.markdown("""
When making your allocation decisions, think about:

1. **Risk-Based**: Should higher-risk arrondissements contribute more to the target?
2. **Exposure-Based**: Should allocation be proportional to insured amounts or number of customers?
3. **Market-Based**: Are some arrondissements more price-sensitive than others?
4. **Strategic**: Are there growth opportunities in certain areas that justify different pricing?
5. **Fairness**: Is the allocation fair and defensible to stakeholders?
6. **Competitiveness**: Will the resulting premiums remain competitive in the market?
""")

st.header("📈 Success Criteria")

st.markdown("""
Your allocation will be evaluated on:

- ✅ **Accuracy**: Does the allocation sum to the target?
- ✅ **Reasoning**: Is the allocation strategy well-justified?
- ✅ **Data Usage**: Are decisions based on available data?
- ✅ **Strategic Thinking**: Does the allocation align with business objectives?
- ✅ **Practicality**: Is the allocation implementable and sustainable?
""")

st.header("🚀 Getting Started")

st.info("""
**Ready to begin?** 

1. Review the **FAQ** page if you need to refresh your understanding of insurance pricing
2. Go to the **Dashboard** page to start your analysis
3. Use the data and tools provided to make informed allocation decisions
4. Don't hesitate to experiment with different allocation strategies!

**Good luck with your strategic pricing decisions!** 🎯
""")

st.markdown("---")
st.markdown("*Remember: There's no single 'correct' answer. The goal is to make well-reasoned, data-driven decisions that balance multiple objectives.*")

