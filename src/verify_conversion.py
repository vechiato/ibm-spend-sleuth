#!/usr/bin/env python3
"""
Currency Conversion Verification

Quick script to verify that BRL to USD conversion is working correctly.
"""

try:
    from .ibm_billing_parser import IBMBillingParser
except ImportError:
    from ibm_billing_parser import IBMBillingParser

def verify_conversion():
    """Verify that currency conversion is working properly."""
    
    print("🔍 Verifying Currency Conversion (BRL to USD)")
    print("="*50)
    
    # Test with USD conversion (default)
    parser_usd = IBMBillingParser(".", convert_to_usd=True, exchange_rate=5.55)
    data_usd = parser_usd.load_all_data()
    
    if data_usd.empty:
        print("No data found!")
        return
    
    total_usd = data_usd['Cost'].sum()
    
    # Test without conversion (BRL)
    parser_brl = IBMBillingParser(".", convert_to_usd=False)
    data_brl = parser_brl.load_all_data()
    total_brl = data_brl['Cost'].sum()
    
    print(f"Total Cost in BRL: {total_brl:,.2f}")
    print(f"Total Cost in USD: {total_usd:,.2f}")
    print(f"Exchange Rate: 5.55")
    print(f"Manual Calculation: {total_brl / 5.55:,.2f} USD")
    print(f"Conversion Accurate: {'✅ Yes' if abs(total_usd - (total_brl / 5.55)) < 0.01 else '❌ No'}")
    
    # Test Oracle instances specifically
    print(f"\n🔍 Oracle Instances (DRW4ORAPROD01, DRW4ORAPROD02)")
    print("-" * 50)
    
    filters = {'Instance Name': ['DRW4ORAPROD01', 'DRW4ORAPROD02']}
    
    oracle_usd = parser_usd.get_filtered_analysis(filters)
    oracle_brl = parser_brl.get_filtered_analysis(filters)
    
    print(f"Oracle Total in BRL: {oracle_brl['total_cost']:,.2f}")
    print(f"Oracle Total in USD: {oracle_usd['total_cost']:,.2f}")
    print(f"Manual Calculation: {oracle_brl['total_cost'] / 5.55:,.2f} USD")
    print(f"Oracle Conversion Accurate: {'✅ Yes' if abs(oracle_usd['total_cost'] - (oracle_brl['total_cost'] / 5.55)) < 0.01 else '❌ No'}")
    
    if not oracle_usd['monthly_costs'].empty:
        print(f"\nMonthly Oracle Costs in USD:")
        for _, row in oracle_usd['monthly_costs'].iterrows():
            print(f"  {row['Billing Month']}: {row['Total Cost']:,.2f} USD")

if __name__ == "__main__":
    verify_conversion()