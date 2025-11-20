# FAIR Analysis Tools - Comparison Guide

You now have TWO ways to run FAIR Monte Carlo simulations. Here's when to use each:

## 📊 Quick Comparison

| Feature | Command-Line Script | Interactive Dashboard |
|---------|-------------------|---------------------|
| **Launch** | `python3 fair_monte_carlo.py` | `streamlit run fair_dashboard.py` |
| **Interface** | Terminal/console | Web browser |
| **Best For** | Automation, batch processing | Client presentations, exploration |
| **Interactivity** | Edit code, re-run | Live sliders and inputs |
| **Visualization** | Static PNG files | Interactive Plotly charts |
| **Learning Curve** | Need Python knowledge | Point and click |
| **Speed** | Fast | Slightly slower (web interface) |
| **Exports** | PNG, CSV, JSON | PNG (screenshot), CSV, JSON, TXT report |
| **Customization** | Full code control | Limited to UI options |
| **Client Friendly** | No (technical) | Yes (very intuitive) |

## 🎯 When to Use Command-Line Script

### ✅ Best For:

1. **Automation & Batch Processing**
   ```python
   # Run 10 scenarios automatically
   for scenario in scenarios:
       sim = FAIRMonteCarloSimulation(10000)
       stats = sim.run_simulation(...)
       save_results(scenario, stats)
   ```

2. **Integration with Other Tools**
   - Import into Jupyter notebooks
   - Part of larger Python workflows
   - Scheduled/automated reporting

3. **Custom Analysis**
   - Need specific distributions not in UI
   - Complex calculations beyond FAIR
   - Research and methodology development

4. **Documentation & Version Control**
   - Code in Git for reproducibility
   - Peer review of methodology
   - Academic or compliance documentation

5. **High-Volume Processing**
   - Run 50,000+ simulations
   - Process multiple clients at once
   - Statistical validation studies

### 📝 Example Use Cases:

**Monthly Client Reports:**
```python
# run_monthly_reports.py
for client in active_clients:
    sim = create_simulation(client.parameters)
    stats = sim.run_simulation(...)
    generate_report(client, stats)
    email_to_client(client, report)
```

**Sensitivity Analysis:**
```python
# Test how changes in vulnerability affect ALE
for vuln in np.linspace(0.001, 0.05, 50):
    stats = sim.run_simulation(vuln_prob=vuln, ...)
    results.append((vuln, stats['ale_mean']))
```

**Integration Example:**
```python
# In your existing risk assessment tool
from fair_monte_carlo import FAIRMonteCarloSimulation

def calculate_ale_for_control(control_id):
    scenario = get_scenario_for_control(control_id)
    sim = FAIRMonteCarloSimulation(10000)
    stats = sim.run_simulation(**scenario)
    return stats['ale_mean']
```

---

## 🎨 When to Use Interactive Dashboard

### ✅ Best For:

1. **Client Meetings & Presentations**
   - Adjust parameters live during discussion
   - "What if we reduce clicks from 8% to 3%?" → instant answer
   - Professional, polished interface

2. **Executive Presentations**
   - Clean, visual interface
   - No code visible
   - Export charts for PowerPoint

3. **Training & Workshops**
   - Show FAIR methodology visually
   - Let participants experiment
   - Build intuition about risk

4. **Initial Client Discovery**
   - Quick baseline assessment
   - Explore different scenarios
   - Show value of your services

5. **Collaborative Analysis**
   - Client can see and understand inputs
   - Make decisions together
   - Build consensus around numbers

### 📝 Example Use Cases:

**vCISO Quarterly Review:**
- Launch dashboard before meeting
- Pre-load client's scenarios
- Walk through results together
- Adjust based on recent changes
- Export report for their records

**Budget Justification Meeting:**
- Show current risk (baseline)
- Live adjust for proposed controls
- Show ROSI calculation
- Compare multiple investment options
- Get buy-in with visual proof

**Board Presentation:**
- Clean, professional interface
- Focus on exceedance curve
- Show percentiles clearly
- Screenshot for board deck
- No technical jargon visible

**Client Training:**
- Show them how risk quantification works
- Let them adjust parameters
- Build understanding of methodology
- Demystify risk assessment

---

## 🔄 Combined Workflow (Recommended)

Use BOTH tools in your practice:

### Phase 1: Development (Command-Line)
```python
# Develop your methodology
# Test parameter ranges
# Validate against historical data
# Create client-specific presets
```

### Phase 2: Client Engagement (Dashboard)
```bash
# Use dashboard for meetings
streamlit run fair_dashboard.py
# Live exploration and adjustment
# Professional presentation
```

### Phase 3: Production (Command-Line)
```python
# Finalized parameters from dashboard session
# Run formal analysis
# Generate official reports
# Archive in version control
```

### Example Full Workflow:

**Week 1: Preparation (Command-Line)**
```python
# Test different parameter combinations
# Validate against client's historical incidents
# Create custom preset in dashboard code
```

