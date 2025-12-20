# Kafka Streaming Fraud Detection with AI Agents

A real-time fraud detection system powered by **3 collaborative AI agents** using Google's Gemini API, Kafka streaming, and Kafka UI for visualization.

## 🎯 Features

- **Multi-Agent AI System**: Three specialized agents collaborate on fraud detection
  - 🔴 **Risk Analyst**: Financial risk assessment expert
  - 🟢 **Pattern Detective**: Behavioral pattern recognition specialist
  - 🔵 **Decision Maker**: Final decision synthesizer
- **Real-time Streaming**: Kafka-based transaction processing
- **Intelligent Analysis**: AI-powered fraud detection with detailed reasoning
- **Visual Dashboard**: Kafka UI for monitoring transactions and decisions
- **Realistic Data**: Automated generation of legitimate and suspicious transactions

## 🏗️ Architecture

```
Transaction Generator → Kafka (transactions) → Consumer → Multi-Agent AI
                                                              ↓
                                                    ┌─────────┴─────────┐
                                                    ↓                   ↓
                                          fraud-alerts      legitimate-transactions
                                                    ↓                   ↓
                                                    └─────────┬─────────┘
                                                              ↓
                                                         Kafka UI
```

## 📋 Prerequisites

- **Docker Desktop**: For running Kafka ecosystem
- **Python 3.8+**: For the application
- **Gemini API Key**: Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Mukund-31/spa.git
cd spa
```

### 2. Run Setup Script (Windows)

For quick setup, run the automated setup script:

```bash
setup.bat
```

This will:
- Create a virtual environment
- Install all Python dependencies
- Create `.env` file from template

**OR** follow the manual setup steps below:

### 3. Configure Environment

Create a `.env` file from the template:

```bash
copy .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Start Kafka Infrastructure

```bash
docker-compose up -d
```

Verify containers are running:

```bash
docker-compose ps
```

You should see `zookeeper`, `kafka`, and `kafka-ui` all in "Up" state.

### 5. Install Python Dependencies (Manual Setup Only)

If you didn't run `setup.bat`, install dependencies manually:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 6. Run the System

**Option A: Run everything together**

```bash
python run.py
```

**Option B: Run components separately**

Terminal 1 - Setup Kafka topics:
```bash
python kafka_admin.py
```

Terminal 2 - Start consumer:
```bash
python consumer.py
```

Terminal 3 - Start producer:
```bash
python producer.py
```

### 7. View Results in Kafka UI

Open your browser to: **http://localhost:8080**

Navigate to:
- **Topics** → View all three topics
- **transactions** → See incoming transactions
- **fraud-alerts** → See detected fraud cases
- **legitimate-transactions** → See approved transactions

## 🧪 Testing

Test the multi-agent system with sample transactions:

```bash
python test_agents.py
```

This will run three test cases:
1. **Suspicious transaction**: Large wire transfer to high-risk location
2. **Legitimate transaction**: Normal grocery purchase
3. **Medium risk transaction**: Electronics purchase from China

You'll see the complete agent discussion and decision-making process in color-coded output.

## 📊 How It Works

### Multi-Agent Collaboration

1. **Risk Analyst** analyzes the transaction first:
   - Evaluates transaction amount
   - Assesses merchant category risk
   - Checks geographic risk factors
   - Provides financial risk score (0-100)

2. **Pattern Detective** performs behavioral analysis:
   - Detects timing anomalies
   - Identifies velocity patterns
   - Spots location inconsistencies
   - Provides behavioral risk score (0-100)

3. **Decision Maker** synthesizes findings:
   - Reviews both agents' analyses
   - Weighs all evidence
   - Makes final decision (APPROVE/REVIEW/REJECT)
   - Provides comprehensive reasoning

### Decision Routing

- **Score 0-40**: APPROVE → `legitimate-transactions` topic
- **Score 41-70**: REVIEW → `legitimate-transactions` topic (flagged for review)
- **Score 71-100**: REJECT → `fraud-alerts` topic

## 🎨 Console Output

The system provides rich, color-coded console output:

- 🔴 **Red**: Risk Analyst analysis
- 🟢 **Green**: Pattern Detective analysis
- 🔵 **Blue**: Decision Maker synthesis
- 🟡 **Yellow**: Final decision summary
- 📊 **Statistics**: Periodic processing stats

## 📁 Project Structure

```
spa/
├── agents/
│   ├── base_agent.py          # Base agent class
│   ├── risk_analyst.py        # Financial risk agent
│   ├── pattern_detective.py   # Behavioral pattern agent
│   └── decision_maker.py      # Final decision agent
├── agent_coordinator.py       # Multi-agent orchestration
├── config.py                  # Configuration management
├── models.py                  # Data models
├── producer.py                # Transaction generator
├── consumer.py                # Fraud detection consumer
├── kafka_admin.py             # Kafka topic management
├── test_agents.py             # Agent testing script
├── run.py                     # Main orchestration
├── docker-compose.yml         # Kafka infrastructure
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables
```

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# Transaction generation rate (per second)
TRANSACTION_RATE=2

# Percentage of suspicious transactions (0.1 = 10%)
SUSPICIOUS_TRANSACTION_RATIO=0.1

# Kafka connection
KAFKA_BOOTSTRAP_SERVERS=localhost:9093
```

## 🐛 Troubleshooting

### Kafka Connection Issues

```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs kafka

# Restart containers
docker-compose restart
```

### Python Errors

```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API Key Issues

- Verify your Gemini API key is correct in `.env`
- Check API quota at [Google AI Studio](https://makersuite.google.com/)

## 📈 Monitoring

### Kafka UI (http://localhost:8080)

- **Topics**: View all topics and their messages
- **Consumers**: Monitor consumer groups and lag
- **Brokers**: Check Kafka broker health

### Console Output

- Real-time agent discussions
- Processing statistics every 10 transactions
- Color-coded decision summaries

## 🛑 Stopping the System

Press `Ctrl+C` in the terminal running the system.

To stop Docker containers:

```bash
docker-compose down
```

## 🎓 Learn More

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Google Gemini API](https://ai.google.dev/)
- [Kafka UI](https://github.com/provectus/kafka-ui)

## 📝 License

This project is for educational and demonstration purposes.

---

**Built with ❤️ using Kafka, Gemini AI, and Python**
