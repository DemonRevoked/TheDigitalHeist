# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Build and Start
```bash
docker-compose up --build
```

### 2. Verify It's Running
```bash
curl http://localhost:5000/health
```

### 3. Test the API
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"features": [0.1, -0.2, 0.3, 0.4, -0.5, 0.6, -0.7, 0.8, -0.9, 1.0, -1.1, 1.2, -1.3, 1.4, -1.5, 1.6, -1.7, 1.8, -1.9, 2.0]}'
```

## 🎯 Your Mission

1. **Extract the model** by probing the `/analyze` endpoint
2. **Find the hidden trigger** for the VAULT-ACCESS class
3. **Submit your findings** to `/report` for bonus points

## 📚 Resources

- `sample_data.json` - Example input format
- `hint.txt` - The Professor's hint
- `example_attack.py` - Reference attack script
- `README.md` - Full documentation

## 🛠️ Using Make (Optional)

```bash
make build    # Build containers
make up       # Start challenge
make verify   # Verify it works
make logs     # View logs
make down     # Stop challenge
```

## 🐛 Troubleshooting

**Port 5000 already in use?**
Edit `docker-compose.yml` and change the port mapping.

**Container won't start?**
```bash
docker-compose down
docker-compose up --build --force-recreate
```

Good luck, agent! 🕵️

