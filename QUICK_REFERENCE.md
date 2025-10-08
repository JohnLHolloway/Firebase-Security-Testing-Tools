# Quick Reference Card

## 🚀 Quick Commands

### Start Master (Windows PC)
```bash
py master_server.py
```
Dashboard: http://localhost:5000

### Setup Worker (Raspberry Pi)
```bash
# One-time setup
./setup_worker.sh

# Start worker
python3 worker_daemon.py
```

### Test Locally
```bash
py test_worker.py
```

---

## 📁 Essential Files

| File | Purpose |
|------|---------|
| `stable_web_env.py` | Training environment (FIXED) |
| `train_fixed.py` | Training script |
| `master_server.py` | Master orchestrator |
| `worker_daemon.py` | Worker node |
| `evaluation_system.py` | Model evaluation |

---

## 🎯 Quick Start (15 min)

1. **Master**: `py master_server.py`
2. **Browser**: Open http://localhost:5000
3. **RPi**: Copy files, run `worker_daemon.py`
4. **Done**: Watch dashboard as training begins

---

## 🔧 Troubleshooting

### No workers appear
```bash
# On RPi, specify master IP:
python3 worker_daemon.py --master 192.168.1.XXX
```

### Check system status
```bash
curl http://localhost:5000/status
```

### Create new jobs
```bash
curl -X POST http://localhost:5000/create_test_jobs
```

---

## 📊 What to Expect

- **Setup time**: 15-30 min
- **Training speed**: ~1 FPS
- **100K steps**: ~28 hours
- **Target score**: 25,940 points
- **3 RPis**: 3x faster

---

## 🎮 Current Status

✅ **Environment**: Fixed & working
✅ **Master server**: Running
✅ **Worker system**: Ready
✅ **Documentation**: Complete
✅ **Git**: Pushed & synced

**Next**: Setup your RPi 5!

---

## 📚 Full Documentation

- `QUICK_START.md` - Detailed setup
- `DISTRIBUTED_TRAINING_ARCHITECTURE.md` - System design
- `RASPBERRY_PI_SETUP_GUIDE.md` - RPi specifics
- `SESSION_SUMMARY.md` - Complete overview
- `PROJECT_STRUCTURE.md` - File organization

---

## 🆘 Need Help?

1. Check `SESSION_SUMMARY.md`
2. Review `QUICK_START.md`
3. Test with `test_worker.py`
4. Check dashboard: http://localhost:5000

---

## 🎯 Success Checklist

- [ ] Master server running
- [ ] Dashboard accessible
- [ ] RPi setup complete
- [ ] Worker connected
- [ ] Jobs processing
- [ ] Models training
- [ ] Scores improving!
