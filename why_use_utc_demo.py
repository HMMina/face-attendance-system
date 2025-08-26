"""
DEMONSTRATION: Why Use UTC in Database vs Local Time
"""
import datetime

def demonstrate_utc_benefits():
    print("🌍 WHY USE UTC IN DATABASE?")
    print("=" * 60)
    
    print("📋 SCENARIO 1: Single Timezone (Vietnam Only)")
    print("-" * 50)
    
    # Simulate attendance at different times
    utc_times = [
        datetime.datetime(2025, 8, 26, 1, 0, 0),   # 01:00 UTC = 08:00 Vietnam
        datetime.datetime(2025, 8, 26, 8, 30, 0),  # 08:30 UTC = 15:30 Vietnam
        datetime.datetime(2025, 8, 26, 10, 0, 0),  # 10:00 UTC = 17:00 Vietnam
    ]
    
    print("✅ GOOD: Store UTC, Display Vietnam Time")
    for i, utc_time in enumerate(utc_times, 1):
        vietnam_time = utc_time + datetime.timedelta(hours=7)
        print(f"Record {i}: Store {utc_time} UTC → Display {vietnam_time.strftime('%H:%M Vietnam')}")
    
    print("\n❌ BAD: Store Vietnam Time Directly")
    for i, utc_time in enumerate(utc_times, 1):
        vietnam_time = utc_time + datetime.timedelta(hours=7)
        print(f"Record {i}: Store {vietnam_time} VN → Cannot convert to other timezones!")
    
    print("\n" + "="*60)
    print("📋 SCENARIO 2: Multiple Countries Expansion")
    print("-" * 50)
    
    base_utc = datetime.datetime(2025, 8, 26, 8, 0, 0)  # 08:00 UTC
    
    countries = [
        ("Vietnam", 7),
        ("Singapore", 8),
        ("Thailand", 7), 
        ("Philippines", 8),
        ("Japan", 9),
        ("India", 5.5),
        ("Australia", 10),
    ]
    
    print("✅ GOOD: UTC in Database → Easy Multi-Country Support")
    print(f"Database stores: {base_utc} UTC")
    print("Display times:")
    for country, offset in countries:
        local_time = base_utc + datetime.timedelta(hours=offset)
        print(f"  {country:12}: {local_time.strftime('%H:%M (%d/%m)')}")
    
    print("\n❌ BAD: Vietnam Time in Database → Complex Conversion")
    vietnam_time = base_utc + datetime.timedelta(hours=7)
    print(f"Database stores: {vietnam_time} Vietnam")
    print("To display in other countries, need complex conversion:")
    for country, offset in countries:
        if country != "Vietnam":
            # Need to convert: Vietnam time → UTC → Target timezone
            utc_equivalent = vietnam_time - datetime.timedelta(hours=7)  # Back to UTC
            target_time = utc_equivalent + datetime.timedelta(hours=offset)  # To target
            print(f"  {country:12}: {target_time.strftime('%H:%M')} (needs VN→UTC→{country} conversion)")
    
    print("\n" + "="*60)
    print("📋 SCENARIO 3: Server Location Independence")
    print("-" * 50)
    
    print("✅ GOOD: UTC Storage")
    print("  Server in Vietnam (UTC+7)  → Stores UTC → Always consistent")
    print("  Server in Singapore (UTC+8) → Stores UTC → Always consistent") 
    print("  Server in AWS US (UTC-5)   → Stores UTC → Always consistent")
    print("  Server moved anywhere      → No data migration needed")
    
    print("\n❌ BAD: Local Time Storage")
    print("  Server in Vietnam → Stores UTC+7 → User confused when server moves")
    print("  Server moved to US → All times wrong by 12+ hours")
    print("  Need database migration when server relocates")
    
    print("\n" + "="*60)
    print("📋 SCENARIO 4: Database Queries & Reports")
    print("-" * 50)
    
    print("✅ GOOD: UTC Storage")
    print("  Query: Get attendance between 00:00-23:59 Vietnam time")
    print("    SELECT * FROM attendance") 
    print("    WHERE timestamp >= '2025-08-26 17:00:00' UTC")  # 00:00 VN = 17:00 UTC
    print("      AND timestamp <  '2025-08-27 17:00:00' UTC")  # 00:00 VN next day
    print("    → Simple, fast, reliable")
    
    print("\n❌ BAD: Local Time Storage") 
    print("  Query: Get attendance for Vietnam day, but data in Vietnam time")
    print("    Hard to query other timezones")
    print("    Complex timezone conversions in SQL")
    print("    Performance issues with timezone functions")
    
    print("\n" + "="*60)
    print("📋 SCENARIO 5: API Consistency")
    print("-" * 50)
    
    sample_utc = datetime.datetime(2025, 8, 26, 10, 0, 0)
    
    print("✅ GOOD: UTC API Response")
    api_response = {
        "timestamp": sample_utc.isoformat(),  # UTC for API consistency
        "formatted_time": (sample_utc + datetime.timedelta(hours=7)).strftime("%H:%M - %d/%m/%Y"),  # Display format
        "timezone": "UTC+7"
    }
    print("  API Response:")
    for key, value in api_response.items():
        print(f"    {key}: {value}")
    print("  → Frontend knows how to handle UTC timestamps")
    print("  → Easy to add timezone selection in frontend")
    
    print("\n❌ BAD: Local Time API Response")
    local_response = {
        "timestamp": (sample_utc + datetime.timedelta(hours=7)).isoformat(),  # Vietnam time
        "formatted_time": (sample_utc + datetime.timedelta(hours=7)).strftime("%H:%M - %d/%m/%Y"),
    }
    print("  API Response:")
    for key, value in local_response.items():
        print(f"    {key}: {value}")
    print("  → Frontend doesn't know what timezone this is")
    print("  → Cannot support international users")
    
    print("\n" + "="*60)
    print("🎯 CONCLUSION: ALWAYS USE UTC IN DATABASE")
    print("="*60)
    
    benefits = [
        "🌍 Global compatibility from day one",
        "🔧 Simple timezone conversions", 
        "📊 Clean database queries",
        "🚀 Easy server relocation",
        "🔄 Consistent API responses",
        "⚡ Better database performance",
        "🛡️ No Daylight Saving Time issues",
        "📈 Future-proof architecture"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")
    
    print("\n💡 IMPLEMENTATION RULE:")
    print("  📥 INPUT: Convert user timezone → UTC → Store in DB")
    print("  📤 OUTPUT: Read UTC from DB → Convert to user timezone → Display")

if __name__ == "__main__":
    demonstrate_utc_benefits()