**Week 2: Discovery Meeting (Dashboard)**
```bash
# Launch dashboard with client
# Walk through their scenarios
# Adjust based on their feedback
# Export initial assessment
```

**Week 3: Formal Analysis (Command-Line)**
```python
# Use agreed parameters from dashboard
# Run comprehensive simulations
# Generate detailed technical report
# Include in compliance documentation
```

**Week 4: Quarterly Review (Dashboard)**
```bash
# Review previous quarter's actuals
# Update parameters if needed
# Show trend over time
# Plan next quarter's priorities
```

---

## 🛠️ Technical Comparison

### Command-Line Script

**Pros:**
- ✅ Full Python power and flexibility
- ✅ Easy to version control
- ✅ Can integrate with any system
- ✅ Fast execution
- ✅ Scriptable and automatable
- ✅ Better for research

**Cons:**
- ❌ Requires Python knowledge
- ❌ Not client-friendly
- ❌ Need to edit code for changes
- ❌ Static visualizations
- ❌ Less intuitive for exploration

**Dependencies:**
```
numpy, pandas, matplotlib, scipy
```

### Interactive Dashboard

**Pros:**
- ✅ Beautiful, professional interface
- ✅ No coding required
- ✅ Interactive charts (zoom, pan, hover)
- ✅ Live parameter adjustment
- ✅ Client-ready
- ✅ Easy scenario comparison

**Cons:**
- ❌ Less flexible than code
- ❌ Requires browser
- ❌ Slightly slower
- ❌ Limited to UI features
- ❌ Need to keep Streamlit updated

**Dependencies:**
```
numpy, pandas, matplotlib, scipy, streamlit, plotly
```

---

## 💼 Recommended Setup

### Your Laptop
- Both tools installed
- Dashboard for client meetings
- Command-line for analysis work

### Development Machine
- Command-line for automation
- Git repository for scenarios
- Scheduled monthly reports

### Client Site / Tablet
- Dashboard deployed online
- Shared link for client access
- Or run locally on site

---

## 📚 Which Guide to Read?

**New to FAIR?**
→ Start with `FAIR_Monte_Carlo_Guide.md` (methodology)

**Want to run it quickly?**
→ Read `README.md` (basic command-line)

**Preparing for client meeting?**
→ Read `Dashboard_Quick_Start.md` (interactive)

**Need parameter values?**
→ Use `FAIR_Parameter_Reference.md` (benchmarks)

**Building custom scenario?**
→ Use `custom_scenario_template.py` (template)

---

## 🎓 Learning Path

### Beginner
1. Read the main guide to understand FAIR
2. Run `python3 fair_monte_carlo.py` (example)
3. Launch dashboard: `streamlit run fair_dashboard.py`
4. Play with presets to build intuition

### Intermediate
1. Use `custom_scenario_template.py` for real client
2. Reference parameter guide for values
3. Customize dashboard presets for your clients
4. Run both CLI and dashboard for same scenario

### Advanced
1. Create Python scripts for automation
2. Deploy dashboard online for clients
3. Integrate FAIR into your existing tools
4. Build custom reports and workflows

---

## 🚀 Quick Commands Reference

```bash
# Install everything
pip3 install -r requirements.txt

# Run example (command-line)
python3 fair_monte_carlo.py

# Run custom scenario (command-line)
python3 custom_scenario_template.py

# Launch interactive dashboard
streamlit run fair_dashboard.py

# Stop dashboard
# Press Ctrl+C in terminal
```

---

## 💡 Pro Tips

1. **Use dashboard for exploration**, command-line for production
2. **Screenshot dashboard results** for quick reports
3. **Export CSV from either tool** for Excel analysis
4. **Version control your Python scripts**, not dashboard sessions
5. **Keep presets synchronized** between both tools
6. **Use dashboard for demos**, command-line for automation
7. **Train clients on dashboard**, do your work in code

---

## 🎯 Decision Flowchart

```
Need to quantify cyber risk?
        |
        ├─ Client meeting? → Use DASHBOARD
        |   └─ Live discussion, visual, interactive
        |
        ├─ Batch processing? → Use COMMAND-LINE
        |   └─ Multiple scenarios, automation, integration
        |
        ├─ Board presentation? → Use DASHBOARD
        |   └─ Clean interface, export charts
        |
        ├─ Compliance doc? → Use COMMAND-LINE
        |   └─ Reproducible, version controlled
        |
        └─ Not sure? → Start with DASHBOARD
            └─ More intuitive, build understanding
```

---

## 🎉 Bottom Line

Both tools use the **exact same simulation engine** (fair_monte_carlo.py). The only difference is the interface:

- **Dashboard** = User-friendly wrapper for client work
- **Command-Line** = Direct access for technical work

Use whichever fits your current task!

Most consultants will use:
- **80% Dashboard** (client-facing work)
- **20% Command-Line** (internal analysis, automation)

---

**Questions?** Both tools are documented and ready to use. Start with the dashboard if you're new to this, then explore the command-line scripts when you need more power!
