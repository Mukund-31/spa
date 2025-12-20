# Quick Start - Interactive Fraud Detection Demo

## ✅ Prerequisites Complete
- Kafka is running ✓
- Topics created ✓
- All agents ready ✓

## 🚀 Run the Interactive Demo

```bash
python fraud_demo.py
```

## 📋 What You'll See

### Main Menu
```
Choose a scenario to test:

  1. Normal Transaction (₹500 grocery purchase)
  2. High Velocity Attack (12 rapid ₹10 txns + ₹2,000 final)
  3. Unusual Amount Spike (₹150 avg → ₹10,000 spike)
  4. View Results in Kafka UI
  5. Exit
```

## 🎯 Scenario Details

### Option 1: Normal Transaction
- **What**: Regular ₹500 grocery purchase
- **Expected**: LOW RISK → APPROVED ✅
- **Kafka Topic**: `legitimate-transactions`
- **Use Case**: Baseline normal behavior

### Option 2: High Velocity Attack
- **What**: 12 rapid ₹10 transactions + ₹2,000 final fraud
- **Pattern**: Card testing attack
- **Expected**: HIGH RISK → FRAUD DETECTED 🚨
- **Kafka Topic**: `fraud-alerts`
- **Streaming Context**: 
  - Velocity: 12 txns in ~2 minutes
  - Streaming Bonus: +20 points
- **Use Case**: Demonstrates velocity-based fraud detection

### Option 3: Unusual Amount Spike
- **What**: Customer avg ₹150 → ₹10,000 jewelry purchase
- **Pattern**: Account takeover or stolen card
- **Expected**: MEDIUM-HIGH RISK → REVIEW ⚠️
- **Kafka Topic**: `fraud-alerts` or `legitimate-transactions` (based on score)
- **Streaming Context**:
  - Amount Deviation: 6,567%
  - Streaming Bonus: +15 points
- **Use Case**: Demonstrates amount deviation detection

## 📊 View Results in Kafka UI

### Option 4: Kafka UI Instructions

1. **Open Browser**: http://localhost:8080
2. **Click**: "Topics" in left sidebar
3. **View Topics**:
   - `fraud-alerts` - High-risk detections
   - `legitimate-transactions` - Approved transactions
   - `transactions` - All raw transactions
4. **Expand Message**: See full 5-agent analysis

### What You'll See in Kafka UI
```json
{
  "transaction_id": "VELOCITY_FINAL",
  "final_score": 70.0,
  "decision": "FRAUD DETECTED",
  "agent_discussion": [
    {
      "agent": "BehaviorAnalyst",
      "analysis": {
        "score": 85,
        "key_findings": ["High velocity detected", "Automated behavior"]
      }
    },
    {
      "agent": "PatternDetector",
      "analysis": {
        "score": 85,
        "key_findings": ["Card testing pattern", "Progressive amounts"]
      }
    }
    // ... 3 more agents
  ]
}
```

## 🎬 Example Run

```
Choose a scenario to test:
Enter your choice (1-5): 2

⚡ SCENARIO 2: HIGH VELOCITY ATTACK (Card Testing)

Description:
  Attacker makes 12 rapid ₹10 transactions to test stolen card
  Then attempts ₹2,000 purchase
  Expected: HIGH RISK → FRAUD DETECTED

Simulating 12 rapid ₹10 transactions (card testing)...
  Transaction 1/12: ₹10.00 (testing card)
  Transaction 2/12: ₹10.00 (testing card)
  ...

Final attack transaction: ₹2,000

Analyzing final transaction with velocity context...

📊 PHASE 1: Parallel 5-Agent Analysis
🔴 BEHAVIOR ANALYST...
  Score: 85/100 | Confidence: 90%
  Finding: High velocity detected - automated behavior

🟢 PATTERN DETECTOR...
  Score: 85/100 | Confidence: 90%
  Finding: Classic card testing pattern

🔵 GEOGRAPHIC ANALYST...
  Score: 50/100 | Confidence: 70%

🟡 RISK ASSESSOR...
  Score: 70/100 | Confidence: 80%
  Finding: Velocity multiplier applied

🟣 TEMPORAL ANALYST...
  Score: 75/100 | Confidence: 85%
  Finding: Scripted timing detected

⚖️  PHASE 2: Weighted Voting Consensus
  Base Risk Score: 73.0%

🚀 PHASE 3: Streaming Intelligence Bonus
  Streaming Bonus: +20 points
    • High velocity (12 txns)
  Final Score: 93.0%

✅ Published to Kafka topic: fraud-alerts

⚖️  FINAL VERDICT: High Velocity Attack

🚨 Decision: FRAUD DETECTED
📊 Final Risk Score: 93.0%
🎯 Transaction ID: VELOCITY_FINAL

📈 Streaming Context Impact:
  Velocity: 12 txns in 2.0 min
  Amount Deviation: 19900%

✅ View this transaction in Kafka UI: http://localhost:8080
```

## 🔄 Running Multiple Scenarios

You can run all 3 scenarios in sequence:
1. Choose option 1 (Normal) - See baseline
2. Choose option 2 (Velocity) - See attack detection
3. Choose option 3 (Amount) - See spike detection
4. Choose option 4 - View all results in Kafka UI

## 💡 Tips

- **Rate Limits**: If you see "Unable to parse structured response", wait 1-2 minutes between scenarios
- **Kafka UI**: Keep it open in browser while running scenarios
- **Real-time**: Results appear in Kafka UI immediately after analysis
- **Agent Discussion**: Full conversation log available in Kafka messages

## 🎯 Success Criteria

After running all 3 scenarios, you should see:

✅ **Normal Transaction**: Score ~30-40% → APPROVED  
✅ **Velocity Attack**: Score 70-95% → FRAUD DETECTED  
✅ **Amount Spike**: Score 60-75% → REVIEW  

All with detailed 5-agent analysis and streaming context!

---

**Ready to start? Run:** `python fraud_demo.py`
