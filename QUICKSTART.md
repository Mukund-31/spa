# Quick Start Guide

## Prerequisites Check
- [ ] Docker Desktop installed and running
- [ ] Python 3.8+ installed
- [ ] Gemini API key obtained from https://makersuite.google.com/app/apikey

## Setup (5 minutes)

### 1. Configure API Key
Edit `.env` file and replace `your_gemini_api_key_here` with your actual Gemini API key:
```
GEMINI_API_KEY=AIza...your_actual_key_here
```

### 2. Start Kafka Infrastructure
```bash
docker-compose up -d
```

Wait 30 seconds for Kafka to fully start.

### 3. Install Python Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Running the System

### Option 1: Test Agents First (Recommended)
```bash
python test_agents.py
```
This will show you the 3 AI agents in action without needing Kafka.

### Option 2: Run Full System
```bash
python run.py
```
This starts the complete fraud detection pipeline.

### Option 3: Run Components Separately

**Terminal 1 - Setup:**
```bash
python kafka_admin.py
```

**Terminal 2 - Consumer:**
```bash
python consumer.py
```

**Terminal 3 - Producer:**
```bash
python producer.py
```

## Viewing Results

Open browser to: **http://localhost:8080**

Navigate to **Topics** and click on:
- `transactions` - See all incoming transactions
- `fraud-alerts` - See detected fraud cases
- `legitimate-transactions` - See approved transactions

## Stopping the System

Press `Ctrl+C` in the terminal, then:
```bash
docker-compose down
```

## Troubleshooting

**"Connection refused" error:**
- Make sure Docker containers are running: `docker-compose ps`
- Wait 30 seconds after starting Docker

**"API key not found" error:**
- Check that `.env` file exists and contains your API key
- Make sure there are no extra spaces in the API key

**"Module not found" error:**
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## What You'll See

### Console Output
- 🔴 Red: Risk Analyst's financial analysis
- 🟢 Green: Pattern Detective's behavioral analysis  
- 🔵 Blue: Decision Maker's final decision
- 🟡 Yellow: Decision summary

### Kafka UI
- Real-time message flow
- Complete transaction details
- Full agent discussion logs
- Processing statistics

## Next Steps

1. Watch the agents analyze transactions in real-time
2. Modify transaction generation in `producer.py`
3. Adjust fraud thresholds in `config.py`
4. Customize agent prompts in `agents/` directory

---

**Need help?** Check the full [README.md](README.md) for detailed documentation.
