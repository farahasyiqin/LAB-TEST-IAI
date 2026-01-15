import json
import operator
import streamlit as st
from typing import List, Dict, Any, Tuple

# 1) Logic Engine Helpers (as provided)
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

# 2) Define Rules based on Table 1
DEFAULT_AC_RULES: List[Dict[str, Any]] = [
    {
        "name": "Windows open → turn AC off",
        "priority": 100,
        "conditions": [["windows_open", "==", True]],
        "action": {"mode": "OFF", "fan": "LOW", "setpoint": "-", "reason": "Windows are open"}
    },
    {
        "name": "No one home → eco mode",
        "priority": 90,
        "conditions": [["occupancy", "==", "EMPTY"]],
        "action": {"mode": "ECO", "fan": "LOW", "setpoint": "27°C", "reason": "Home empty; save energy"}
    },
    {
        "name": "Too cold → turn off",
        "priority": 85,
        "conditions": [["temperature", "<=", 22]],
        "action": {"mode": "OFF", "fan": "LOW", "setpoint": "-", "reason": "Already cold"}
    },
    {
        "name": "Hot & humid (occupied) → cool strong",
        "priority": 80,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">", 30],
            ["humidity", ">=", 70]
        ],
        "action": {"mode": "COOL", "fan": "HIGH", "setpoint": "23°C", "reason": "Hot and humid"}
    },
    {
        "name": "Night (occupied) → sleep mode",
        "priority": 75,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["time_of_day", "==", "NIGHT"],
            ["temperature", ">=", 26]
        ],
        "action": {"mode": "SLEEP", "fan": "LOW", "setpoint": "26°C", "reason": "Night comfort"}
    },
    {
        "name": "Hot (occupied) → cool",
        "priority": 70,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 28]
        ],
        "action": {"mode": "COOL", "fan": "MEDIUM", "setpoint": "24°C", "reason": "Temperature high"}
    },
    {
        "name": "Slightly warm (occupied) → gentle cool",
        "priority": 60,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 26],
            ["temperature", "<", 28]
        ],
        "action": {"mode": "COOL", "fan": "LOW", "setpoint": "25°C", "reason": "Slightly warm"}
    }
]


def evaluate_condition(facts: Dict[str, Any], cond: List[Any]) -> bool:
    if len(cond) != 3: return False
    field, op, value = cond
    if field not in facts or op not in OPS: return False
    return OPS[op](facts[field], value)


def rule_matches(facts: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    return all(evaluate_condition(facts, c) for c in rule.get("conditions", []))


def run_rules(facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    fired = [r for r in rules if rule_matches(facts, r)]
    if not fired:
        return ({"mode": "IDLE", "fan": "LOW", "setpoint": "-", "reason": "No rule matched"}, [])
    fired_sorted = sorted(fired, key=lambda r: r.get("priority", 0), reverse=True)
    return fired_sorted[0].get("action"), fired_sorted


# 3) Streamlit UI [cite: 77]
st.title("Smart Home AC Controller (Rule-Based)")
st.caption("BSD3513 Laboratory Test 2025/2026")

with st.sidebar:
    st.header("Home Facts")
    temp = st.number_input("Temperature (°C)", value=22)
    hum = st.number_input("Humidity (%)", value=46)
    occ = st.selectbox("Occupancy", ["OCCUPIED", "EMPTY"], index=0)
    tod = st.selectbox("Time of Day", ["MORNING", "AFTERNOON", "EVENING", "NIGHT"], index=3)
    win = st.checkbox("Windows Open", value=False)

facts = {
    "temperature": temp,
    "humidity": hum,
    "occupancy": occ,
    "time_of_day": tod,
    "windows_open": win
}

if st.button("Evaluate AC Settings", type="primary"):
    action, fired = run_rules(facts, DEFAULT_AC_RULES)

    st.subheader("System Result")
    st.info(f"**AC Mode:** {action['mode']} | **Fan:** {action['fan']} | **Setpoint:** {action['setpoint']}")
    st.write(f"**Primary Reason:** {action['reason']}")

    with st.expander("Show Matched Rules (Sorted by Priority)"):
        for r in fired:
            st.write(f"- {r['name']} (Priority: {r['priority']})")